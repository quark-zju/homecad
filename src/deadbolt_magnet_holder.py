"""Deadbolt sensor - Magnet holder

Similar to [this "Invisible Zigbee Deadbolt Sensor" project](https://www.instructables.com/Invisible-Zigbee-Deadbolt-Sensor/).

I use [10x5x2mm magnets](https://www.amazon.com/dp/B0B6PBXBVJ). This is the holder for the magnets. It fixes the magnet to the 5x5mm lock cylinder.
"""

from cqutils import *


# deadbolt: 5mm x 5mm
# magnet: 1.7mm x 9.8mm x 4.7mm
# room: 7mm

m_w = 5.0
m_h = 2.0
m_t = 10.0

d_w = d_h = 5.2


w = cq.Workplane()


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


render().export().show()
