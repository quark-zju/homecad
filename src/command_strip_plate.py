"""
Snap-on two-plate mounting system for Command Refill Strips

The back plate (the thiner one) is meant to be attached to a wall using [3M Command Refill Strips](https://www.amazon.com/dp/B073XR4X72).

The front plate (the thicker one) can be attached to objects that need to be mounted.

The two plates snap together to hold the object in place. When removal is needed, the front plate can be detached easily, exposing the pull tab of the Command strip.
"""

import cadquery as cq
from cqutils import *
import os
import math


# 4 medium-sized strips; modify as needed
WIDTH = 63
HEIGHT = 46
THICK = 2


def render():
    objs = []
    d = THICK - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_plate(w, h):
        return (
            W()
            .box(WIDTH + d2 * 2, HEIGHT + d2, THICK)
            .edges(">Z")
            .filter(lambda edge: edge.Center().y > -5)
            .chamfer(d, d2)
        )

    w, h = WIDTH + d2 * 2, HEIGHT + d2 * 2
    plate = get_plate(w, h)
    objs += [plate]

    edge = 4
    plate2 = W().box(WIDTH + edge * 2, HEIGHT + edge, THICK * 2)
    plate2 = align(plate2, plate, ">Z <Y")
    plate2 = plate2.cut(get_plate(w + 0.3, h + 0.3))
    plate2 = align(plate2, plate, "<Z")

    objs += [plate2.translate((0, h + 2, 0))]

    obj = union_all(objs)
    return obj


def preview_obj(obj):
    return rotate_axis(obj, "X", 180)


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)
