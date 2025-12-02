from cqutils import *
import math


# 4 medium-sized strips; modify as needed
WIDTH = 63 - 0.2 - 0.3
HEIGHT = 46
ROUND = 6
THICK = 2


def connect_obj(width, height, thick, kind="male", edge=2, seam=0.2):
    assert thick > 0.2
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_obj(w, h, dthick=0):
        return W().box(w, thick + dthick, h).edges("<Y").edges("|Z").chamfer(d, d2)

    b_inner = get_obj(width, height)
    outer_width = width + (edge - d2 / 2) * 2
    outer_height = height + edge
    unprintable = 0.01
    if kind in {1, "male"}:
        b_placeholder = (
            W()
            .box(outer_width, unprintable, unprintable)
            .align(b_inner, "<Z >Y", dz=outer_height - unprintable)
        )
        return b_inner.union(b_placeholder)

    b_outer = W().box(outer_width, thick + edge, outer_height)
    b_inner_for_cut = get_obj(width + seam * 2, height + seam, 0.2)
    if kind in {2, "cut"}:
        b_placeholder = (
            W()
            .box(outer_width, unprintable, unprintable)
            .align(b_inner_for_cut, "<Z >Y", dz=outer_height - unprintable)
        )
        return b_inner_for_cut.union(b_placeholder)
    b_outer = b_outer.cut(b_inner_for_cut.align(b_outer, "<Z <Y"))
    return b_outer


def render():
    o1 = connect_obj(10, 20, 2, "male")
    o2 = connect_obj(10, 20, 2, "female")
    o2 = o2.align(o1, "<Y >Z")
    return o1.union(o2.translate((0, 0, 0)))


render().export().show()
