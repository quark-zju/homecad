"""
Holder for digital wall clock

Fits 3M command strip medium size.

https://www.amazon.com/dp/B0D69MLXGT
"""

from cqutils import *


WIDTH = 63 / 4
HEIGHT = 46


def render():
    c1z = 3
    c1r = 9 / 2
    c1 = W().cylinder(c1z, c1r)
    c2z = 7
    c2 = W().cylinder(c2z, c1r).align(c1, "<Z")
    c3r = 4.5 / 2
    # c3 = W().cylinder(7 - c1z, 4.5 / 2).align(c1, ":>Z")
    b2 = W().box(c1r * 2, c3r * 2, c2z).align(c1, "<Z")
    b2c = b2.intersect(c2)
    distance = 21.85 * 10
    b1 = W().box(HEIGHT, WIDTH, 2)  # 3m command strip
    o1 = (
        c1.union(b2c)
        .rotate_axis("Y", 180)
        .align(b1, ":>Z", dx=-(HEIGHT / 2 - c1r - 6))
        .union(b1)
    )
    o2 = o1.translate((0, distance, 0))
    b2 = W().box(10, distance, 2).align(o1, "<Z <X :>Y")
    b2a = b2.align(o1, ">X")
    b1a = b1.translate((0, distance / 2, 0))
    obj = o1.union(o2).union(b2).union(b2a).union(b1a)
    return obj


render().show().export()
