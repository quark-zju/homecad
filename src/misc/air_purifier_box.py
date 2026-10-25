"""双滤网、六 P14 净化器。单位 mm，X/Z 为滤网面，Y 为箱体深度。

滤网放置净尺寸 496.2 方形，前后各容纳 15 mm 厚度，其余外露并用胶带封边。
默认外形 506.2×178.2×506.2；接头板厚 5，无风扇板中部 2，最高打印高度 13。
top/right 各三块风扇板，bottom/left 各五块短板；默认 16 件、11 盘，
按 240×240 可用平台预排。风扇和滤网均为 show_* 预览，不导出。
先拼合每面，再利用水平板的内向公榫侧滑装配竖板；内部倒角填胶密封。
最后封闭的侧面须同时对准上下母槽，沿 X 滑入，不可从 Z 方向硬压。
风扇固定通孔沿用 P14 盖板，紧固件另备；电源线孔需按线材密封。
止口内侧上沿的 V 缺口标记面别：bottom=1、left=2、top=3、right=4；
旁边圆弧缺口的数量为分件序号，与文件名后缀一致。前后止口重复同一标记，
不依赖观察方向；滤网接触面保持完整。mark_depth=0 可关闭标记。
风扇排向无风扇转角偏置；风扇外框到拼缝倒角边保留 sealant_land（默认 8）。
"""

from dataclasses import dataclass
import math

from b4dcad import cylinder, mesh, polygon, square, union

from air_purifier import _top_seam_chamfer, dovetail_tabs, p14_cover


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
    cable_hole: float = 10.0
    cable_height: float = 35.0
    bed_size: float = 240.0  # 260 平台主动留边。
    bed_gap: float = 8.0
    mark_depth: float = 0.8
    mark_width: float = 1.2

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
        if self.cable_height <= self.cable_hole / 2 + self.stop_width:
            raise ValueError("电源线孔离转角过近")
        if self.mark_depth:
            if self.mark_depth > self.stop_width - 0.5:
                raise ValueError("标记不能切穿止口，底部须保留至少 0.5 mm")
            if self.mark_width > self.stop_thickness - 0.5:
                raise ValueError("标记须保留至少 0.5 mm 完整滤网接触面")
            if self.mark_depth < 0.5 or self.mark_width < 0.5:
                raise ValueError("标记宽深至少为 0.5 mm，便于 FDM 打印识别")


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


def _part_marks(wall, index, start, end, d):
    """止口朝箱内的一侧切两组缺口：V 数量为面别，圆弧数量为序号。"""
    face = {"bottom": 1, "left": 2, "top": 3, "right": 4}[wall]
    radius, pitch, gap = d.mark_depth, 4 * d.mark_depth, 6.0
    length = (face + index - 1) * pitch + 4 * radius + gap
    if end - start < length + 8:
        raise ValueError("止口可用长度不足以容纳分件标记")
    first = (start + end - length) / 2 + radius
    second = first + (face - 1) * pitch + 2 * radius + gap
    height = d.thickness + d.stop_width
    triangle = (
        polygon(
            [
                (-radius - 0.05, height + 0.05),
                (radius + 0.05, height + 0.05),
                (0, height - radius),
            ]
        )
        .extrude(d.mark_width + 0.05)
        .rotate(x=90)
    )
    rounded = (
        cylinder(h=d.mark_width + 0.05, r=radius, fn=32).rotate(x=90).move(z=height)
    )
    marks = []
    for y in (
        d.filter_capture + d.stop_thickness + 0.05,
        d.depth - d.filter_capture - d.stop_thickness + d.mark_width,
    ):
        marks.extend(triangle.move(x=first + i * pitch, y=y) for i in range(face))
        marks.extend(rounded.move(x=second + i * pitch, y=y) for i in range(index + 1))
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
    if wall == "left" and d.cable_hole and start <= d.cable_height <= end:
        hole = cylinder(h=d.thickness + 2, d=d.cable_hole, fn=64).move(
            x=d.cable_height, y=d.depth / 2, z=-1
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
    fan_names = [name for name in parts if name.startswith(("top_", "right_"))]
    blank_names = [name for name in parts if name.startswith(("bottom_", "left_"))]
    plate_names = [(name,) for name in fan_names] + [
        tuple(blank_names[i : i + 2]) for i in range(0, len(blank_names), 2)
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
