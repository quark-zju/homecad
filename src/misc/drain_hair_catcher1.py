"""Preview: b4dcad preview src/misc/drain_hair_catcher1.py"""

from math import cos, pi, sin

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
    slot_width=1.4,
    top=0,
    thick=1.2,
    d1=3,
    cap_slot_length=10,
    cap_slot_width=2.5,
    cap_slots_per_ring=0,
    outer_slot_width=None,
    rim_chamfer=2,
):
    if not 0 <= rim_chamfer < min(w1, r1 - r2):
        raise ValueError("Rim chamfer must fit within the height and annular wall")
    # Keep the original centered Z range and maximum diameter. A conical
    # envelope replaces the upper outside corner with a 45-degree chamfer.
    c1 = cylinder(h=w1, r=r1, center=True, fn=720)
    if rim_chamfer:
        lower = cylinder(h=w1 - rim_chamfer, r=r1, fn=720).move(z=-w1 / 2)
        bevel = cylinder(h=rim_chamfer, r=r1, r2=r1 - rim_chamfer, fn=720).move(
            z=w1 / 2 - rim_chamfer
        )
        c1 = lower + bevel
    slot_length = (r1 - r2) / 2 + slot_width * 2
    pos_inner = r2 + (r1 - r2) / 4
    pos_outer = r2 + (r1 - r2) * 3 / 4
    if outer_slot_width is None:
        # Match nominal tooth thickness at the two slot-center radii.
        # Project adjacent-center spacing onto the normal of the 45-degree
        # slots. Rounded ends and rotated neighbors prevent exact uniformity.
        outer_slot_width = slot_width + (
            2 * (pos_outer - pos_inner) * sin(pi / n) * cos(pi / 4)
        )
    pair = slot(slot_length, slot_width).rotate(45).move(x=pos_inner)
    pair += slot(slot_length + d1, outer_slot_width).rotate(-45).move(x=pos_outer)
    grooves = pair
    for i in range(1, n):
        grooves += pair.rotate(360.0 * i / n)
    # Union the repeated profiles in 2D before doing the solid subtraction.
    g1 = grooves.extrude(w1 - thick * (1 if top else 2))
    obj = c1 - g1.align_to(c1, ">Z", dz=0 if top else -thick)
    # `top` is the cap thickness, independent of the groove floor `thick`.
    c2 = cylinder(h=w1, r=r2, center=True, fn=720)
    obj -= c2.move(z=-top)
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
        slot_width=2,
        d1=1.8,
        cap_slots_per_ring=12,
    )


obj = render()
