"""净化器小组件。尺寸单位为 mm；各组件独立建模，便于后续装配。"""

import math

from b4dcad import cylinder, polygon, square


def dovetail_tabs(
    edge_length,
    thickness=5.0,
    neck_width=8.0,
    depth=5.0,
    spacing=None,
    angle=30.0,
    overlap=0.8,
    clearance=0.0,
):
    """沿直边的两个共面燕尾榫；尺寸单位 mm，角度单位度。

    边位于 X=0、沿 Y 居中，板在 X<0，榫向 +X 伸出，底面 Z=0。
    angle 为梯形腰相对 +X 的夹角；neck_width 是 X=0 处的榫宽。
    spacing 为两榫中心距，默认边长的一半；overlap 为埋入板内的深度。
    clearance 将轮廓各边向外偏移，可用于切另一块板的凹槽。
    返回的两个榫独立，需与板相加；可旋转、平移到其他板边。
    """
    if spacing is None:
        spacing = edge_length / 2
    dimensions = (edge_length, thickness, neck_width, depth, spacing, overlap)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if not math.isfinite(angle) or not 0 < angle < 90:
        raise ValueError("燕尾斜角必须在 0 到 90 度之间")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("配合余量必须为有限非负数")

    slope = math.tan(math.radians(angle))
    root_half_width = neck_width / 2 - overlap * slope
    tip_half_width = neck_width / 2 + depth * slope
    if root_half_width <= 0:
        raise ValueError("埋入深度过大，燕尾根部宽度必须为正")
    profile = polygon(
        [
            (-overlap, -root_half_width),
            (depth, -tip_half_width),
            (depth, tip_half_width),
            (-overlap, root_half_width),
        ]
    )
    if clearance:
        profile = profile.offset(clearance, "miter")
    tab = profile.extrude(thickness)
    half_width = tab.size().y / 2
    if 2 * half_width >= spacing:
        raise ValueError("两个燕尾榫必须留有间隔")
    if spacing / 2 + half_width >= edge_length / 2:
        raise ValueError("燕尾榫必须位于板边范围内")
    return tab.move(y=-spacing / 2) + tab.move(y=spacing / 2)


def p14_cover(
    thickness=5.0,
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
p14_plate += dovetail_tabs(edge_length=140).move(x=70)
p14_plate -= dovetail_tabs(edge_length=140, thickness=7, clearance=0.2).move(
    x=-70, z=-1
)
show_connected_pair = p14_plate + p14_plate.move(x=140)
