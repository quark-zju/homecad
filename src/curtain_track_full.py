"""
Corner connector for curtain tracks

The stock connector of the [curtain track](https://www.amazon.com/dp/B0BB1PS5NW) has a smaller radius (7cm) that is not smooth enough for automation (SwitchBot). I need a larger one.

Requires drilling and M2.5 screws to fix the connector to the metal tracks.
"""

import cadquery as cq
from cadquery import *
from functools import partial, reduce
import os


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


def center(obj, x=None, y=None, z=None):
    # 0: center, -1: edge, 1: edge
    bbox = obj.val().BoundingBox()
    x_offset = y_offset = z_offset = 0
    if x is not None:
        x_offset = -(bbox.xmax + bbox.xmin) / 2
        x_offset += x * (bbox.xmax - bbox.xmin)
    if y is not None:
        y_offset = -(bbox.ymax + bbox.ymin) / 2
        y_offset += y * (bbox.ymax - bbox.ymin)
    if z is not None:
        z_offset = -(bbox.zmax + bbox.zmin) / 2
        z_offset += z * (bbox.zmax - bbox.zmin)
    return obj.translate((x_offset, y_offset, z_offset))


W = Workplane()


def create_solid_quarter_ring(inner_radius, width, height):
    radius = inner_radius + width
    w = Workplane()
    box = w.center(radius / 2, radius / 2).box(radius, radius, height)
    outer = w.cylinder(height, radius)
    inner = w.cylinder(height, inner_radius)
    return outer.intersect(box).cut(inner)


def create_quarter_frame(
    radius,
    width,
    height,
    outer_width,
    outer_height,
    outer_bottom,
    wall_width,
    wall_height,
    thin,
    slot,
    slot_pad,
):
    outer_total_width = width + outer_width * 2
    outer_total_height = height + outer_height + outer_bottom
    bottom = wall_height + outer_bottom
    ring = partial(
        create_solid_quarter_ring, width=outer_total_width, height=outer_total_height
    )
    ring1 = ring(inner_radius=radius)
    inner_width = width - wall_width * 2
    ring2 = ring(
        inner_radius=radius + (outer_total_width - inner_width) / 2, width=inner_width
    )
    ring2t = ring2.translate((0, 0, bottom + thin))
    slot2 = slot - slot_pad * 2
    ring3 = ring(
        inner_radius=radius + outer_total_width / 2.0 - slot2 / 2.0, width=slot2
    )
    slot_pad_height = wall_height * 2 / 3
    ring4 = ring(
        inner_radius=radius + outer_total_width / 2.0 - slot / 2.0,
        height=outer_total_height,
        width=slot,
    ).translate((0, 0, outer_bottom + slot_pad_height))
    s = []
    n = 12
    for i in range(n):
        a = -90 / (n + 1) * (i + 1)
        s.append(
            W.box(
                wall_width + outer_width,
                width,
                outer_height,
                centered=(False, False, False),
            )
            .translate(
                (
                    0,
                    radius + outer_width / 2.0,
                    (outer_total_height) / 2.0 - outer_height,
                )
            )
            .rotate((0, 0, 0), (0, 0, 1), a)
        )
    return ring1.cut(ring2t).cut(ring3).cut(ring4).union(union_all(s))


def render():
    return connector_full()


# rev 1:
# - width increased from 20 to 20.4
# - wall_width increased from 1.5 to 1.6
# rev 2:
# - height increased from 18.8 to 20.0
# - wall_height increased from 1.7 to 1.8, back to 1.7
# - slot decreased from 7.0 to 6.6 (6.8 remasured metal)
# - add slot_pad
# - width increased from 20.4 to 20.6
# rev 3: fix too loose
# - Is it because "precise Z height?", measured 19.9, nope, typo
#   Other settings:
#   桥接流量: 0.9 - 好像下垂减轻了一些
#   熨烫类型: 顶面 - 内部的小顶面确实光滑了一些
#   精准 Z 高度: true
# - height decreased from 20.0 to 19.0
# - width decreased from 20.6 to 20.4
# - wall_height changed from 1.7 to 1.6
# 比较成功 - 宽度稍微宽了一点
# rev 4:
# - width change: 20.4 to 20.2
# - slot change: 6.6 to 6.7
# - 好像还不错，上下比较紧
# rev 5:
# - 增加螺丝孔
# - length 暂时下降，从 10 到 1
# - outer_length 暂时下降，从 20 到 10
# - 测试螺纹孔 - 还行，有点扁扁的，小件不用支撑
# - 中部使用树状支撑，看看效果 - 效果还行
# - 犯错：直径当成了半径...
# rev 6:
# - 完整版
# - 纠正孔半径
# - thin 额外高度 0.4 -> 0.2
# - 螺丝孔数: 1 -> 3
# - 使用树状支撑
def connector_full(
    length=5,
    outer_length=30,
    width=20.2,  # metal outer
    height=19.0,  # metal outer
    outer_width=2.0,
    outer_height=2.0,
    outer_bottom=1.0,  # plastic bottom
    wall_width=1.6,  # metal frame
    wall_height=1.6,  # metal frame (also slot height)
    thin=0.2,
    thin_end=1,
    thin_inner=False,
    slot=6.8,
    slot_pad=0.5,
    screw=3,
    radius=190.0,
):
    # outer box
    b1 = W.box(
        width + outer_width * 2,
        height + outer_height + outer_bottom,
        length + outer_length,
        centered=(True, True, False),
    ).translate((0, (outer_bottom - outer_height) / 2, 0))
    # regular box - match metal outer
    b2 = W.box(
        width,
        height,
        outer_length,
        centered=(True, True, False),
    ).translate((0, 0, length))
    # inner box - match metal inner, reserve thin, ignore top
    b3 = W.box(
        width - wall_width * 2,
        height - wall_height - thin,
        length,
        centered=(True, True, False),
    ).translate((0, -(wall_height + thin) / 2, 0))
    # slot
    bslot = W.box(
        slot, height / 2, length + outer_length, centered=(True, True, False)
    ).translate((0, height / 2, 0))
    objs = [b1.cut(b2).cut(b3).cut(bslot)]
    if slot_pad:
        slot_pad_height = wall_height * 2 / 3
        s1 = W.box(
            slot_pad,
            outer_bottom + slot_pad_height,
            length + outer_length,
            centered=(True, False, False),
        ).translate((0, height / 2 - slot_pad_height, 0))
        s2 = s1.translate((slot / 2 - slot_pad / 2, 0, 0))
        s3 = s1.translate((-(slot / 2 - slot_pad / 2), 0, 0))
        objs += [s2, s3]
    if screw:
        for i in range(screw):
            z = length + outer_length / (screw + 1) * (i + 1)
            c1 = (
                Workplane("YZ")
                .cylinder(width + (outer_width) * 2 + 2, 1.8 / 2)
                .translate((0, 0, z))
            )
            c2 = (
                Workplane("YZ")
                .cylinder(width + (outer_width) * 2 + 2, 4 / 2)
                .translate((0, 0, z))
            )
            c3 = Workplane("YZ").cylinder(width, 4 / 2).translate((0, 0, z))
            objs = [union_all(objs + [c2.cut(c3)]).cut(c1)]
    if thin_inner:
        # thin inner border
        lside_thin_end = 0.5
        lside_height = height / 5 - wall_height
        lside = (
            W.workplane(offset=0)
            .rect(thin, lside_height)
            .workplane(offset=outer_length + length)
            .center(0, lside_height / 2 - lside_thin_end / 2)
            .rect(thin, lside_thin_end)
            .loft(combine=True)
        )
        l1 = lside.translate(
            (
                width / 2 - thin / 2 - wall_width,
                height / 2 - wall_height - lside_height / 2,
                0,
            )
        )
        l2 = lside.translate(
            (
                -(width / 2 - thin / 2 - wall_width),
                height / 2 - wall_height - lside_height / 2,
                0,
            )
        )
        lbottom_width = (width - slot) / 2 - wall_width
        lbottom = (
            W.workplane(offset=length)
            .rect(lbottom_width, thin)
            .workplane(offset=outer_length)
            .center(lbottom_width / 2 - thin_end / 2, 0)
            .rect(thin_end, thin)
            .loft(combine=True)
        )
        l3 = lbottom.translate(
            (
                width / 2 - wall_width - lbottom_width / 2,
                height / 2 - wall_height - thin / 2,
                0,
            )
        )
        l4 = lbottom.rotate((0, 0, 0), (0, 0, 1), 180).translate(
            (
                -(width / 2 - wall_width - lbottom_width / 2),
                height / 2 - wall_height - thin / 2,
                0,
            )
        )
        objs += [l1, l2, l3, l4]
    c1 = center(
        union_all(objs)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .rotate((0, 0, 0), (0, 1, 0), 180),
        z=0,
    )
    c1a = c1.translate((radius + width / 2 + outer_width, 0, 0))
    objs = [c1a]
    if radius:
        objs.append(
            create_quarter_frame(
                radius,
                width,
                height,
                outer_width=outer_width,
                outer_height=outer_height,
                outer_bottom=outer_bottom,
                wall_width=wall_width,
                wall_height=wall_height,
                thin=thin,
                slot=slot,
                slot_pad=slot_pad,
            )
        )
        c1b = c1.rotate((0, 0, 0), (0, 0, 1), -90).translate(
            (0, radius + width / 2 + outer_width, 0)
        )
        objs.append(c1b)
    return union_all(objs)


def preview_obj(obj):
    return obj.rotate((0, 0, 0), (0, 1, 0), 180)


obj = render()
cq.exporters.export(obj, os.path.basename(__file__).split(".")[0] + ".stl")
show_object(obj)
