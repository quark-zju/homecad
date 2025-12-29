from cqutils import *


def render():
    w, h, z = 13, 3, 45
    t = 1
    b1 = W().box(w + t * 2, h + t * 2, z + t * 2)
    b1c = b1.cut_inner_box(">Z", t)
    r = 2
    b1c = b1c.faces("Z").hole(r)
    d1 = W().cylinder(b1.measure("Y"), r / 2).rotate_axis("X", 90)
    obj = b1c.cut(d1)
    b2 = W().box(w + t * 2, h + t * 2, t).align(b1, ":>Y <Z", dy=6)
    b2t = (
        W()
        .box(w - 0.2, h - 0.2, t * 2.6)
        .align(b2, ":>Z -Y -X")
        .edges("|Z or >Z")
        .fillet(0.8)
    )
    b2c = b2.union(b2t)
    obj = obj.union(b2c)
    return obj


render().show().export()
