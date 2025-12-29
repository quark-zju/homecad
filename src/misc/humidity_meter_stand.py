"""
Desktop mount for Mini Humidity Meter (22.4 x 22.4 x 4.8mm)

https://www.amazon.com/dp/B0DQSKM97D
"""

from cqutils import *
import math


def render():
    width = height = 22.4 * 2 + 0.4
    height2 = 14.4 * 2
    depth = 4.8 * 2
    angle = 60
    angle_r = math.radians(angle)
    pad = 5
    pad_top = 10
    b1_depth = depth + pad / math.tan(angle_r)
    b1 = W().box(width, b1_depth, height)
    bevel_len = height + pad * 2
    b2 = (
        W()
        .rect(
            width + pad * 2,
            bevel_len * math.cos(angle_r) + pad_top,
            centered=(True, False),
        )
        .workplane(offset=bevel_len * math.sin(angle_r))
        .rect(width + pad * 2, pad_top, centered=(True, False))
        .loft(combine=True)
    )
    b3 = W().box(width - 6, 18, height - height2).align(b1, ">Z :<Y", dz=-3)
    b4 = W().box(pad, b1_depth, height - height2).align(b1, ">Z >Y :<X", dz=0)
    b4b = b4.align(b1, ":>X")
    u1 = b1.union(b3).union(b4).union(b4b)
    u1 = u1.rotate_axis("X", 90 - angle).align(b2, ">Y -Z")
    obj = b2.cut(u1)
    return obj


render().show().export()
