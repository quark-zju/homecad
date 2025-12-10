"""
Hook for calendar (with a r=2.5mm hole)

Fits 3M command strip medium size.
"""

from cqutils import *


WIDTH = 63 / 4
HEIGHT = 46


def render():
    c1r = 5 / 2
    c1z = 4
    hole_d = 2
    hole_z = 3
    c1 = (
        W()
        .cylinder(c1z, c1r)
        .faces("<Z")
        .chamfer(2, 0.5)
        .faces(">Z")
        .hole(hole_d, hole_z)
    )
    thick = 1.2
    b1 = W().box(WIDTH, HEIGHT, thick).align(c1, ":<Z", dy=-HEIGHT / 2 + c1r * 1.5)
    obj1 = c1.union(b1)

    c2 = W().cylinder(hole_z - 0.4, hole_d / 2 - 0.1).faces(">Z").chamfer(0.4)
    c3 = W().cylinder(thick, c1r + 1.4).align(c2, ":<Z")
    obj2 = c2.union(c3)

    obj = obj1.union(obj2.align(obj1, "<Z", dy=10))

    return obj


render().show().export()
