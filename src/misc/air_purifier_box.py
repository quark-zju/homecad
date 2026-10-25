"""双滤网、六 P14 净化器。单位 mm，X/Z 为滤网面，Y 为箱体深度。

滤网放置净尺寸 496.2 方形，前后各容纳 15 mm 厚度，其余外露并用胶带封边。
默认外形 506.2×178.2×506.2；接头板厚 5，无风扇板中部 2，最高打印高度 13。
top/right 各三块风扇板，bottom/left 各五块短板；默认 16 件、11 盘，
按 240×240 可用平台预排。风扇和滤网均为 show_* 预览，不导出。
先拼合每面，再利用水平板的内向公榫侧滑装配竖板；内部倒角填胶密封。
最后封闭的侧面须同时对准上下母槽，沿 X 滑入，不可从 Z 方向硬压。
风扇固定通孔沿用 P14 盖板，紧固件另备；电源口高 21、宽 17，需按线材密封。
止口内侧上沿的长缺口标记面别：bottom=1、left=2、top=3、right=4；
旁边短缺口的数量为分件序号，与文件名后缀一致。长短默认 6/2，深 1.5。
两组之间留 8 mm 间隔；例如 top_2 为三个长缺口、两个短缺口。前后重复标记，
不依赖观察方向；滤网接触面保持完整。mark_depth=0 可关闭标记。
风扇排向无风扇转角偏置；风扇外框到拼缝倒角边保留 sealant_land（默认 8）。
每只风扇沿分件方向的两侧有短定位块，高度与滤网止口一致，外框单边余量 0.4。
"""

from dataclasses import dataclass
import math

from b4dcad import cylinder, loft, mesh, polygon, square, union


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


@dataclass(frozen=True)
class BoxDimensions:
    filter_size: float = 495.0
    filter_clearance: float = 1.2  # 总余量，单边 0.6。
    filter_capture: float = 15.0
    stop_width: float = 8.0
    stop_thickness: float = 3.0
    fan_size: float = 140.2
    fan_thickness: float = 28.25
    fan_clearance: float = 1.0
    corner_fan_clearance: float = 2.0
    sealant_land: float = 8.0
    fan_locator_clearance: float = 0.4
    fan_locator_width: float = 2.0  # 设为 0 关闭短定位块。
    fan_locator_length: float = 18.0
    thickness: float = 5.0
    web_thickness: float = 2.0  # 无风扇面中央薄壁，周边及接头仍为 5 mm。
    frame_width: float = 8.0
    hole_pitch: float = 125.0
    screw_hole: float = 4.3
    fan_opening: float = 134.2
    joint_clearance: float = 0.1
    joint_depth: float = 5.0
    chamfer: float = 0.8
    gusset_leg: float = 6.0
    gusset_width: float = 3.0
    cable_hole: float = 17.0  # 电源口宽度，沿箱体 Y；设为 0 关闭。
    cable_hole_height: float = 21.0  # 电源口高度，沿箱体 Z。
    cable_height: float = 35.0  # 电源口中心离底部的高度。
    bed_size: float = 240.0  # 260 平台主动留边。
    bed_gap: float = 8.0
    mark_depth: float = 1.5
    mark_width: float = 1.5
    mark_short: float = 2.0
    mark_long: float = 6.0
    mark_spacing: float = 2.5
    mark_group_gap: float = 8.0

    @property
    def span(self):
        return self.filter_size + self.filter_clearance

    @property
    def depth(self):
        return self.fan_size + 2 * (
            self.filter_capture + self.stop_thickness + self.fan_clearance
        )

    @property
    def fan_centers(self):
        """顶部三风扇：保持右侧双风扇转角避让，向左侧空转角偏置。"""
        last = (
            self.span
            - self.fan_thickness
            - self.corner_fan_clearance
            - self.fan_size / 2
        )
        pitch = self.fan_size + 2 * (self.sealant_land + self.chamfer)
        return (last - 2 * pitch, last - pitch, last)

    def fan_centers_for(self, wall):
        # 右面打印坐标 U 与装配后的 Z 相反；危险转角位于 U=0。
        if wall == "right":
            return tuple(self.span - center for center in reversed(self.fan_centers))
        return self.fan_centers

    @property
    def blank_segments(self):
        usable = (self.bed_size - self.bed_gap) / 2 - self.joint_depth
        return math.ceil((self.span + 2 * self.thickness) / usable)

    def validate(self):
        nonnegative = {
            "filter_clearance",
            "fan_clearance",
            "corner_fan_clearance",
            "joint_clearance",
            "chamfer",
            "gusset_leg",
            "cable_hole",
            "mark_depth",
            "fan_locator_clearance",
            "fan_locator_width",
        }
        for name, value in vars(self).items():
            if (
                not math.isfinite(value)
                or value < 0
                or (value == 0 and name not in nonnegative)
            ):
                raise ValueError(f"{name} 必须为有限有效尺寸")
        if self.thickness < 0.5 or self.stop_thickness < 0.5 or self.gusset_width < 0.5:
            raise ValueError("打印壁厚必须至少为 0.5 mm")
        if self.chamfer > self.thickness - 0.5:
            raise ValueError("倒角后必须保留至少 0.5 mm 定位厚度")
        if not 0.5 <= self.web_thickness <= self.thickness:
            raise ValueError("中央薄壁必须至少 0.5 mm，且不大于接头板厚")
        free_end = self.fan_centers[0] - self.fan_size / 2
        required = (
            max(self.stop_width, self.gusset_leg + self.joint_clearance)
            + self.corner_fan_clearance
        )
        if free_end < required:
            raise ValueError(
                "三个风扇、转角避让及填胶余量无法同时容纳；请减小 sealant_land 或增大滤网边长"
            )
        if (self.bed_size - self.bed_gap) / 2 <= self.joint_depth:
            raise ValueError("可用平台太小")
        if self.gusset_leg >= self.stop_width:
            raise ValueError("小三角应位于止口宽度内，避免占用风扇空间")
        if self.cable_hole and not (
            self.stop_width + self.cable_hole_height / 2
            < self.cable_height
            < self.span - self.stop_width - self.cable_hole_height / 2
        ):
            raise ValueError("电源线孔离转角过近")
        if self.fan_locator_width:
            if self.fan_locator_width < 0.5 or self.fan_locator_length < 2:
                raise ValueError("风扇定位块壁厚至少 0.5 mm，长度至少 2 mm")
            if self.fan_locator_length >= self.fan_size:
                raise ValueError("短定位块长度必须小于风扇宽度")
            if (
                self.fan_locator_clearance + self.fan_locator_width
                > self.sealant_land - 2
            ):
                raise ValueError("定位块到填胶倒角边须保留至少 2 mm 操作空间")
        if self.mark_depth:
            if self.mark_depth > self.stop_width - 0.5:
                raise ValueError("标记不能切穿止口，底部须保留至少 0.5 mm")
            if self.mark_width > self.stop_thickness - 0.5:
                raise ValueError("标记须保留至少 0.5 mm 完整滤网接触面")
            if self.mark_depth < 0.5 or self.mark_width < 0.5:
                raise ValueError("标记宽深至少为 0.5 mm，便于 FDM 打印识别")
            if self.mark_short < 1 or self.mark_long < 2 * self.mark_short:
                raise ValueError("短缺口至少 1 mm，长缺口至少为短缺口的两倍")
            if self.mark_spacing < 1 or self.mark_group_gap < 2 * self.mark_spacing:
                raise ValueError("缺口间隔至少 1 mm，组间距至少为缺口间距的两倍")


def _wall_to_world(part, wall, d):
    """四面都以内表面朝 +Z 平放打印，再作刚性装配变换。"""
    if wall == "bottom":
        return part.move(z=-d.thickness)
    if wall == "top":
        return part.rotate(x=180).move(y=d.depth, z=d.span + d.thickness)
    if wall == "left":
        return part.rotate(x=180).rotate(y=-90).move(x=-d.thickness, y=d.depth)
    return (
        part.rotate(y=90)
        .rotate(z=180)
        .move(x=d.span + d.thickness, y=d.depth, z=d.span)
    )


def _tabs(d, thickness=None, clearance=0.0, depth=None):
    return dovetail_tabs(
        edge_length=d.depth,
        thickness=d.thickness if thickness is None else thickness,
        depth=d.joint_depth if depth is None else depth,
        clearance=clearance,
    ).move(y=d.depth / 2)


def _corner_males(d):
    tabs = _tabs(d, depth=d.thickness)
    if d.chamfer:
        tabs = union(
            _top_seam_chamfer(tab, tab.project(), d.thickness, d.chamfer)
            for tab in tabs.decompose()
        )
    right = tabs.rotate(y=-90).move(x=d.span + d.thickness, z=d.thickness)
    return right, right.mirror(x=1).move(x=d.span)


def _bounds(wall, d):
    horizontal = wall in ("bottom", "top")
    start, end = (-d.thickness, d.span + d.thickness) if horizontal else (0, d.span)
    if wall in ("top", "right"):
        a, b, c = d.fan_centers_for(wall)
        return (start, (a + b) / 2, (b + c) / 2, end)
    n = d.blank_segments
    return tuple(start + (end - start) * i / n for i in range(n + 1))


def _chunk_profile(wall, i, bounds, d, extended=False):
    start, end = bounds[i : i + 2]
    first, last = i == 0, i == len(bounds) - 2
    side = wall in ("left", "right")
    padding = 2 * d.chamfer if extended else 0
    a = start - padding if first and not side else start
    b = end + padding if last and not side else end
    profile = square(b - a, d.depth + 2 * padding).move(x=a, y=-padding)
    if not last:
        profile += _tabs(d).project().move(x=end)
    if not first:
        profile -= _tabs(d, clearance=d.joint_clearance).project().move(x=start)
    if side:
        female = _tabs(d, clearance=d.joint_clearance, depth=d.thickness).project()
        if first:
            profile -= female
        if last:
            profile -= female.mirror(x=1).move(x=d.span)
    return profile


def _guides(d):
    if not d.gusset_leg:
        return None
    edge = d.span - d.joint_clearance
    section = polygon(
        [
            (edge, d.thickness),
            (edge - d.gusset_leg, d.thickness),
            (edge, d.thickness + d.gusset_leg),
        ]
    )
    guide = section.extrude(d.gusset_width).rotate(x=90)
    right = union(
        guide.move(y=y)
        for y in (
            d.filter_capture + d.stop_thickness + d.fan_clearance + d.gusset_width,
            d.depth - d.filter_capture - d.stop_thickness - d.fan_clearance,
        )
    )
    return right + right.mirror(x=1).move(x=d.span)


def _fan_void(d):
    # 复用已有 P14 盖板生成孔群，避免维护第二套安装孔几何。
    blank = square(d.fan_size, d.fan_size, center=True).extrude(d.thickness + 2)
    cover = p14_cover(
        thickness=d.thickness + 2,
        plate_size=d.fan_size,
        hole_pitch=d.hole_pitch,
        screw_hole_diameter=d.screw_hole,
        opening_diameter=d.fan_opening,
    )
    return (blank - cover).move(z=-1)


def _fan_locators(center, d):
    """一体短定位块，夹住风扇 U 两侧；不跨接缝，不遮孔位。"""
    edge = d.fan_size / 2 + d.fan_locator_clearance
    return union(
        square(d.fan_locator_width, d.fan_locator_length)
        .move(x=x, y=(d.depth - d.fan_locator_length) / 2)
        .extrude(d.stop_width)
        .move(z=d.thickness)
        for x in (center - edge - d.fan_locator_width, center + edge)
    )


def _part_marks(wall, index, start, end, d):
    """止口内侧的两组平底缺口：长缺口数量为面别，短缺口数量为序号。"""
    face = {"bottom": 1, "left": 2, "top": 3, "right": 4}[wall]
    face_width = face * d.mark_long + (face - 1) * d.mark_spacing
    index_width = (index + 1) * d.mark_short + index * d.mark_spacing
    length = face_width + d.mark_group_gap + index_width
    if end - start < length + 8:
        raise ValueError("止口可用长度不足以容纳分件标记")
    first = (start + end - length) / 2
    second = first + face_width + d.mark_group_gap
    height = d.thickness + d.stop_width
    marks = []
    for y in (
        d.filter_capture + d.stop_thickness - d.mark_width,
        d.depth - d.filter_capture - d.stop_thickness - 0.05,
    ):
        for count, mark_length, origin in (
            (face, d.mark_long, first),
            (index + 1, d.mark_short, second),
        ):
            for i in range(count):
                marks.append(
                    square(mark_length, d.mark_width + 0.05)
                    .move(x=origin + i * (mark_length + d.mark_spacing), y=y)
                    .extrude(d.mark_depth + 0.05)
                    .move(z=height - d.mark_depth)
                )
    return union(marks)


def _build_chunk(wall, i, bounds, d, fan_void, corner_males, guides):
    start, end = bounds[i : i + 2]
    profile = _chunk_profile(wall, i, bounds, d)
    part = profile.extrude(d.thickness)
    if d.chamfer:
        part = _top_seam_chamfer(
            part,
            _chunk_profile(wall, i, bounds, d, extended=True),
            d.thickness,
            d.chamfer,
        )
    clip = (
        square(end - start, d.depth)
        .extrude(d.thickness + max(d.stop_width, d.gusset_leg) + d.thickness)
        .move(x=start)
    )
    # 止口与根部一次挤出，避免倒角下方留下悬空底面。
    stop_start, stop_end = (
        (0, d.span)
        if wall in ("bottom", "top")
        else (d.stop_width, d.span - d.stop_width)
    )
    a, b = max(start, stop_start), min(end, stop_end)
    if a < b:
        for y in (d.filter_capture, d.depth - d.filter_capture - d.stop_thickness):
            foot = square(b - a, d.stop_thickness).move(x=a, y=y) & profile
            part += foot.extrude(d.thickness + d.stop_width)
    if wall in ("bottom", "top"):
        if i == 0:
            part += corner_males[1]
        if i == len(bounds) - 2:
            part += corner_males[0]
        if guides is not None:
            part += guides & clip
    if wall in ("top", "right"):
        center = d.fan_centers_for(wall)[i]
        part -= fan_void.move(x=center, y=d.depth / 2)
        if d.fan_locator_width:
            part += _fan_locators(center, d)
    if (
        wall == "left"
        and d.cable_hole
        and start < d.cable_height + d.cable_hole_height / 2
        and end > d.cable_height - d.cable_hole_height / 2
    ):
        hole = (
            square(d.cable_hole_height, d.cable_hole, center=True)
            .extrude(d.thickness + 2)
            .move(x=d.cable_height, y=d.depth / 2, z=-1)
        )
        part -= hole
    if wall in ("bottom", "left"):
        keep = d.filter_capture + d.stop_thickness + d.fan_clearance + d.gusset_width
        width, depth = end - start - 2 * d.frame_width, d.depth - 2 * keep
        if width <= 0 or depth <= 0:
            raise ValueError("无风扇短板太小，无法保留加强边框")
        pocket = (
            square(width, depth)
            .move(x=start + d.frame_width, y=keep)
            .extrude(d.thickness - d.web_thickness + 1)
            .move(z=d.web_thickness)
        )
        part -= pocket
    if d.mark_depth and a < b:
        part -= _part_marks(wall, i, a, b, d)
    return part.as_original().simplify(1e-6)


def _filter_proxy(d, thickness, front):
    # 外形占位；只画周边框与薄的滤料面，不计入打印件。
    size = d.filter_size
    border = 18.0
    rim = square(size, size) - square(size - 2 * border, size - 2 * border).move(
        x=border, y=border
    )
    proxy = rim.extrude(thickness) + square(size, size).extrude(0.6).move(
        z=thickness / 2
    )
    proxy = proxy.rotate(x=90).move(x=d.filter_clearance / 2, z=d.filter_clearance / 2)
    return proxy.move(
        y=d.filter_capture if front else d.depth - d.filter_capture + thickness
    )


def build_box(d=BoxDimensions()):
    """返回打印件、装配件、风扇占位/实心包络、逐盘布局；不导出文件。"""
    d.validate()
    parts, assembled = {}, {}
    fan_void = _fan_void(d)
    males = _corner_males(d)
    for wall in ("bottom", "left", "top", "right"):
        bounds = _bounds(wall, d)
        guides = _guides(d) if wall in ("bottom", "top") else None
        for i in range(len(bounds) - 1):
            name = f"{wall}_{i + 1}"
            part = _build_chunk(wall, i, bounds, d, fan_void, males, guides)
            if max(part.size().x, part.size().y) > d.bed_size:
                raise ValueError(f"{name} 超出预留后的可用打印平台")
            parts[name] = part.align(xmin=0, ymin=0, zmin=0)
            assembled[name] = _wall_to_world(part, wall, d)

    fan_blank = square(d.fan_size, d.fan_size, center=True).extrude(d.fan_thickness)
    airflow = cylinder(h=d.fan_thickness + 2, d=d.fan_opening, fn=128).move(z=-1)
    hub = cylinder(h=d.fan_thickness, d=38, fn=48)
    bridge = square(d.fan_size, 2, center=True).extrude(2)
    fan_proxy = fan_blank - airflow + hub + bridge + bridge.rotate(z=90)
    fans, fan_envelopes = {}, {}
    for wall in ("top", "right"):
        for i, center in enumerate(d.fan_centers_for(wall)):
            position = dict(x=center, y=d.depth / 2, z=d.thickness)
            name = f"{wall}_fan_{i + 1}"
            fans[name] = _wall_to_world(fan_proxy.move(**position), wall, d)
            fan_envelopes[name] = _wall_to_world(fan_blank.move(**position), wall, d)

    # 风扇板各占一盘；无风扇短板两件一盘，保持 240 mm 内的排版边距。
    blank_names = [
        name
        for wall in ("bottom", "left")
        for name in parts
        if name.startswith(f"{wall}_")
    ]
    plate_names = [
        tuple(blank_names[i : i + 2]) for i in range(0, len(blank_names), 2)
    ] + [
        (name,)
        for wall in ("right", "top")
        for name in parts
        if name.startswith(f"{wall}_")
    ]
    plates = []
    for names in plate_names:
        placed, cursor = [], 0.0
        for name in names:
            part = parts[name].move(x=cursor)
            placed.append(part)
            cursor += parts[name].size().x + d.bed_gap
        plate = union(placed)
        if max(plate.size().x, plate.size().y) > d.bed_size:
            raise ValueError("成对排盘超出预留后的可用平台")
        plates.append(plate)
    return parts, assembled, fans, fan_envelopes, plate_names, plates


dimensions = BoxDimensions()
_parts, _assembled, _fans, _fan_envelopes, print_plate_names, _plates = build_box(
    dimensions
)
globals().update(_parts)


def _preview_group(parts):
    # 保留装配件各自的网格，避免贴合面布尔合并产生极细碎三角形。
    vertices, triangles = [], []
    for part in parts:
        data = part.manifold.to_mesh64()
        offset = len(vertices)
        vertices.extend(data.vert_properties[:, :3])
        triangles.extend(data.tri_verts + offset)
    return mesh(vertices, triangles, merge=False)


show_frame = _preview_group(_assembled.values())
show_with_fans = _preview_group([show_frame, *_fans.values()])
show_filter_fit_1in = _preview_group(
    [
        show_with_fans,
        _filter_proxy(dimensions, 25.4, True),
        _filter_proxy(dimensions, 25.4, False),
    ]
)
show_filter_fit_2in = _preview_group(
    [
        show_with_fans,
        _filter_proxy(dimensions, 50.8, True),
        _filter_proxy(dimensions, 50.8, False),
    ]
)
for _i, _plate in enumerate(_plates, 1):
    globals()[f"show_print_plate_{_i:02d}"] = _plate


# 原独立 P14 单板演示，仅用于预览，不导出为正式打印件。
show_p14_plate = p14_cover()
show_p14_plate += dovetail_tabs(edge_length=140).move(x=70)
show_p14_plate -= dovetail_tabs(edge_length=140, thickness=7, clearance=0.2).move(
    x=-70, z=-1
)
show_connected_pair = show_p14_plate + show_p14_plate.move(x=140)


def _corner_brim_points(part, radius, spacing):
    """底面外环的四角各三点：角点及沿轮廓两侧各 spacing mm。"""
    contours = part.manifold.slice(part.bounding_box()[2]).to_polygons()

    # Manifold 外环逆时针、孔洞顺时针；选最大的外环，孔洞不参与布点。
    def area(poly):
        return (
            sum(
                poly[i - 1][0] * p[1] - p[0] * poly[i - 1][1]
                for i, p in enumerate(poly)
            )
            / 2
        )

    outer = max(contours, key=area)
    xmin, ymin, zmin, xmax, ymax, _ = part.bounding_box()

    def walk(index, direction):
        remaining = spacing
        point = tuple(outer[index])
        for _ in range(len(outer)):
            index = (index + direction) % len(outer)
            target = tuple(outer[index])
            length = math.dist(point, target)
            if length >= remaining and length > 0:
                return tuple(
                    a + (b - a) * remaining / length for a, b in zip(point, target)
                )
            remaining -= length
            point = target
        raise ValueError("Brim 点间距大于外轮廓周长")

    points = []
    for corner in ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)):
        index = min(range(len(outer)), key=lambda i: math.dist(outer[i], corner))
        for x, y in (walk(index, -1), outer[index], walk(index, 1)):
            points.append((float(x), float(y), zmin - 0.0001, radius))
    return points


def export_project_3mf(
    template,
    output,
    d=BoxDimensions(),
    filament=3,
    brim_radius=None,
    brim_spacing=5.5,
):
    """由模板复制完整打印配置，导出多盘项目；四角各三个局部 Brim 点。

    python air_purifier_box.py --template sample.3mf --output print.3mf
    可用 --filament / --brim-radius / --brim-spacing 调整；半径默认取模板。
    Brim 点使用居中网格的局部坐标，编号为 build 顺序号（从 1 开始）。
    耳朵由切片器生成，不合并进零件实体；导出后需重新切片。
    """
    import io
    import json
    from pathlib import Path
    import xml.etree.ElementTree as ET
    import zipfile

    from b4dcad import save_3mf

    template, output = Path(template).expanduser(), Path(output).expanduser()
    if template.resolve() == output.resolve():
        raise ValueError("输出路径不能覆盖模板")
    with zipfile.ZipFile(template) as source:
        settings = json.loads(source.read("Metadata/project_settings.config"))
        main = ET.fromstring(source.read("3D/3dmodel.model"))
        if brim_radius is None:
            lines = source.read("Metadata/brim_ear_points.txt").decode().splitlines()
            if not lines or lines[0] != "brim_points_format_version=0":
                raise ValueError(
                    "模板需有 version=0 的 Brim 点，或显式指定 brim_radius"
                )
            brim_radius = float(
                next(line.split("|", 1)[1] for line in lines if "|" in line).split()[3]
            )
        creality = source.read("Metadata/creality.config")
        types = source.read("[Content_Types].xml")
    if not 1 <= filament <= len(settings["filament_settings_id"]):
        raise ValueError("耗材编号超出模板耗材列表")
    if not all(math.isfinite(v) and v > 0 for v in (brim_radius, brim_spacing)):
        raise ValueError("Brim 半径、间距必须为有限正数")
    if brim_spacing >= 2 * brim_radius:
        raise ValueError("Brim 点间距需小于直径，保证三个耳朵相互重叠")
    settings["brim_type"] = "painted"
    parts, _, _, _, plate_names, _ = build_box(d)
    bed = [tuple(map(float, point.split("x"))) for point in settings["printable_area"]]
    bx0, by0 = min(p[0] for p in bed), min(p[1] for p in bed)
    bx1, by1 = max(p[0] for p in bed), max(p[1] for p in bed)
    if set(bed) != {(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)}:
        raise ValueError("当前布局需要矩形打印平台")
    bed_width, bed_depth = bx1 - bx0, by1 - by0
    columns = math.ceil(math.sqrt(len(plate_names)))
    # Creality PartPlateList：盘间距为平台尺寸的 1.2 倍，按行向 -Y 排列。
    gap = max(d.bed_gap, 2 * brim_radius + 1.0)
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    prod = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
    relns = "http://schemas.openxmlformats.org/package/2006/relationships"
    reltype = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
    ET.register_namespace("", ns)
    ET.register_namespace("p", prod)
    ET.register_namespace("BambuStudio", "http://schemas.bambulab.com/package/2021")

    def node(parent, tag, **attrs):
        return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})

    def meta(parent, key, value):
        return node(parent, "metadata", key=key, value=value)

    def xml(element):
        return ET.tostring(element, encoding="utf-8", xml_declaration=True)

    for tag in ("resources", "build"):
        main.remove(main.find(f"{{{ns}}}{tag}"))
    resources = node(main, f"{{{ns}}}resources")
    build = node(main, f"{{{ns}}}build")
    config = ET.Element("config")
    rels = ET.Element("Relationships", xmlns=relns)
    model_rels = ET.Element("Relationships", xmlns=relns)
    node(rels, "Relationship", Target="/3D/3dmodel.model", Id="rel-1", Type=reltype)
    ears = ["brim_points_format_version=0"]
    files = {}
    plate_elements = []
    serial = 0
    for plate_index, names in enumerate(plate_names):
        width = sum(parts[name].size().x for name in names) + gap * (len(names) - 1)
        depth = max(parts[name].size().y for name in names)
        # 整盘旋转 90°，与样例相同；连同耳朵外缘检查平台及相邻零件间距。
        if width > d.bed_size or depth > d.bed_size:
            raise ValueError(f"第 {plate_index + 1} 盘含 Brim 间距后超过可用平台")
        if depth + 2 * brim_radius > bed_width or width + 2 * brim_radius > bed_depth:
            raise ValueError(f"第 {plate_index + 1} 盘的 Brim 超出打印平台")
        if max(parts[name].size().z for name in names) > float(
            settings["printable_height"]
        ):
            raise ValueError("零件超出打印高度")
        ox = (plate_index % columns) * bed_width * 1.2
        oy = -(plate_index // columns) * bed_depth * 1.2
        plate = ET.Element("plate")
        meta(plate, "plater_id", plate_index + 1)
        meta(plate, "plater_name", ", ".join(names))
        meta(plate, "locked", "false")
        cursor = 0.0
        for name in names:
            serial += 1
            part = parts[name]
            sx, sy, sz = part.size().x, part.size().y, part.size().z
            cx, cy, cz = sx / 2, sy / 2, sz / 2
            mesh_id, object_id = 2 * serial - 1, 2 * serial
            path = f"3D/Objects/object_{serial}.model"
            with zipfile.ZipFile(
                io.BytesIO(save_3mf(None, [(name, part.move(x=-cx, y=-cy, z=-cz))]))
            ) as geometry:
                model = ET.fromstring(geometry.read("3D/3dmodel.model"))
            mesh_obj = model.find(f"{{{ns}}}resources/{{{ns}}}object")
            mesh_obj.set("id", str(mesh_id))
            model.remove(model.find(f"{{{ns}}}build"))
            files[path] = xml(model)
            obj = node(resources, f"{{{ns}}}object", id=object_id, type="model")
            components = node(obj, f"{{{ns}}}components")
            component = node(
                components,
                f"{{{ns}}}component",
                objectid=mesh_id,
                transform="1 0 0 0 1 0 0 0 1 0 0 0",
            )
            component.set(f"{{{prod}}}path", "/" + path)
            node(
                model_rels,
                "Relationship",
                Target="/" + path,
                Id=f"rel-{serial}",
                Type=reltype,
            )
            tx = ox + (bx0 + bx1) / 2 + depth / 2 - cy
            ty = oy + (by0 + by1) / 2 - width / 2 + cursor + cx
            node(
                build,
                f"{{{ns}}}item",
                objectid=object_id,
                printable=1,
                transform=f"0 1 0 -1 0 0 0 0 1 {tx:.9f} {ty:.9f} {cz:.9f}",
            )
            obj_settings = node(config, "object", id=object_id)
            meta(obj_settings, "name", name + ".stl")
            meta(obj_settings, "extruder", filament)
            part_settings = node(
                obj_settings, "part", id=mesh_id, subtype="normal_part"
            )
            meta(part_settings, "name", name + ".stl")
            meta(part_settings, "matrix", "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
            instance = node(plate, "model_instance")
            meta(instance, "object_id", object_id)
            meta(instance, "instance_id", 0)
            meta(instance, "identify_id", serial)
            points = _corner_brim_points(part, brim_radius, brim_spacing)
            values = " ".join(
                f"{v:.6f}" for x, y, z, r in points for v in (x - cx, y - cy, z - cz, r)
            )
            ears.append(f"object_id={serial}|{values}")
            cursor += sx + gap
        plate_elements.append(plate)
    config.extend(plate_elements)
    files.update(
        {
            "[Content_Types].xml": types,
            "_rels/.rels": xml(rels),
            "3D/3dmodel.model": xml(main),
            "3D/_rels/3dmodel.model.rels": xml(model_rels),
            "Metadata/model_settings.config": xml(config),
            "Metadata/project_settings.config": json.dumps(
                settings, ensure_ascii=False, indent=2
            ),
            "Metadata/brim_ear_points.txt": "\n".join(ears) + "\n",
            "Metadata/creality.config": creality,
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="导出净化器多盘 3MF 项目，四角各三个 Brim 点"
    )
    parser.add_argument(
        "--template", required=True, help="提供打印机、耗材和切片参数的样例 3MF"
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--filament", type=int, default=3)
    parser.add_argument("--brim-radius", type=float)
    parser.add_argument("--brim-spacing", type=float, default=5.5)
    args = parser.parse_args()
    print(
        export_project_3mf(
            args.template,
            args.output,
            filament=args.filament,
            brim_radius=args.brim_radius,
            brim_spacing=args.brim_spacing,
        )
    )
