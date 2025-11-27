"""
Holder for rack edges

This is a holder that can attach to the edges of [racks like this](https://www.amazon.com/dp/B09W2Y51TC/).

It can be useful to stick something like a [Pico remote](https://www.amazon.com/Lutron-3-Button-Wireless-Lighting-PJ2-3BRL-WH-L01R/dp/B00KLAXFQ0) to the rack.
"""

import cadquery as cq
from cadquery import *
from functools import partial, reduce
import os


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


W = Workplane()


def render():
    # matches pico plate
    h = 36.5
    w = 26.8
    # matches rack edge
    d = 6.0
    dh = 21.0
    thick = 2.0
    b1 = W.box(w, h, d + thick * 2, centered=(True, False, True))
    b1c = W.box(w, dh + thick + (h - dh) / 2, d, centered=(True, False, True))
    b2 = W.box(w, thick, thick, centered=(True, False, True)).translate(
        (0, (h - dh) / 2, thick)
    )
    b3 = b2.translate((0, 0, -thick * 2))
    return union_all([b1.cut(b1c), b2, b3])


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)
