"""Deadbolt sensor - Contact sensor holder

Similar to [this "Invisible Zigbee Deadbolt Sensor" project](https://www.instructables.com/Invisible-Zigbee-Deadbolt-Sensor/).

I use [a smaller Zigbee contact sensor](https://www.amazon.com/dp/B0FPX7874R). This is the holder for the contact sensor. In my case, there is no need for wiring or soldering. I only need to remove the shell of the device.
"""

import cadquery as cq
from cadquery import *
from functools import reduce
import os


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


# deadbolt: r = 27mm
# depth: 30 mm
# top room: 10mm

r = 27.0
depth = 30.0
top_room = 10.0

# device: 8mm x 21mm x 42mm

d_h = 21.0
d_w = 42.0
d_t = 8.0


w = Workplane()


def render(thickness=1.0):
    # --- 1. 定义参数 ---
    radius = r
    cut_y = -14.8

    # --- 2. 创建外部的实心形状 ---
    # 先创建一个完整的圆柱体
    outer_solid = cq.Workplane("XY").circle(radius).extrude(depth)

    # 创建一个足够大的“切割盒”，用来切掉圆柱的下半部分
    # 切割盒的上表面需要精确地在 y = -10 的位置
    # 为了确保完全切除，盒子要比圆宽，并且其中心位置需要计算好
    cutter_box = (
        cq.Workplane("XY")
        .box(
            radius * 2,  # 盒子宽度
            radius * 2,  # 盒子高度
            depth,  # 盒子深度，和 extrude 深度一致
        )
        .translate(
            (
                0,  # x 方向不移动
                cut_y,  # y 方向移动，使其上边缘在 y = -10
                depth / 2,  # z 方向移动，使其与 extrude 的物体对齐
            )
        )
    )

    # 从圆柱体上切掉下面部分，得到我们想要的外部轮廓
    outer_solid_cut = outer_solid.cut(cutter_box)

    # --- 3. 创建内部的、用于挖空的形状 ---
    # 内部形状的尺寸都需要向内收缩 1mm
    inner_radius = radius - thickness  # 半径减小1mm
    inner_cut_y = cut_y + thickness  # 切割线上移1mm

    # 用与上面完全相同的方法，只是使用 "inner_" 尺寸
    inner_solid = cq.Workplane("XY").circle(inner_radius).extrude(depth - thickness)
    inner_cutter_box = (
        cq.Workplane("XY")
        .box(radius * 2, radius * 2, depth)
        .translate((0, inner_cut_y, depth / 2))  # 使用 'inner_cut_y'
    )
    inner_solid = inner_solid.cut(inner_cutter_box)

    # --- 4. 布尔减法：用外部形状减去内部形状 ---
    # 这就是实现“挖空”或“1mm边框”的关键步骤
    c1 = outer_solid_cut.cut(inner_solid)

    lines = []
    for y_offset in [d_t]:
        line = w.box(r * 2, thickness, depth, centered=(True, False, False)).translate(
            (0, r + cut_y + d_t, 0)
        )
        line = line.intersect(outer_solid)
        lines.append(line)

    return union_all([c1] + lines)


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)

# SVG_OPTS = {"projectionDir": (0.5, 0.5, 0.5)}
