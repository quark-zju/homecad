"""净化器接头试片，单位 mm。水平直角试板带一体小三角，打印高度 11 mm。

dovetail_male / female 各打印一件，从 Z 方向拼合，测试平面燕尾松紧。
corner_horizontal / corner_vertical 各打印一件；水平板带朝 +Z 的燕尾公榫，竖板底边为母槽，从 +X 侧面滑入。
两端 Y 面齐平；水平板两端各有 3 mm 厚、6 mm 高的一体小三角，辅助定位。
水平板打印高度 11 mm，其他试片为 5 mm；小三角竖边需胶粘到竖板内表面。
直角内侧保留填胶倒角，燕尾配合余量为单边 0.1 mm。
show_* 为装配预览，不导出。
"""

import math

from b4dcad import loft, polygon, square, union

from air_purifier import dovetail_tabs


def dovetail_coupons(
    edge_length=40.0, depth=16.0, thickness=5.0, clearance=0.1, chamfer=0.8
):
    """短边燕尾试片；clearance 为凹槽单边余量，chamfer 为顶面填胶槽深。

    顶面 Z=thickness 沿整条接缝切 90° V 槽，槽口宽约为 2*chamfer（另加原配合间隙）。
    底面不倒角，下方 thickness-chamfer 高度保留原燕尾定位轮廓。
    chamfer=0 可关闭填胶槽；先干装，再从顶面压入填缝胶。
    """
    if not math.isfinite(depth) or depth <= 5 + clearance:
        raise ValueError("试片深度必须大于榫深和余量")
    if not math.isfinite(chamfer) or not 0 <= chamfer <= thickness - 0.5:
        raise ValueError("倒角深度必须非负，并保留至少 0.5 mm 的定位高度")
    tabs = dovetail_tabs(edge_length, thickness=thickness)
    cutter = dovetail_tabs(
        edge_length, thickness=thickness + 2, clearance=clearance
    ).move(z=-1)
    blank_profile = square(depth, edge_length).move(y=-edge_length / 2)
    male_profile = blank_profile.move(x=-depth) + tabs.project()
    male = male_profile.extrude(thickness)
    female = blank_profile.extrude(thickness) - cutter
    if chamfer:
        # 扩大非接缝的外边界，使内缩放样只切到接缝，不改变试片外围。
        extended_blank = square(depth + 2 * chamfer, edge_length + 4 * chamfer).move(
            y=-edge_length / 2 - 2 * chamfer
        )
        male_extended = extended_blank.move(x=-depth - 2 * chamfer) + tabs.project()
        female_extended = extended_blank - cutter.project()
        male = _top_seam_chamfer(male, male_extended, thickness, chamfer)
        female = _top_seam_chamfer(female, female_extended, thickness, chamfer)
    return male, female


def _top_seam_chamfer(part, extended_profile, thickness, chamfer):
    """上方 45° 内缩放样；扩大的轮廓保护非接缝外边缘。"""
    shoulder = thickness - chamfer
    profile = part.project()
    xmin, ymin, _, xmax, ymax, _ = part.bounding_box()
    bounds = square(xmax - xmin, ymax - ymin).move(x=xmin, y=ymin)
    top_profile = extended_profile.offset(-chamfer, "miter") & bounds
    return profile.extrude(shoulder) + loft(
        [profile, top_profile], [shoulder, thickness], match="shortest"
    )


def _standing_corner_panel(panel, thickness):
    """刚性旋转平放的竖板，使顶面填胶倒角朝向装配后的直角内侧。"""
    return panel.rotate(x=180).move(z=thickness).rotate(y=90).move(z=thickness)


def corner_test_parts(
    thickness=5.0,
    edge_length=60.0,
    panel_length=35.0,
    clearance=0.1,
    chamfer=0.8,
    gusset_leg=6.0,
    gusset_width=3.0,
):
    """燕尾直角试片：水平公榫板、平放竖槽板、装配预览。

    公榫从水平板顶面向 +Z 伸出 thickness，榫头沿 Y 比榫根宽。
    竖板下缘为对应母槽，从 +X 向 -X 侧滑入，不能从上方直接套入。
    公榫与母槽在内侧 X=0 面均有填胶倒角，便于从直角内部压胶。
    榫深等于板厚；板厚改变时仍保留 8 mm 榫颈和 30° 斜角。
    小三角与水平板一体，边长 gusset_leg、Y 厚 gusset_width；设边长为 0
    可关闭。所有结构均在原 Y 范围内，滤网贴合端面保持齐平。
    水平板返回时沿 X 移动 -thickness，装配需移回；竖板用
    _standing_corner_panel() 放置。小三角与竖板接触面需胶粘固定。
    """
    dimensions = (thickness, edge_length, panel_length)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if thickness < 0.5 or panel_length <= 2 * thickness + clearance:
        raise ValueError("板厚至少为 0.5 mm，板长必须容纳榫及后方板面")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("配合间隙必须为有限非负数")
    if not math.isfinite(chamfer) or not 0 <= chamfer <= thickness - 0.5:
        raise ValueError("倒角必须非负且保留至少 0.5 mm 的定位高度")
    if not math.isfinite(gusset_leg) or not 0 <= gusset_leg < panel_length - thickness:
        raise ValueError("小三角边长必须非负且小于内侧板长")
    if not math.isfinite(gusset_width) or not 0.5 <= gusset_width < edge_length / 2:
        raise ValueError("小三角厚度至少为 0.5 mm，且两端之间须有间隔")

    tabs = dovetail_tabs(edge_length, thickness=thickness, depth=thickness)
    # 分别倒角两个榫的内侧面；旋转后 canonical +X 成为实际 +Z。
    if chamfer:
        tabs = union(
            _top_seam_chamfer(tab, tab.project(), thickness, chamfer)
            for tab in tabs.decompose()
        )
    upright_tabs = tabs.rotate(y=-90).move(x=thickness, z=thickness)
    horizontal = (
        square(panel_length, edge_length)
        .move(x=thickness - panel_length, y=-edge_length / 2)
        .extrude(thickness)
        + upright_tabs
    )
    raw_socket = dovetail_tabs(
        edge_length,
        thickness=thickness + 2 * clearance,
        depth=thickness,
        clearance=clearance,
    )
    socket = raw_socket.rotate(y=-90).move(x=thickness + clearance, z=thickness)
    standing = (
        square(thickness, edge_length)
        .move(y=-edge_length / 2)
        .extrude(panel_length - thickness)
        .move(z=thickness)
        - socket
    )
    if gusset_leg:
        gusset = (
            polygon(
                [(0, thickness), (-gusset_leg, thickness), (0, thickness + gusset_leg)]
            )
            .extrude(gusset_width)
            .rotate(x=90)
        )
        for start in (-edge_length / 2, edge_length / 2 - gusset_width):
            horizontal += gusset.move(y=start + gusset_width)
    vertical = (
        standing.move(z=-thickness).rotate(y=-90).move(z=-thickness).rotate(x=180)
    )
    if chamfer:
        flat_socket = (
            socket.move(z=-thickness).rotate(y=-90).move(z=-thickness).rotate(x=180)
        )
        extended = (
            square(panel_length + 2 * chamfer, edge_length + 4 * chamfer).move(
                x=-panel_length - 2 * chamfer, y=-edge_length / 2 - 2 * chamfer
            )
            - flat_socket.project()
        )
        vertical = _top_seam_chamfer(vertical, extended, thickness, chamfer)
    assembly = horizontal + _standing_corner_panel(vertical, thickness)
    return horizontal.move(x=-thickness), vertical, assembly


dovetail_male, dovetail_female = dovetail_coupons()
show_dovetail_assembled = dovetail_male + dovetail_female
show_dovetail_exploded = dovetail_male + dovetail_female.move(x=12, z=8)

corner_horizontal, corner_vertical, show_corner_assembled = corner_test_parts()
show_corner_exploded = corner_horizontal.move(x=5) + _standing_corner_panel(
    corner_vertical, 5
).move(x=14)
