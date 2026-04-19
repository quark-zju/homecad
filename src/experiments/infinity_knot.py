"""
Infinity Knot

This is the same shape as [Infinity Knot: Modern Display Art](https://makerworld.com/en/models/920049-infinity-knot-modern-display-art) by [Adam L](https://makerworld.com/en/@AdamL).

Attempt to split into parts without support. But it seems impossible to do so.
"""

from cqutils import *
from functools import partial


def render(size=20, pad=10):
    hb = hollow_box(size)

    cm = connect_obj(size - 6, size - 2, 5, placeholder=False)
    cm = cm.align(hb, "<Y <Z -X").union(hb)

    cf = connect_obj(size - 6, size - 2, 5, "cut", placeholder=False)
    cf = cf.align(hb, "<Y <Z -X").union(hb)

    n = [i * size + (i - 1) * pad for i in range(5)]
    p = [i * size + i * pad for i in range(5)]

    def l_shape(w, h, align=">Y <X"):
        b1 = W().box(size, n[w], size)
        b2 = W().box(n[h], size, size).align(b1, align)
        return b1.union(b2)

    l1 = l_shape(2, 3, ">Y <X")
    l2 = l_shape(4, 3, ">Y <X").align(l1, ":>Z >Y >X", dz=pad, dx=p[1], dy=p[1])
    l3 = l_shape(3, 2, "<Y >X").align(l2, ":>Z <Y <X", dz=pad)
    l4 = l_shape(3, 4, "<Y >X").align(l3, ":>Z, <Y <X", dz=pad, dx=-p[1], dy=p[1])

    def vbar(obj1, obj2):
        bb1 = obj1.bbox()
        bb2 = obj2.bbox()
        ax = "<X" if bb1.xmin == bb2.xmin else ">X"
        ay = "<Y" if bb1.ymin == bb2.ymin else ">Y"
        b = W().box(size, size, bb2.zmax - bb1.zmin)
        return b.align(obj1, f"<Z {ax} {ay}")

    def vbars(obj1):
        return vbar(obj1, l3).union(vbar(obj1, l4))

    def align2(obj1, obj2, face, rotate=0, **kwargs):
        hb1 = hb.align(obj2, face, **kwargs)
        return obj1.rotate_axis("Z", rotate).align(obj2, face, **kwargs).cut(hb1)

    cm_align = partial(align2, cm)
    cf_align = partial(align2, cf)

    b1 = vbars(l1)
    b1a = b1.cut(cf_align(b1, ">Z >Y >X", dz=-p[1]))
    b1a = b1a.cut(cf_align(b1, ">Z <Y <X", rotate=90))
    o1 = l1.union(b1a)

    sep = 30
    b2 = vbars(l2)
    b2a = b2.cut(cf_align(b2, ">Z >Y >X"))
    b2a = b2a.cut(cf_align(b2, ">Z <Y <X", rotate=90, dz=-p[1]))
    o2 = l2.union(b2a).align(dz=sep)

    l3a = l3.cut(b1).cut(b2)
    l3a = l3a.union(cm_align(l3a, ">Z :>Y >X"))
    l3a = l3a.union(cm_align(l3a, ">Z <Y :<X", rotate=90))
    o3 = l3a.align(dz=sep * 2)

    l4a = l4.cut(b1).cut(b2)
    l4a = l4a.union(cm_align(l4a, ":>Y >X <Z"))
    l4a = l4a.union(cm_align(l4a, "<Y :<X <Z", rotate=90))
    o4 = l4a.align(dz=sep * 3)

    obj = union_all([o1, o2, o3, o4])

    return obj


render().show().export()
