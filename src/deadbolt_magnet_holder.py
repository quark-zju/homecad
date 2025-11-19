"""Deadbolt sensor - Magnet holder

Similar to [this "Invisible Zigbee Deadbolt Sensor" project](https://www.instructables.com/Invisible-Zigbee-Deadbolt-Sensor/).

I use [10x5x2mm magnets](https://www.amazon.com/dp/B0B6PBXBVJ). This is the holder for the magnets. It fixes the magnet to the lock lock cylinder (5x5mm).
"""

import cadquery as cq
from cadquery import *
from functools import partial, reduce
import os


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


# deadbolt: 5mm x 5mm
# magnet: 1.7mm x 9.8mm x 4.7mm
# room: 7mm

m_w = 5.0
m_h = 2.0
m_t = 10.0

d_w = d_h = 5.2


w = Workplane()


def render(border=2.0):
    thick = m_t + border * 2

    b1 = w.box(d_w + border * 2, d_h + border * 2, thick)
    b1c = w.box(d_w, d_h, thick)
    b1 = b1.cut(b1c)

    b2 = w.box(m_w + border * 2, m_h + border * 2, thick)
    b2c = w.box(m_w, m_h, thick).translate((0, 0, border))
    b2 = b2.cut(b2c).translate((0, (d_h + m_h) / 2 + border, 0))

    obj = union_all([b1, b2])
    return obj


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)
