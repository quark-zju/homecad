from cqutils import *


def get_obj(r1=70 / 2, r2=51.2 / 2, w1=17, n=40):
    c1 = W().cylinder(w1, r1)
    slot_width = 1.4
    slot_length = (r1 - r2) / 2 + slot_width * 2
    pos_inner = r2 + (r1 - r2) / 4
    pos_outer = r2 + (r1 - r2) * 3 / 4
    g1 = (
        W()
        .polarArray(pos_inner, startAngle=0, angle=360, count=n, rotate=True)
        .slot2D(slot_length, slot_width, angle=45)
        .polarArray(pos_outer, startAngle=0, angle=360, count=n, rotate=True)
        .slot2D(slot_length + 3, slot_width, angle=-45)
        .extrude(w1 - 1.2 * 2)
    )
    c1 = c1.faces(">Z").fillet(3)
    obj = c1.cut(g1.align(c1, ">Z", dz=-1.2))
    c2 = W().cylinder(w1, r2)
    obj = obj.cut(c2)
    return obj


def render():
    return get_obj()


obj = render().export().show()
