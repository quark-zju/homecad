"""Thinkpad X13 (Gen 4) thin stand

A small stand for the ThinkPad X13 (Gen 4) that sits under the cooling area to prevent uneven surfaces from blocking airflow.

Includes slots for [20 × 20 × 1 mm magnet tiles](https://www.amazon.com/dp/B0DBVHMRW5).
"""

import cadquery as cq
from cadquery import *
from functools import partial, reduce
import os


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


W = Workplane()


# rev 1: test with width = 40 and n = 3
# rev 2:
# - reduce z2 from "5 + z1" to "2.5 + z1"
# - reduce width and remove b1a, b1b for testing
# - reduce w9 from 22 to 20.4
# - o1e loft z1 * 2
# rev 3:
# - reduce z2 from "2.5 + z1" to "2 + z1"
# - use full width
# suggest:
# - 0.12mm per layer
def render():
    width = 140
    n = 16
    # width = 30
    # n = 3
    y1 = 30
    y2 = y1 + 43 + 3
    y3 = y2 + 4.1  # 4.6
    y4 = y3 + 16

    z9 = 1.2  # magnet tile thickness
    w9 = 20.4  # magnet tile width height
    z1 = 1
    z2 = 2 + z1
    # z4 = (z2 - z1) / y2 * y4

    def loft(z1, z2, y1, y2, c2=None):
        o = (
            Workplane("XZ")
            .workplane(offset=-y1)
            .rect(width, z1, centered=(True, False, False))
            .workplane(offset=-(y2 - y1))
        )
        if c2 is not None:
            o = o.center(0, c2)
        return o.rect(width, z2, centered=(True, False, False)).loft(combine=True)

    objs = []
    o1 = loft(z1, z2, 0, y2)
    o1b = loft(z1, z1, 0, y4).translate((0, 0, -z1))
    o1c = loft(z2, z2, y1, y2).translate((0, 0, z1))
    o1e = loft(z1 * 2, z1, y3, y4)
    o1f = o1.union(o1b).cut(o1c).union(o1e)

    b1 = W.box(w9, w9, z9 * 20, centered=(True, False, False)).translate((0, w9 / 4, 0))
    b1a = b1.translate((width / 2 - w9, 0, 0))
    b1b = b1.translate((-width / 2 + w9, 0, 0))
    bz = -z1
    b1all = union_all([b1, b1a, b1b]).translate((0, 0, bz))
    o3 = loft(z9 * 2, z9 * 2, 0, y3, c2=z2 - z1).translate((0, 0, bz))
    b2 = b1all.intersect(o3)

    slots = []
    x_pad = 2
    y_pad = 2
    w_step = (width - x_pad) / (n)
    w_slot = w_step - x_pad
    b_slot = W.box(
        w_slot, (y2 - y1) - y_pad, z1 * 20, centered=(True, False, True)
    ).translate((-(width - x_pad) / 2 + w_step / 2, y1, 0))
    b_slot2 = W.box(
        w_slot, (y4 - y3) - y_pad * 2, z1 * 20, centered=(True, False, True)
    ).translate((-(width - x_pad) / 2 + w_step / 2, y3 + y_pad, 0))
    for i in range(n):
        slots += [
            b_slot.translate((i * w_step, 0, 0)),
            b_slot2.translate((i * w_step, 0, 0)),
        ]
    obj_slot = union_all(slots)

    objs += [o1f.cut(b2).cut(obj_slot)]

    return union_all(objs)


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)
