"""净化器小组件。尺寸单位为 mm；各组件独立建模，便于后续装配。"""

import math

from b4dcad import cylinder, polygon, square


def dovetail_edge(
    edge_length,
    thickness=5.0,
    neck_height=None,
    depth=None,
    angle=30.0,
    overlap=None,
    clearance=0.0,
):
    """板侧边的连续燕尾连接条，沿板边方向滑入；单位 mm、度。

    板在 X<0，边沿 Y 居中，底面 Z=0；燕尾截面位于 XZ 平面。
    榫向 +X 伸出 depth，厚度方向居中；angle 为斜面相对 +X 的夹角。
    neck_height 为 X=0 处的榫高，默认板厚的 36%；depth 默认板厚的 30%。
    overlap 为埋入板内的深度，默认板厚的 15%。返回连接条，需与板相加。
    clearance 沿截面各边向外偏移，用作另一块板的凹槽刀具；刀具沿 Y
    两端各延长 clearance，使槽口贯通。旋转、平移后可用于其他直板边。
    """
    if neck_height is None:
        neck_height = thickness * 0.36
    if depth is None:
        depth = thickness * 0.3
    if overlap is None:
        overlap = thickness * 0.15
    dimensions = (edge_length, thickness, neck_height, depth, overlap)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if not math.isfinite(angle) or not 0 < angle < 90:
        raise ValueError("燕尾斜角必须在 0 到 90 度之间")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("配合余量必须为有限非负数")

    slope = math.tan(math.radians(angle))
    root_half_height = neck_height / 2 - overlap * slope
    tip_half_height = neck_height / 2 + depth * slope
    if root_half_height <= 0:
        raise ValueError("埋入深度过大，燕尾根部高度必须为正")
    profile = polygon(
        [
            (-overlap, -root_half_height),
            (depth, -tip_half_height),
            (depth, tip_half_height),
            (-overlap, root_half_height),
        ]
    )
    if clearance:
        profile = profile.offset(clearance, "miter")
    if profile.extrude(1).size().y >= thickness:
        raise ValueError("燕尾截面及余量必须位于板厚内，为凹槽保留上下壁")
    return (
        profile.extrude(edge_length + 2 * clearance)
        .rotate(x=90)
        .move(y=edge_length / 2 + clearance, z=thickness / 2)
    )


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
p14_plate += dovetail_edge(edge_length=140).move(x=70)
p14_plate -= dovetail_edge(edge_length=140, clearance=0.2).move(x=-70)
show_connected_pair = p14_plate + p14_plate.move(x=140)
