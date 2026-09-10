"""Preview: b4dcad preview src/misc/drain_hair_catcher1.py"""

from b4dcad import circle, cylinder


def slot(length, width):
    """Capsule with the same overall length and width as CadQuery slot2D."""
    end = circle(d=width, fn=24)
    offset = (length - width) / 2
    return end.move(x=-offset).hull(end.move(x=offset))


def get_obj(
    r1=70 / 2, r2=51.2 / 2, w1=17, n=40, slot_width=1.4, top=0, thick=1.2, d1=3
):
    # Keep the original centered Z range; omit the outer rim's 3 mm fillet.
    c1 = cylinder(h=w1, r=r1, center=True, fn=720)
    slot_length = (r1 - r2) / 2 + slot_width * 2
    pos_inner = r2 + (r1 - r2) / 4
    pos_outer = r2 + (r1 - r2) * 3 / 4
    pair = slot(slot_length, slot_width).rotate(45).move(x=pos_inner)
    pair += slot(slot_length + d1, slot_width).rotate(-45).move(x=pos_outer)
    grooves = pair
    for i in range(1, n):
        grooves += pair.rotate(360.0 * i / n)
    # Union the repeated profiles in 2D before doing the solid subtraction.
    g1 = grooves.extrude(w1 - thick * (1 if top else 2))
    obj = c1 - g1.align_to(c1, ">Z", dz=0 if top else -thick)
    # `top` is the cap thickness, independent of the groove floor `thick`.
    c2 = cylinder(h=w1, r=r2, center=True, fn=720)
    obj -= c2.move(z=-top)
    return obj


def render():
    return get_obj(
        r1=106 / 2.0, r2=86 / 2, w1=7, n=60, top=1, thick=1, slot_width=2, d1=1.8
    )


obj = render()
