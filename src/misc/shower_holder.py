import math
from cqutils import *

WIDTH = 63 / 4
HEIGHT = 46


def render(r1=23 / 2, r2=25 / 2, s1=16, h1=35):
    p1 = import_part("command_strip_plate.py", "flat2-female").rotate_axis("X", 90)
    p1a = p1.surface_grow(">Z", 6).edges("|Y and >Z").fillet(5)
    p1b = p1.surface_grow("<Z", 20)
    p1 = p1.union(p1a).union(p1b)
    obj = p1
    angle = 3
    h1 = h1 or p1.measure("Z")
    l1 = (
        W().circle(r1).workplane(offset=h1).circle(r2).loft(combine=True)
    ).rotate_axis("X", -angle)
    w1 = 10
    h2 = h1 - r2 * 2 * math.sin(math.radians(angle)) - 1
    l2 = (
        W()
        .polyline(
            [
                (-(r1 + w1), 0),
                (-(r1 + w1 / 2), r1 * 2 + w1),
                ((r1 + w1 / 2), r1 * 2 + w1),
                ((r1 + w1), 0),
            ]
        )
        .close()
        .workplane(offset=h2)
        .polyline(
            [
                (-(r2 + w1), 0),
                (-(r2 + w1 / 2), r2 * 2 + w1),
                ((r2 + w1 / 2), r2 * 2 + w1),
                ((r2 + w1), 0),
            ]
        )
        .close()
        .loft(combine=True)
    )
    l3 = l2.cut(l1.align(l2, "-X -Y -Z"))
    l3 = l3.align(p1, ":>Y <Z")
    b1 = W().box(s1, w1 + r1, h2)
    l3 = l3.cut(b1.align(l3, ">Y >Z -X"))
    l3 = l3.edges("not <Y or <Z").fillet(1.6)  # slow, comment out when iterating
    obj = obj.union(l3)
    return obj


render().show().export()
