"""净化器接头试片，单位 mm。水平直角试板带一体三角撑，打印高度 17 mm。

dovetail_male / female 各打印一件，从 Z 方向拼合，测试平面燕尾松紧。
corner_horizontal / corner_vertical 各打印一件；沿 Y 的宽梳齿直接拼成直角，
无需独立接件。两端 Y 面齐平，用于试验滤网贴合边界；齿侧留配合间隙。
水平板 Y 两端各有一片 3 mm 厚、12 mm 高的内侧三角撑，胶粘到竖板内表面。
其他试片打印高度均为 5 mm；三角撑不超出 Y 端面。
直角梳齿用于定位和增加胶粘面积，不自锁，装配后仍需胶粘固定。
show_* 为装配预览，不导出。
"""

import math

from b4dcad import loft, polygon, square

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


def corner_test_parts(
    thickness=5.0,
    edge_length=60.0,
    panel_length=35.0,
    finger_count=6,
    clearance=0.15,
    gusset_leg=12.0,
    gusset_width=3.0,
):
    """两块自带交错梳齿的直角试板，返回平放的 A、B 及装配预览。

    平放坐标：板长沿 X（-panel_length 到 0），接合边沿 Y 居中，底面 Z=0。
    每齿宽 edge_length/finger_count，齿深等于 thickness，齿侧总间隙 clearance。
    仅内部齿边各退 clearance/2，最外侧 Y 端面不退让，保持滤网贴合面齐平。
    装配时 A 沿 X 移动 thickness，B 绕 Y 旋转 90°，接缝沿 Y，外角为
    X=thickness、Z=0；两个板仍在原有 Y 范围内，没有凸出的接件。
    A 两端的一体三角撑位于原 Y 范围内，内角两直角边长为 gusset_leg，
    沿 Y 厚度为 gusset_width；gusset_leg=0 可关闭。A 打印高度为
    thickness+gusset_leg。三角撑竖边贴 B 的内表面，胶粘固定。
    B 可从上方沿 -Z 落入 A 的齿间。此版本不倒角，先验证梳齿和撑板。
    """
    dimensions = (thickness, edge_length, panel_length)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("尺寸必须为有限正数")
    if (
        not isinstance(finger_count, int)
        or isinstance(finger_count, bool)
        or finger_count < 2
    ):
        raise ValueError("梳齿分段数必须为至少 2 的整数")
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("配合间隙必须为有限非负数")
    if thickness < 0.5 or panel_length - thickness < 0.5:
        raise ValueError("板厚和齿根后的板长必须至少为 0.5 mm")
    pitch = edge_length / finger_count
    if pitch - clearance < thickness:
        raise ValueError("梳齿净宽不得小于板厚，避免试件齿过细")
    if not math.isfinite(gusset_leg) or not 0 <= gusset_leg < panel_length - thickness:
        raise ValueError("三角撑边长必须非负且小于齿根后的板长")
    if not math.isfinite(gusset_width) or not 0.5 <= gusset_width < edge_length / 2:
        raise ValueError("三角撑厚度必须至少为 0.5 mm，且两端撑板之间须有间隔")

    body = (
        square(panel_length - thickness, edge_length)
        .move(x=-panel_length, y=-edge_length / 2)
        .extrude(thickness)
    )
    panels = [body, body]
    for i in range(finger_count):
        start = -edge_length / 2 + i * pitch
        end = start + pitch
        if i > 0:
            start += clearance / 2
        if i < finger_count - 1:
            end -= clearance / 2
        finger = (
            square(thickness, end - start)
            .move(x=-thickness, y=start)
            .extrude(thickness)
        )
        panels[i % 2] += finger
    if gusset_leg:
        gusset = (
            polygon(
                [
                    (-thickness, thickness),
                    (-thickness - gusset_leg, thickness),
                    (-thickness, thickness + gusset_leg),
                ]
            )
            .extrude(gusset_width)
            .rotate(x=90)
        )
        for y in (-edge_length / 2 + gusset_width, edge_length / 2):
            panels[0] += gusset.move(y=y)
    assembly = panels[0].move(x=thickness) + panels[1].rotate(y=90)
    return panels[0], panels[1], assembly


dovetail_male, dovetail_female = dovetail_coupons()
show_dovetail_assembled = dovetail_male + dovetail_female
show_dovetail_exploded = dovetail_male + dovetail_female.move(x=12, z=8)

corner_horizontal, corner_vertical, show_corner_assembled = corner_test_parts()
show_corner_exploded = corner_horizontal.move(x=5) + corner_vertical.rotate(y=90).move(
    z=12
)
