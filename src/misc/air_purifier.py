"""净化器小组件。尺寸单位为 mm；各组件独立建模，便于后续装配。"""

import math

from b4dcad import cylinder, polygon, square


def dovetail_edge(
    edge_length,
    thickness=5.0,
    angle=30.0,
    root_width=0.8,
    clearance=0.0,
):
    """沿板边的两个反向梯形，平放打印，无封闭槽顶；单位 mm、度。

    板在 X<0，边沿 Y 居中，底面 Z=0。Y<0 段下宽上窄，Y>0 段上宽下窄；
    斜面相对竖直方向为 angle（限 45° 内）。边界围绕 X=0 内外各偏移
    thickness * tan(angle) / 2。root_width 是最窄处保留的连接条宽度。
    返回替换板边的连接条：先从板上去掉同宽的直边条，再与本组件相加。
    需替换的直边条宽为 thickness * tan(angle) / 2 + root_width。
    对边使用同一组件绕 Z 旋转 180°，两块相同板即可互补拼接。
    clearance 为每块板沿斜面法向退让的距离，两板的总间隙为其两倍。
    """
    dimensions = (edge_length, thickness, root_width)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if not math.isfinite(angle) or not 0 < angle <= 45:
        raise ValueError("无支撑斜角必须大于 0 且不超过 45 度")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("配合余量必须为有限非负数")

    radians = math.radians(angle)
    reach = thickness * math.tan(radians) / 2
    inset = clearance / math.cos(radians)
    if inset >= root_width:
        raise ValueError("配合余量过大，梯形根部必须保留连接宽度")
    back = -reach - root_width
    halves = []
    for direction in (1, -1):
        profile = polygon(
            [
                (back, 0),
                (direction * reach - inset, 0),
                (-direction * reach - inset, thickness),
                (back, thickness),
            ]
        )
        halves.append(
            profile.extrude(edge_length / 2)
            .rotate(x=90)
            .move(y=0 if direction == 1 else edge_length / 2)
        )
    return halves[0] + halves[1]


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
# 先替换左右直边，再加入两个反向梯形；不使用封闭凹槽。
_edge_width = 5 * math.tan(math.radians(30)) / 2 + 0.8
_edge_cut = square(2 * _edge_width, 140, center=True).extrude(5)
_edge_joint = dovetail_edge(edge_length=140, clearance=0.15)
p14_plate = p14_plate - _edge_cut.move(x=70) - _edge_cut.move(x=-70)
p14_plate += _edge_joint.move(x=70)
p14_plate += _edge_joint.rotate(z=180).move(x=-70)
show_connected_pair = p14_plate + p14_plate.move(x=140)
