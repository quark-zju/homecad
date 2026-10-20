"""净化器小组件。尺寸单位为 mm；各组件独立建模，便于后续装配。"""

import math

from b4dcad import cylinder, square


def p14_cover(
    thickness=3.0,
    plate_size=140.0,
    hole_pitch=125.0,
    screw_hole_diameter=4.3,
    opening_diameter=134.2,
):
    """P14 安装盖板：直角方板、圆形通风口、四个通孔。

    XY 居中、底面 Z=0。板厚为设计值，可按后续连接结构调整。
    孔径为几何尺寸，不自动增加打印配合余量。
    """
    dimensions = (
        thickness,
        plate_size,
        hole_pitch,
        screw_hole_diameter,
        opening_diameter,
    )
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if opening_diameter >= plate_size:
        raise ValueError("通风口必须小于板宽")
    if hole_pitch + screw_hole_diameter >= plate_size:
        raise ValueError("螺钉孔必须位于板内")
    if hole_pitch * math.sqrt(2) <= opening_diameter + screw_hole_diameter:
        raise ValueError("螺钉孔不能与通风口相交")

    plate = square(plate_size, plate_size, center=True).extrude(thickness)
    opening = cylinder(h=thickness + 2, d=opening_diameter, fn=256).move(z=-1)
    plate -= opening
    screw_hole = cylinder(h=thickness + 2, d=screw_hole_diameter, fn=64).move(z=-1)
    for x in (-hole_pitch / 2, hole_pitch / 2):
        for y in (-hole_pitch / 2, hole_pitch / 2):
            plate -= screw_hole.move(x=x, y=y)
    return plate


p14_plate = p14_cover()
