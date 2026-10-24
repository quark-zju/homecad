"""净化器接头试片，单位 mm。所有导出件均平放，打印高度不超过 6 mm。

dovetail_male / female 各打印一件，从 Z 方向拼合，测试平面燕尾松紧。
corner_connector 打印两件，corner_panel 两件，corner_wedge 四件；
两块板分别插入互相垂直的槽，楔子从槽口沿板边插入，逐步压紧。
楔子露出的尾部用于拔出。此处先测试摩擦锁紧，未设计防退卡扣。
show_* 为装配预览，不导出；直角组件的两块试板可用同一模型打印。
"""

import math

from b4dcad import polygon, square

from air_purifier import dovetail_tabs


def dovetail_coupons(edge_length=40.0, depth=16.0, thickness=5.0, clearance=0.2):
    """一对短边燕尾试片，接缝 X=0；沿用盖板上的双榫 primitive。"""
    if not math.isfinite(depth) or depth <= 5 + clearance:
        raise ValueError("试片深度必须大于榫深和余量")
    tabs = dovetail_tabs(edge_length, thickness=thickness)
    cutter = dovetail_tabs(
        edge_length, thickness=thickness + 2, clearance=clearance
    ).move(z=-1)
    blank = square(depth, edge_length).extrude(thickness)
    return (
        blank.move(x=-depth, y=-edge_length / 2) + tabs,
        blank.move(y=-edge_length / 2) - cutter,
    )


def corner_test_parts(
    panel_thickness=5.0,
    clearance=0.3,
    wall=2.4,
    grip_depth=10.0,
    width=6.0,
    wedge_gap=1.4,
    panel_length=35.0,
    panel_width=24.0,
):
    """返回平放的直角双槽接件、通用试板、楔子及装配预览。

    接件截面在 XY，沿 Z 挤出 width；两槽朝 +X、+Y 开口。
    槽宽=板厚+clearance+wedge_gap。每条槽里用一个楔子填充板外侧间隙。
    楔子厚度沿长度渐增，到达默认插深时恰好接触槽壁；继续推进会压紧。
    装配预览包含两接件、四楔子、两试板，再绕 X 旋转 90° 以展示直角。
    """
    dimensions = (
        panel_thickness,
        wall,
        grip_depth,
        width,
        wedge_gap,
        panel_length,
        panel_width,
    )
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("槽余量必须为有限非负数")
    if min(wall, width, panel_thickness) < 0.5:
        raise ValueError("试件壁厚不得小于 0.5 mm")
    if panel_width < 3 * width or panel_length <= grip_depth:
        raise ValueError("试板必须容纳两个分开的接件，并伸出插槽")

    gap = clearance + wedge_gap
    if gap <= 0.5:
        raise ValueError("楔子空间必须大于 0.5 mm 的尖端厚度")
    slot_width = panel_thickness + gap
    arm = 2 * wall + slot_width
    end = arm + grip_depth
    outline = square(end, arm) + square(arm, end)
    slot = square(grip_depth + 1, slot_width).move(x=arm, y=wall)
    connector = (outline - slot - slot.mirror(x=1, y=-1)).extrude(width)

    tail = 4.0
    wedge_length = grip_depth + tail
    tip = 0.5
    heel = tip + (gap - tip) * wedge_length / grip_depth
    wedge = polygon([(0, 0), (wedge_length, 0), (wedge_length, heel), (0, tip)])
    wedge = wedge.extrude(width)
    panel = square(panel_length, panel_width).extrude(panel_thickness)

    # 装配坐标中，试板厚度在 XY 截面内，板边沿 Z 延伸。
    first_panel = (
        square(panel_length, panel_thickness).extrude(panel_width).move(x=arm, y=wall)
    )
    second_panel = first_panel.mirror(x=1, y=-1)
    seated_wedge = wedge.move(x=arm, y=wall + panel_thickness)
    station = connector + seated_wedge + seated_wedge.mirror(x=1, y=-1)
    assembly = first_panel + second_panel
    for z in (width / 2, panel_width - 1.5 * width):
        assembly += station.move(z=z)
    assembly = assembly.rotate(x=90).align(zmin=0)
    return connector, panel, wedge, assembly


dovetail_male, dovetail_female = dovetail_coupons()
show_dovetail_assembled = dovetail_male + dovetail_female
show_dovetail_exploded = dovetail_male + dovetail_female.move(x=12, z=8)

corner_connector, corner_panel, corner_wedge, show_corner_assembled = (
    corner_test_parts()
)
