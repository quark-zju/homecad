"""Preview: b4dcad preview src/misc/drain_hair_catcher1.py"""

from b4dcad import circle, cylinder


def slot(length, width):
    """Capsule with the same overall length and width as CadQuery slot2D."""
    end = circle(d=width, fn=24)
    offset = (length - width) / 2
    return end.move(x=-offset).hull(end.move(x=offset))


def get_obj(
    r1=70 / 2,
    r2=51.2 / 2,
    w1=17,
    n=40,
    post_diameter=2.5,
    top=0,
    thick=1.2,
    cap_slot_length=10,
    cap_slot_width=2.5,
    cap_slots_per_ring=0,
):
    if not 0 < r2 < r1 or not 0 < post_diameter < (r1 - r2) / 2:
        raise ValueError("Posts must fit within the annular wall")
    if not 0 < thick < w1 or not 0 <= top < w1 - thick:
        raise ValueError("Floor and cap must leave space for water between them")
    if not isinstance(n, int) or n < 3:
        raise ValueError("Each ring needs at least three posts")

    # Preserve the original outer diameter, bore and centered Z range.
    ring = circle(r=r1, fn=720) - circle(r=r2, fn=720)
    obj = ring.extrude(thick).move(z=-w1 / 2)
    post = circle(d=post_diameter, fn=32)
    # Tiny insets avoid tangent mesh edges at the circular ring boundaries.
    posts = None
    for radius, phase in (
        (r2 + post_diameter / 2 + 0.02, 0),
        ((r1 + r2) / 2, 0.5),
        (r1 - post_diameter / 2 - 0.02, 0),
    ):
        radial_post = post.move(x=radius)
        for i in range(n):
            placed = radial_post.rotate(360.0 * (i + phase) / n)
            posts = placed if posts is None else posts + placed
    obj += posts.extrude(w1 - thick / 2).move(z=-w1 / 2 + thick / 2)
    if top > 0:
        # Cover the inner row to attach the cap, but leave the outer two rows
        # open from above. There is deliberately no upper connecting ring.
        obj += cylinder(h=top, r=r2 + post_diameter + 0.04, fn=720).move(z=w1 / 2 - top)
    if top > 0 and cap_slots_per_ring > 0:
        # Two staggered rings of radial slots, entirely over the inner cavity.
        # Set cap_slots_per_ring=0 to compare with the original closed cap.
        if not 0 < cap_slot_width <= cap_slot_length < r2 / 2:
            raise ValueError("Cap slots must satisfy 0 < width <= length < r2 / 2")
        opening = slot(cap_slot_length, cap_slot_width)
        openings = None
        for radius, phase in ((r2 * 0.4, 0), (r2 * 0.75, 0.5)):
            radial_slot = opening.move(x=radius)
            for i in range(cap_slots_per_ring):
                cut = radial_slot.rotate(360.0 * (i + phase) / cap_slots_per_ring)
                openings = cut if openings is None else openings + cut
        # Overlap the cavity and top surface slightly to avoid coplanar cuts.
        obj -= openings.extrude(top + 0.2).move(z=w1 / 2 - top - 0.1)
    return obj


def render():
    return get_obj(
        r1=106 / 2.0,
        r2=86 / 2,
        w1=7,
        n=60,
        top=1,
        thick=1,
        post_diameter=2.5,
        cap_slots_per_ring=12,
    )


obj = render()
