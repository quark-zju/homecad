"""双段回形针轴铰链与磁铁适配试片，单位 mm。

left_leaf / right_leaf 各打印一件，平底朝下；两个同轴连接点各用一段
0.8 裸金属芯，目标轴长 16。两件先对齐，再从中间向两端插轴到盲孔底，
确认能转动后，仅在左件朝中间的两个凹口点少量稠胶封口固定轴。
凹口深 1、直径 2.2；16 长的轴端缩入凹口 0.5，无需另装顶盖或固定件。
胶不得流入两件的 0.3 轴向接缝；先干装，胶固化后再转动。
中央净空为轴长加 2，供两段直轴先后插入；外端盲孔各保留 0.8 塑料。
试片铰链轴高 3，连接全长 52.6，板厚 1.2；不含实际卡槽和磁吸扣。
show_assembly 为翻开 70 度的预览，不导出。

0.4 喷嘴实测：原水平圆孔 1.0/1.1/1.2 切片有孔，但实物全部封住。
先只打印三个新 pin_gauge：horizontal 为水平圆孔，roof 为水平尖顶孔，
vertical 为竖直圆孔；每件沿 +X 尺寸依次 1.2/1.4/1.6/1.8。
尖顶孔尺寸指内接圆直径及最大宽度，上方额外延伸为 45 度尖顶，不是总高。
三件孔长均与外侧轴套相同；按导出朝向打印，无孔内支撑，材料与层高保持一致。
分别记录每种孔的可穿入、可转动及晃动情况，不能共用一个方向的孔径补偿。
铰链默认仍保留原圆孔 1.1，待新试片确认孔型及尺寸后再调整，不建议此时重打铰链。
magnet_gauge 沿 +X 孔径依次 5.12/5.22/5.32，为直径余量；孔深 2.8，
适配实测直径 5.02、高 2.58 的磁铁，底部小孔用于顶出，最终采用胶粘固定。
用户实测最大档 5.32 配合较好，作为最终磁铁孔的起始值；孔深保持 2.8。
"""

import math

from b4dcad import circle, cube, cylinder, polygon

PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BEARING_DIAMETER = 1.1
MAGNET_DIAMETER = 5.02
MAGNET_HEIGHT = 2.58
MAGNET_POCKET_DIAMETER = 5.32
PIN_GAUGE_DIAMETERS = (1.2, 1.4, 1.6, 1.8)

_AXIS_HEIGHT = 3.0
_BARREL_RADIUS = 2.4
_BLIND_WALL = 0.8
_SOCKET_LENGTH = 6.0
_AXIAL_GAP = 0.3
_GLUE_RECESS = 1.0
_PIN_RECESS = 0.5
_OUTER_LENGTH = _BLIND_WALL + PIN_LENGTH + _PIN_RECESS - _AXIAL_GAP - _SOCKET_LENGTH
_INNER_START = _OUTER_LENGTH + _AXIAL_GAP
_END_LENGTH = _INNER_START + _SOCKET_LENGTH
_LENGTH = 2 * _END_LENGTH + PIN_LENGTH + 2


def _bore(diameter, bottom, top):
    return cylinder(h=top - bottom, r=diameter / 2, fn=64).move(z=bottom)


def _axial_bore(diameter, start, end):
    return _bore(diameter, 0, end - start).rotate(x=-90).move(y=start, z=_AXIS_HEIGHT)


def _knuckle(start, end, left):
    """平底、圆顶轴套，根部与所属板面重叠 0.2。"""
    part = _axial_bore(2 * _BARREL_RADIUS, start, end)
    part += cube(2 * _BARREL_RADIUS, end - start, _AXIS_HEIGHT).move(
        x=-_BARREL_RADIUS, y=start
    )
    part += cube(4.7, end - start, _AXIS_HEIGHT).move(x=-4.7 if left else 0, y=start)
    return part


def pivot_leaf(left=True):
    """左件有朝内的装轴封胶口；右件有朝外的盲孔挡轴端。"""
    part = cube(14, _LENGTH, 1.2).move(x=-18.5 if left else 4.5)
    if left:
        intervals = (
            (_INNER_START, _END_LENGTH),
            (_LENGTH - _END_LENGTH, _LENGTH - _INNER_START),
        )
    else:
        intervals = ((0, _OUTER_LENGTH), (_LENGTH - _OUTER_LENGTH, _LENGTH))
    for start, end in intervals:
        part += _knuckle(start, end, left)
        bore_start = start - 0.1 if left or start else _BLIND_WALL
        bore_end = end + 0.1 if left or end < _LENGTH else _LENGTH - _BLIND_WALL
        part -= _axial_bore(BEARING_DIAMETER, bore_start, bore_end)
    if left:
        part -= _axial_bore(2.2, _END_LENGTH - _GLUE_RECESS, _END_LENGTH + 0.1)
        part -= _axial_bore(
            2.2, _LENGTH - _END_LENGTH - 0.1, _LENGTH - _END_LENGTH + _GLUE_RECESS
        )
    return part


def _roof_bore(diameter, start, end):
    """圆孔上接相切的 45 度尖顶，保留下半圆作为轴的支承面。"""
    radius = diameter / 2
    tangent = radius / math.sqrt(2)
    profile = circle(r=radius, fn=64) + polygon(
        [(-tangent, tangent), (tangent, tangent), (0, radius * math.sqrt(2))]
    )
    return profile.extrude(end - start).rotate(x=90).move(y=end, z=_AXIS_HEIGHT)


def pin_hole_gauge(kind="horizontal"):
    """相同长度和四档孔径，分别比较打印方向与横孔顶面形状。"""
    if kind not in ("horizontal", "roof", "vertical"):
        raise ValueError("孔型须为 horizontal、roof 或 vertical")
    if kind == "vertical":
        part = cube(40, 8, _OUTER_LENGTH)
    else:
        part = cube(40, _OUTER_LENGTH, _AXIS_HEIGHT + _BARREL_RADIUS)
    for i, diameter in enumerate(PIN_GAUGE_DIAMETERS):
        x = 5 + 10 * i
        if kind == "vertical":
            cutter = _bore(diameter, -0.1, _OUTER_LENGTH + 0.1).move(x=x, y=4)
        else:
            bore = _roof_bore if kind == "roof" else _axial_bore
            cutter = bore(diameter, -0.1, _OUTER_LENGTH + 0.1).move(x=x)
        part -= cutter
    return part


def magnet_hole_gauge():
    floor = 0.8
    depth = MAGNET_HEIGHT + 0.22
    part = cube(30, 10, floor + depth)
    for x, adjustment in zip((5, 15, 25), (-0.2, -0.1, 0)):
        part -= _bore(
            MAGNET_POCKET_DIAMETER + adjustment, floor, floor + depth + 0.1
        ).move(x=x, y=5)
        part -= _bore(2, -0.1, floor + 0.1).move(x=x, y=5)
    return part


left_leaf = pivot_leaf()
right_leaf = pivot_leaf(False).move(x=12)
pin_gauge_horizontal = pin_hole_gauge().move(x=44)
pin_gauge_roof = pin_hole_gauge("roof").move(x=44, y=16)
pin_gauge_vertical = pin_hole_gauge("vertical").move(x=44, y=32)
magnet_gauge = magnet_hole_gauge().move(x=44, y=45)

show_assembly = (
    pivot_leaf()
    + pivot_leaf(False).move(z=-_AXIS_HEIGHT).rotate(y=-70).move(z=_AXIS_HEIGHT)
).move(x=95)
