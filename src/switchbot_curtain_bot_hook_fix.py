"""
Switchbot curtain bot fixer

Lock the locations of the [W-shaped curtain hooks](https://www.amazon.com/dp/B096ZXQ6PD) around the [Switchbot curtain bot (U-rail)](https://www.amazon.com/SwitchBot-Automatic-Curtain-Opener-High-Performance/dp/B0C6XZYFS7) so the bot less likely runs into the hook and gets stuck.
"""

from cqutils import *


W = cq.Workplane()


def render():
    thick = 2
    thick_z = 6
    x1 = 1.5 + thick / 2
    slot_size = 24
    y0 = 25
    # y1 = 40
    y2 = 40
    width = y2 + slot_size
    y2a = width - slot_size / 3
    y2b = width - slot_size * 2 / 3
    x2 = 29
    pts = [
        (-x2, 0),
        (-x2, y0),
        (-x1, y2),
        (-x1, width),
        (x1, width),
        (x1, y2a),
        (thick / 4 - x1, y2a),
        (thick / 4 - x1, y2b),
        (x1, y2b),
        (x1, y2),
        (x2, y0),
        (x2, 0),
    ]
    l1 = W.polyline(pts).offset2D(thick / 2).extrude(thick_z)
    pts = [
        (-x1, y2),
        (x1, y2),
        (x1, (y2b + y2a) / 2 - 1),
    ]
    l2 = W.polyline(pts).offset2D(thick / 2).extrude(thick_z)
    objs = [l1, l2]
    obj = union_all(objs)
    return obj.mirror("XZ").union(obj)


render().export().show()
