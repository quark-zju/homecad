from cqutils import *


@cq_cache
def get_obj(
    r1=70 / 2, r2=51.2 / 2, w1=17, n=40, slot_width=1.4, top=0, thick=1.2, d1=3
):
    c1 = W().cylinder(w1, r1)
    slot_length = (r1 - r2) / 2 + slot_width * 2
    pos_inner = r2 + (r1 - r2) / 4
    pos_outer = r2 + (r1 - r2) * 3 / 4
    g1 = (
        W()
        .polarArray(pos_inner, startAngle=0, angle=360, count=n, rotate=True)
        .slot2D(slot_length, slot_width, angle=45)
        .polarArray(pos_outer, startAngle=0, angle=360, count=n, rotate=True)
        .slot2D(slot_length + d1, slot_width, angle=-45)
        .extrude(w1 - thick * (top and 1 or 2))
    )
    c1 = c1.faces(">Z").fillet(3)
    obj = c1.cut(g1.align(c1, ">Z", dz=(0 if top else -thick)))
    c2 = W().cylinder(w1, r2)
    obj = obj.cut(c2.align(c1, ">Z", dz=-top))
    return obj


def render():
    o1 = get_obj().export("a")
    o2 = get_obj(
        r1=106 / 2.0, r2=86 / 2, w1=7, n=60, top=1, thick=1, slot_width=2, d1=1.8
    ).export("b")
    o1.show()
    obj = o1.union(o2.align(o1, ":>X", dx=10))
    return obj


obj = render().export().show()
