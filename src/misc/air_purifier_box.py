"""双滤网、六 P14 净化器。单位 mm，X/Z 为滤网面，Y 为箱体深度。

V2 滤网放置净尺寸 503.2 方形（V1 +7），无需 padding；前后各容纳 15 mm，
其余厚度外露并用胶带封边。默认外形 513.2×212.2×513.2；接头板厚 5，
无风扇板中部 2，直角连接耳局部打印高度 25。V2 主板不与 V1 混装。
left/right 对侧各三块风扇板，bottom/top 各三块无风扇板；12 主板加 2 封口壳、13 盘，
按 240×240 可用平台预排。风扇和滤网均为 show_* 预览，不导出。
先拼合每面，再利用水平板的内向公榫侧滑装配竖板；内部倒角填胶密封。
最后封闭的侧面须同时对准上下母槽，沿 X 滑入，不可从 Z 方向硬压。
风扇固定通孔沿用 P14 盖板，紧固件另备；旧侧面电源孔默认关闭。
top_2 安装 45×45×16 控制器，28° 封口托座使电源端在外、风扇端在内。
按图片尺寸加单边 0.4 mm 余量；旋钮只作示意，让位按壳宽保守预留。
托座由两片侧卧打印的壳组成，局部打印高度 26.8；底壁、侧壁及风扇端框连续，
控制面和电源端敞开。底壁及端框外半厚搭接 1.5 mm，搭接胶缝 0.1。
顶板使用直边矩形孔，托座周圈留 0.3 mm 灌胶缝；封胶须覆盖两片搭接缝、
托座与顶板整圈以及控制器固定外壳周边，不能依赖打印配合本身气密。
两片托座共用四套 M3×8 固定到局部 3 mm 顶板，螺丝孔也需封胶，装前先试配。
controller=False 可关闭托座及开孔，controller_angle 控制倾角。
止口内侧上沿的长缺口标记面别：bottom=1、left=2、top=3、right=4；
旁边短缺口的数量为分件序号，与文件名后缀一致。长短默认 6/2，深 1.5。
两组之间留 8 mm 间隔；例如 top_2 为三个长缺口、两个短缺口。前后重复标记，
不依赖观察方向；滤网接触面保持完整。mark_depth=0 可关闭标记。
左右风扇排上下居中；风扇外框到拼缝倒角边保留 sealant_land（默认 8）。
每只风扇四边中部各有一条短限位，长 18、厚 2、高 4（滤网止口高度的一半），
外框单边余量 0.4；fan_locator_height 控制高度，fan_locator_width=0 关闭全部风扇限位。
前后侧沿 Y 各增加 17 mm 走线带，两侧螺丝结构对称，风扇和定位块居中。
前后滤网外缘在打印底面做 2 mm、45° 贴胶带倒角，保留 3 mm 厚端面。
水平板两个外端也延续侧板的贴胶带倒角，使前后四角的两条边都完整倒斜。
填胶斜面每约 8 mm 留宽 3、深 1 的横向 45° 抓槽；设 grip_depth=0 关闭。
每处抓槽另沿板厚 Z 做两级 0.5 mm 的 45° 凹口，经单边 1.2 mm 宽竖向通道
连通上方填胶口，最低保留 2.5 mm 实体；grip_z_depth=0 仅关闭这两级凹口。
直角公榫的入口单独朝榫顶设置，凹口顶面仍为打印方向的 45° 斜面。
填胶斜面及抓槽仅在两道滤网限位条之间；外伸滤网段和止口根部保持平直，
保留外侧贴胶带倒角、防翘槽及止口上的零件识别缺口。
八条平面拼缝、四个直角前后各一组 M3 连接耳，共 24 套，燕尾继续负责定位。
两耳各厚 2、间隔 0.2，配普通 5.5 对边/2.4 厚螺帽，建议 M3×8；M3×6 不足。
孔径 3.4，螺帽不埋入薄耳；预览包含头部和工具包络，装螺丝后再贴滤网。
平面耳根部直接贴合滤网止口，消除窄缝；孔位及工具包络均避开止口与风扇。
直角耳尖端削低 2 mm 成小平顶；两类连接耳外侧各有两条 1.2 mm 厚的斜坡筋，
避开中间螺丝及工具通道。bolt_rib_height=0 可关闭加强筋。
平面耳根部距滤网止口 0 mm；直角耳相对平面耳向箱内退 10 mm，侧筋伸出改为 2 mm，距滤网止口约 11.9 mm，
便于胶枪处理直角接缝；两耳厚度及 M3×8 规格不变。
水平板四角靠滤网止口的小定位三角撑为 10×10、厚 3 mm，尺寸由 gusset_leg/gusset_width 控制；
其范围按实际风扇端部余量校验，不随滤网止口高度限制。
防翘试验槽仅布置在板面四角，每角两条 45° 对角贯穿槽，燕尾附近不布槽。
槽宽 0.6、高 1，保留 0.2 首层；贯穿指连通相邻两条边，不沿板厚打穿。
默认两条斜线在相邻边上的截距为 12、24；孔口上方仍保留 0.4×0.4 退让斜坡。
设 edge_relief_height=0 关闭小槽，edge_relief_lip_chamfer=0 仅关闭孔口斜坡。
试印记录（2026-10-26）：bottom_1 使用当前角槽设计，无翘边；低温板温度
同时从 35°C 提高到 45°C，尚不能单独判断角槽与板温各自的效果。
试印记录（2026-10-27）：Brim 设为 0.15 mm 时仍可能黏住、不易拆除。
风扇板无 Brim 试印约 2 小时，无翘边；低温板 45°C 并涂胶水，PLA Plus
喷嘴 215°C，底面速度 40 mm/s。怀疑板温 45°C 是重要因素，模型小孔隙
也可能有帮助，尚未分别验证；此结果不代表所有板件均无需 Brim。
"""

from dataclasses import dataclass
import math

from b4dcad import circle, cylinder, loft, mesh, polygon, square, union


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
    filter_size: float = 500.126  # 19.69 inch 实际滤网边长。
    filter_clearance: float = 3.074  # 总余量，使净尺寸为 503.2（V1 +7）。
    filter_capture: float = 15.0
    stop_width: float = 8.0
    stop_thickness: float = 3.0
    fan_size: float = 140.2
    fan_thickness: float = 28.25
    fan_clearance: float = 1.0
    wiring_padding: float = 17.0
    rear_wiring_padding: float = 17.0
    corner_fan_clearance: float = 2.0
    sealant_land: float = 8.0
    fan_locator_clearance: float = 0.4
    fan_locator_width: float = 2.0  # 设为 0 关闭短定位块。
    fan_locator_length: float = 18.0
    fan_locator_height: float = 4.0
    thickness: float = 5.0
    web_thickness: float = 2.0  # 无风扇面中央薄壁，周边及接头仍为 5 mm。
    frame_width: float = 8.0
    hole_pitch: float = 125.0
    screw_hole: float = 4.3
    fan_opening: float = 134.2
    joint_clearance: float = 0.1
    joint_depth: float = 5.0
    chamfer: float = 0.8
    tape_chamfer: float = 2.0
    grip_depth: float = 1.0
    grip_width: float = 3.0
    grip_pitch: float = 8.0
    grip_z_depth: float = 0.5
    grip_z_channel: float = 1.2
    grip_z_levels: int = 2
    bolts: bool = True
    bolt_hole: float = 3.4
    bolt_ear: float = 2.0
    bolt_gap: float = 0.2
    bolt_length: float = 8.0
    bolt_nut_af: float = 5.5
    bolt_nut_height: float = 2.4
    bolt_head_diameter: float = 6.4
    bolt_head_height: float = 3.0
    bolt_tool_diameter: float = 7.0
    bolt_tip_cut: float = 2.0
    bolt_rib_width: float = 1.2
    bolt_rib_run: float = 4.0
    bolt_rib_height: float = 6.0
    bolt_inset: float = 6.0
    corner_bolt_setback: float = 10.0
    corner_bolt_rib_run: float = 2.0
    controller: bool = True
    controller_length: float = 45.0
    controller_width: float = 45.0
    controller_height: float = 16.0
    controller_clearance: float = 0.4
    controller_angle: float = 28.0
    controller_knob_height: float = 15.0
    controller_panel: float = 3.0
    controller_wall: float = 2.4
    controller_foot: float = 2.0
    controller_seal_gap: float = 0.3
    controller_lap: float = 1.5
    controller_fan_plug_width: float = 20.0
    controller_fan_plug_height: float = 12.0
    controller_fan_plug_length: float = 25.0
    controller_dc_plug_diameter: float = 12.0
    controller_dc_plug_length: float = 35.0
    gusset_leg: float = 10.0
    gusset_width: float = 3.0
    cable_hole: float = 0.0  # 旧侧面电源孔默认关闭，改用顶部控制器的电源接口。
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
    first_layer_height: float = 0.2
    edge_relief_width: float = 0.6
    edge_relief_height: float = 1.0
    edge_relief_lip_chamfer: float = 0.4
    corner_relief_offset: float = 12.0
    corner_relief_spacing: float = 12.0
    corner_relief_count: int = 2
    edge_relief_hole_guard: float = 0.8

    @property
    def span(self):
        return self.filter_size + self.filter_clearance

    @property
    def depth(self):
        return (
            self.fan_size
            + 2 * (self.filter_capture + self.stop_thickness + self.fan_clearance)
            + self.wiring_padding
            + self.rear_wiring_padding
        )

    @property
    def fan_center_y(self):
        return (
            self.filter_capture
            + self.stop_thickness
            + self.fan_clearance
            + self.wiring_padding
            + self.fan_size / 2
        )

    @property
    def fan_centers(self):
        """对侧各三只风扇，上下等距居中；不再需要相邻风扇转角的偏置。"""
        pitch = self.fan_size + 2 * (self.sealant_land + self.chamfer)
        middle = self.span / 2
        return (middle - pitch, middle, middle + pitch)

    def fan_centers_for(self, wall):
        # 右面打印坐标 U 与装配后的 Z 相反，两侧风扇保持同高。
        if wall == "right":
            return tuple(self.span - center for center in reversed(self.fan_centers))
        return self.fan_centers

    @property
    def controller_min_angle(self):
        diagonal = math.hypot(self.controller_length, self.controller_height)
        ratio = (self.thickness + 1) / diagonal
        if ratio >= 1:
            raise ValueError("控制器尺寸不足以跨过板厚和接口余量")
        return math.degrees(
            math.atan2(self.controller_height, self.controller_length)
            + math.asin(ratio)
        )

    @property
    def blank_segments(self):
        usable = self.bed_size - self.joint_depth
        return math.ceil((self.span + 2 * self.thickness) / usable)

    def validate(self):
        nonnegative = {
            "filter_clearance",
            "fan_clearance",
            "wiring_padding",
            "rear_wiring_padding",
            "corner_fan_clearance",
            "joint_clearance",
            "chamfer",
            "tape_chamfer",
            "grip_depth",
            "grip_z_depth",
            "bolts",
            "bolt_tip_cut",
            "bolt_rib_height",
            "corner_bolt_setback",
            "controller",
            "gusset_leg",
            "cable_hole",
            "mark_depth",
            "fan_locator_clearance",
            "fan_locator_width",
            "edge_relief_height",
            "edge_relief_lip_chamfer",
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
        if self.tape_chamfer > self.thickness - 0.5:
            raise ValueError("贴胶带倒角后端面须保留至少 0.5 mm 厚度")
        if self.tape_chamfer >= self.filter_capture:
            raise ValueError("贴胶带倒角不能切到滤网限位条")
        if self.grip_depth + self.chamfer > self.thickness - 1.0:
            raise ValueError("填胶抓槽底下须保留至少 1 mm 实体")
        if self.grip_width < 0.5 or self.grip_pitch < self.grip_width + 1:
            raise ValueError("抓槽宽度至少 0.5 mm，槽间实体至少 1 mm")
        if (
            not isinstance(self.grip_z_levels, int)
            or isinstance(self.grip_z_levels, bool)
            or self.grip_z_levels < 1
        ):
            raise ValueError("Z 向抓槽级数必须为正整数")
        if _grip_floor(self) < 1:
            raise ValueError("Z 向抓槽底部须保留至少 1 mm 实体")
        if self.grip_z_channel + self.grip_z_depth > self.thickness - 1:
            raise ValueError("Z 向胶道及凹口过深，侧面须保留至少 1 mm 实体")
        if self.bolts:
            if self.bolt_ear < 2 or self.bolt_hole < 3.2:
                raise ValueError("M3 连接耳厚至少 2 mm，通孔至少 3.2 mm")
            if (
                self.bolt_length
                < 2 * self.bolt_ear + self.bolt_gap + self.bolt_nut_height + 0.5
            ):
                raise ValueError("螺丝须穿过两耳、间隔及完整螺帽，另留至少 0.5 mm")
            # 耳片、侧筋及紧固件均留在风扇外框之间的拼缝余量中。
            # 默认耳根贴止口；增大 bolt_inset 时仍需检查工具是否伸入风扇区。
            if (
                self.bolt_inset + 6.5
                >= (self.depth - 2 * (self.filter_capture + self.stop_thickness)) / 2
            ):
                raise ValueError("前后平面连接耳过于接近")
            fastener_reach = (
                self.bolt_ear
                + self.bolt_gap / 2
                + max(
                    self.bolt_rib_run,
                    self.bolt_nut_height,
                    self.bolt_head_height,
                    self.bolt_length - 2 * self.bolt_ear - self.bolt_gap,
                )
            )
            if self.sealant_land + self.chamfer < fastener_reach + 0.5:
                raise ValueError("拼缝到风扇外框的余量不足以容纳连接耳、侧筋及紧固件")
            if max(self.bolt_head_diameter, self.bolt_tool_diameter, 9) > 9.5:
                raise ValueError("螺丝头或工具过大，会碰到板面；请重新调整耳孔高度")
            c = _bolt_corner_height(self)
            reach = _corner_bolt_reach(self)
            cap = c + 10 - self.bolt_tip_cut
            half = c * self.bolt_tip_cut / (c + 10)
            safe = self.fan_centers[0] - self.fan_size / 2 - self.corner_fan_clearance
            distance = (cap * (reach - c) - c * (reach - c - half)) / math.hypot(
                cap, reach - c - half
            )
            if (
                cap > safe
                or distance
                < max(self.bolt_head_diameter / 2, self.bolt_hole / math.sqrt(2)) + 0.5
            ):
                raise ValueError("风扇间距不足以容纳直角耳及孔周实体")
            if (
                _corner_bolt_y(self)
                + self.bolt_ear
                + self.bolt_gap / 2
                + self.corner_bolt_rib_run
                + 1
                >= self.depth / 2
            ):
                raise ValueError("前后直角耳过于接近")
            if self.bolt_tip_cut > 10 - max(4.5, self.bolt_head_diameter / 2) - 1:
                raise ValueError("耳尖削除过多，螺孔与平顶之间须保留实体")
            if self.bolt_rib_height:
                c = _bolt_corner_height(self)
                available = (c + 10) * (5 - self.bolt_rib_width / 2) / c
                if not 0.5 <= self.bolt_rib_width <= 1.5:
                    raise ValueError("筋厚须在 0.5–1.5 mm 内，避免挡住螺帽工具")
                if self.bolt_rib_height > min(8, available - 0.5):
                    raise ValueError("加强筋过高，无法与耳侧保持足够接触")
                if c - 5 - self.bolt_rib_width / 2 <= 4.5:
                    raise ValueError("直角耳侧筋过于接近螺帽及工具通道")
                if (
                    self.bolt_ear + self.bolt_gap / 2 + self.bolt_rib_run
                    > self.frame_width - 0.5
                ):
                    raise ValueError("加强筋伸出加强边框，请减小 bolt_rib_run")
        if not 0.5 <= self.web_thickness <= self.thickness:
            raise ValueError("中央薄壁必须至少 0.5 mm，且不大于接头板厚")
        if self.controller:
            angle = math.radians(self.controller_angle)
            drop = self.controller_length * math.sin(
                angle
            ) - self.controller_height * math.cos(angle)
            if not 0 < self.controller_angle < 60 or drop < self.thickness + 1:
                raise ValueError(
                    f"控制器需至少约 {self.controller_min_angle:.1f}° 才能保守分隔两端面，且须小于 60°"
                )
            if not self.web_thickness <= self.controller_panel <= self.thickness:
                raise ValueError("控制器安装区厚度须介于中央薄壁与板厚之间")
            if (
                self.bolt_length
                < self.controller_panel
                + self.controller_foot
                + self.bolt_nut_height
                + 0.5
            ):
                raise ValueError("控制器托架固定螺丝不足以穿过顶板、脚和完整螺帽")
            if self.controller_wall < 2.2 or self.controller_foot < 1.5:
                raise ValueError(
                    "封口壳壁须至少 2.2 mm、脚至少 1.5 mm，搭接后保留至少 1 mm"
                )
            if not 0.1 <= self.controller_seal_gap <= 0.6:
                raise ValueError("控制器封口配合间隙须在 0.1–0.6 mm")
            if not 0.5 <= self.controller_lap <= self.controller_width / 4:
                raise ValueError("两片封口搭接长度须在 0.5 mm 与壳宽四分之一之间")
            if (
                self.controller_fan_plug_width
                >= self.controller_width - 2 * self.controller_wall
            ):
                raise ValueError("风扇插头包络过宽，须保留两侧封口壁")
            mount_width = self.controller_length + self.controller_height + 24
            if (
                mount_width
                >= (self.span + 2 * self.thickness) / self.blank_segments
                - 2 * self.frame_width
            ):
                raise ValueError("控制器安装区越过 top_2 的接头边框")
            if self.controller_width + 2 * (
                self.controller_clearance + self.controller_wall + 3
            ) >= self.depth - 2 * (self.filter_capture + self.stop_thickness):
                raise ValueError("控制器安装区过宽，会碰到滤网限位条")
        free_end = self.fan_centers[0] - self.fan_size / 2
        required = (
            max(self.stop_width, self.gusset_leg + self.joint_clearance)
            + self.corner_fan_clearance
        )
        if free_end < required:
            raise ValueError(
                "三个风扇、转角避让及填胶余量无法同时容纳；请减小 sealant_land 或增大滤网边长"
            )
        if self.bed_size <= self.joint_depth:
            raise ValueError("可用平台太小")
        if self.cable_hole and not (
            self.stop_width + self.cable_hole_height / 2
            < self.cable_height
            < self.span - self.stop_width - self.cable_hole_height / 2
        ):
            raise ValueError("电源线孔离转角过近")
        if self.cable_hole and any(
            abs(self.cable_height - center)
            < (self.cable_hole_height + self.fan_size) / 2
            for center in self.fan_centers_for("left")
        ):
            raise ValueError("侧面电源孔与左侧风扇重叠；请关闭该孔或移到风扇间隙")
        if self.fan_locator_width:
            if self.fan_locator_width < 0.5 or self.fan_locator_length < 2:
                raise ValueError("风扇定位块壁厚至少 0.5 mm，长度至少 2 mm")
            if self.fan_locator_height < 0.5:
                raise ValueError("风扇限位高度至少 0.5 mm")
            if (
                self.fan_locator_clearance + self.fan_locator_width + 0.5
                > self.fan_clearance
                + min(self.wiring_padding, self.rear_wiring_padding)
            ):
                raise ValueError("新增风扇侧限位到滤网止口须留至少 0.5 mm")
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
        if self.edge_relief_height:
            if (
                not isinstance(self.corner_relief_count, int)
                or isinstance(self.corner_relief_count, bool)
                or self.corner_relief_count < 1
            ):
                raise ValueError("每角槽数必须为正整数")
            top = (
                self.first_layer_height
                + self.edge_relief_height
                + self.edge_relief_lip_chamfer
            )
            if top > self.thickness - 0.5:
                raise ValueError("角槽上方须保留至少 0.5 mm 实体")
            reach = (
                self.corner_relief_offset
                + (self.corner_relief_count - 1) * self.corner_relief_spacing
            )
            keep = (
                self.filter_capture
                + self.stop_thickness
                + self.fan_clearance
                + self.gusset_width
            )
            if reach + self.edge_relief_width >= self.frame_width + keep:
                raise ValueError("角槽越过厚边框，会削弱中部薄壁；请缩小角槽范围")
            protected_y = (
                self.depth / 4
                - 4
                - max(self.thickness, self.joint_depth) * math.tan(math.radians(30))
                - 2 * self.joint_clearance
            )
            if (
                reach + self.edge_relief_width + self.edge_relief_lip_chamfer
                >= protected_y
            ):
                raise ValueError("角槽靠近燕尾，须缩小角槽范围")


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


def _world_to_wall(part, wall, d):
    if wall == "bottom":
        return part.move(z=d.thickness)
    if wall == "top":
        return part.move(y=-d.depth, z=-d.span - d.thickness).rotate(x=180)
    if wall == "left":
        return part.move(x=d.thickness, y=-d.depth).rotate(y=90).rotate(x=180)
    return (
        part.move(x=-d.span - d.thickness, y=-d.depth, z=-d.span)
        .rotate(z=180)
        .rotate(y=-90)
    )


def _bolt_y(d):
    return d.filter_capture + d.stop_thickness + d.bolt_inset


def _corner_bolt_y(d):
    return _bolt_y(d) + d.corner_bolt_setback


def _grip_floor(d):
    floor = d.thickness - d.chamfer
    if d.chamfer and d.grip_depth:
        floor -= d.grip_depth
        if d.grip_z_depth:
            floor = min(floor, d.thickness - (2 * d.grip_z_levels + 1) * d.grip_z_depth)
    return floor


def _bolt_corner_height(d):
    return d.stop_width + d.bolt_tool_diameter / 2 + 0.5


def _corner_bolt_reach(d):
    return min(
        2 * _bolt_corner_height(d),
        d.fan_centers[0] - d.fan_size / 2 - d.corner_fan_clearance,
    )


def _flat_bolt_ear(edge, male_side, d):
    """平面拼缝的配对立耳；孔顶做 45° 尖顶，侧卧孔无需平顶支撑。"""
    y, z = _bolt_y(d), d.thickness + 5
    r = d.bolt_hole / 2
    shape = polygon(
        [
            (y - 6, _grip_floor(d) - 0.4),
            (y + 6, _grip_floor(d) - 0.4),
            (y + 6, d.thickness + 8),
            (y + 5, d.thickness + 9),
            (y - 5, d.thickness + 9),
            (y - 6, d.thickness + 8),
        ]
    )
    bore = circle(r=r, fn=48).move(x=y, y=z) + polygon(
        [
            (y - r / math.sqrt(2), z + r / math.sqrt(2)),
            (y + r / math.sqrt(2), z + r / math.sqrt(2)),
            (y, z + r * math.sqrt(2)),
        ]
    )
    x = edge - d.bolt_gap / 2 - d.bolt_ear if male_side else edge + d.bolt_gap / 2
    ear = (shape - bore).extrude(d.bolt_ear).rotate(x=90).rotate(z=90).move(x=x)
    if d.bolt_rib_height:
        side = x if male_side else x + d.bolt_ear
        rib = (
            polygon(
                [
                    (-0.2, d.thickness - 0.4),
                    (d.bolt_rib_run, d.thickness - 0.4),
                    (-0.2, d.thickness + d.bolt_rib_height),
                ]
            )
            .extrude(d.bolt_rib_width)
            .rotate(x=90)
        )
        if male_side:
            rib = rib.mirror(x=1)
        for offset in (-5.3, 5.3):
            ear += rib.move(x=side, y=y + offset + d.bolt_rib_width / 2)
    return ear + ear.mirror(y=1).move(y=d.depth)


def _corner_bolt_ear(wall, left, top, d):
    """直角两耳分别连到水平/竖板，沿 Y 穿短螺丝；根部下伸至薄板实体。"""
    h, c = d.span, _bolt_corner_height(d)
    horizontal = wall in ("bottom", "top")
    root = max(
        d.thickness - d.web_thickness + 0.4 if wall in ("bottom", "top") else 0.4,
        d.thickness - _grip_floor(d) + 0.4,
    )
    cap = c + 10 - d.bolt_tip_cut
    half = c * d.bolt_tip_cut / (c + 10)
    reach = _corner_bolt_reach(d)
    if horizontal:
        shape = polygon(
            [
                (h - reach, -root),
                (h, -root),
                (h, 0),
                (h - c + half, cap),
                (h - c - half, cap),
                (h - reach, 0),
            ]
        )
    else:
        shape = polygon(
            [
                (h + root, 0),
                (h + root, reach),
                (h, reach),
                (h - cap, c + half),
                (h - cap, c - half),
                (h, 0),
            ]
        )
    # 对两个零件的打印法向都呈 45° 孔顶，圆孔所需的圆截面包含在菱形内。
    r = d.bolt_hole / math.sqrt(2)
    bore = polygon([(h - c - r, c), (h - c, c - r), (h - c + r, c), (h - c, c + r)])
    cy = d.depth - _corner_bolt_y(d)
    yend = cy + d.bolt_gap / 2 + d.bolt_ear if horizontal else cy - d.bolt_gap / 2
    ear = (shape - bore).extrude(d.bolt_ear).rotate(x=90).move(y=yend)
    if d.bolt_rib_height:
        rib = polygon(
            [(-0.2, -root), (d.corner_bolt_rib_run, -root), (-0.2, d.bolt_rib_height)]
        )
        rib = rib.extrude(d.bolt_rib_width).rotate(x=90).rotate(z=90)
        for offset in (5 - c, reach - 5 - c):
            brace = rib.move(
                x=h - c + offset - d.bolt_rib_width / 2,
                y=cy + d.bolt_gap / 2 + d.bolt_ear,
            )
            if not horizontal:
                brace = (
                    brace.rotate(y=90).mirror(x=1).mirror(y=1).move(x=h, y=2 * cy, z=h)
                )
            ear += brace
    ear += ear.mirror(y=1).move(y=d.depth)
    if left:
        ear = ear.mirror(x=1).move(x=h)
    if top:
        ear = ear.mirror(z=1).move(z=h)
    return _world_to_wall(ear, wall, d)


def _bolt_pack(d, origin, axis, grip=None):
    """保守头部包络、普通六角螺帽和直线工具通道；均只作预览/避让验证。"""
    grip = 2 * d.bolt_ear + d.bolt_gap if grip is None else grip
    far = tuple(o + a * grip for o, a in zip(origin, axis))
    reverse = tuple(-a for a in axis)
    shaft = cylinder(h=d.bolt_length, d=3, fn=48).orient(axis, origin=origin)
    head = cylinder(h=d.bolt_head_height, d=d.bolt_head_diameter, fn=48).orient(
        reverse, origin=origin
    )
    radius = d.bolt_nut_af / math.sqrt(3)
    nut = polygon(
        [
            (radius * math.cos(i * math.pi / 3), radius * math.sin(i * math.pi / 3))
            for i in range(6)
        ]
    ).extrude(d.bolt_nut_height)
    nut -= cylinder(h=d.bolt_nut_height, d=d.bolt_hole, fn=48)
    nut = nut.orient(axis, origin=far)
    driver_start = tuple(o - a * d.bolt_head_height for o, a in zip(origin, axis))
    nut_start = tuple(o + a * d.bolt_nut_height for o, a in zip(far, axis))
    driver = cylinder(h=20, d=d.bolt_tool_diameter, fn=48).orient(
        reverse, origin=driver_start
    )
    wrench = cylinder(h=5, d=9, fn=48).orient(axis, origin=nut_start)
    return head + shaft + nut, driver + wrench


def _controller_mount(d):
    """返回直边开孔、两片搭接封口壳和控制器占位；先用 top 的打印坐标。"""
    if not d.controller:
        return None
    l, w, h = d.controller_length, d.controller_width, d.controller_height
    gap, wall = d.controller_clearance, d.controller_wall
    cx, cy = d.span / 2, d.depth / 2
    base = d.controller_panel

    def local(part):
        return part.rotate(x=180).rotate(y=-d.controller_angle).move(z=base / 2)

    def located(part):
        return part.move(x=cx, y=cy)

    shell = square(l, w, center=True).extrude(h).move(z=-h / 2 - gap)
    # 旋钮实际直径未知；预览取 30 mm，碰撞检查按整个壳宽预留。
    knob = cylinder(h=d.controller_knob_height, d=min(30, w), fn=64).move(z=h / 2 - gap)
    body = local(shell + knob)
    dc = cylinder(
        h=d.controller_dc_plug_length, d=d.controller_dc_plug_diameter, fn=48
    ).orient((-1, 0, 0), origin=(-l / 2, 0, -gap))
    fan = (
        square(d.controller_fan_plug_length, d.controller_fan_plug_width)
        .move(x=l / 2, y=-d.controller_fan_plug_width / 2)
        .extrude(d.controller_fan_plug_height)
        .move(z=-d.controller_fan_plug_height / 2 - gap)
    )
    ports = local(dc + fan)
    clearance = local(
        square(l + 2 * gap, w + 2 * gap, center=True)
        .extrude(h + 2 * gap)
        .move(z=-h / 2 - gap)
    )
    knob_keep = local(
        cylinder(h=d.controller_knob_height + 2 * gap, d=w + 2 * gap, fn=64).move(
            z=h / 2 - gap
        )
    )
    # 开孔与封口外壁保持恒定灌胶间隙；不再用旋钮的圆形包络切顶板。
    angle = math.radians(d.controller_angle)
    inner, outer = w / 2 + gap, w / 2 + gap + wall
    clip_x = outer / math.cos(angle) + base / 2 * math.tan(angle)
    opening = square(
        2 * (clip_x + d.controller_seal_gap),
        2 * (outer + d.controller_seal_gap),
        center=True,
    )
    # 固定孔距不随倾角变化；两端脚留在板内侧，主体从直边开孔伸出。
    screw_x = (l + h) / 2 + 4
    extent = screw_x + 6
    foot_inner = inner - 8
    screw_y = -(inner - 4.5)
    profile = (
        (
            clearance.rotate(x=-90).project()
            + square(2 * clip_x, base + d.controller_foot + 0.5).move(x=-clip_x, y=-0.5)
        )
        .hull()
        .offset(wall, "miter")
    )
    profile &= square(2 * clip_x, 4 * (l + h)).move(x=-clip_x, y=-2 * (l + h))
    housing = profile.extrude(2 * outer).rotate(x=90).move(y=outer)
    # 上方及电源端敞开便于滑入；其余外壳、底壁与风扇端框形成封胶托座。
    trough = local(
        square(4 * (l + h), 2 * inner)
        .move(x=l / 2 + gap - 4 * (l + h), y=-inner)
        .extrude(4 * (l + h))
        .move(z=-h / 2 - gap)
    )
    housing -= trough + local(
        square(
            d.controller_fan_plug_length + wall + 1, d.controller_fan_plug_width + 0.2
        )
        .move(x=l / 2, y=-d.controller_fan_plug_width / 2 - 0.1)
        .extrude(d.controller_fan_plug_height + 0.2)
        .move(z=-d.controller_fan_plug_height / 2 - gap - 0.1)
    )
    big = 4 * (l + w + h)

    def halfspace(y0, y1):
        return square(2 * big, y1 - y0).move(x=-big, y=y0).extrude(2 * big).move(z=-big)

    def lap_region(clearance=0):
        floor = (
            square(2 * big, 2 * big, center=True)
            .extrude(big - h / 2 - gap - wall / 2 + clearance)
            .move(z=-big)
        )
        end = (
            square(big, 2 * big)
            .move(x=l / 2 + gap + wall / 2 - clearance, y=-big)
            .extrude(2 * big)
            .move(z=-big)
        )
        return local(floor + end)

    # 在底壁及端壁的外半厚做搭接；保留内半厚，搭接处留 0.1 mm 胶缝。
    rail = housing & (
        halfspace(-big, -0.1) + (halfspace(-0.2, d.controller_lap) & lap_region())
    )
    other = (housing & halfspace(0.1, big)) - (
        halfspace(-big, d.controller_lap + 0.1) & lap_region(0.1)
    )
    holes = []
    for x in (-screw_x, screw_x):
        foot = (
            square(12, outer - foot_inner)
            .move(x=x - 6, y=-outer)
            .extrude(d.controller_foot)
            .move(z=base)
        )
        bore = cylinder(
            h=d.thickness + d.controller_foot + 2, d=d.bolt_hole, fn=48
        ).move(x=x, y=screw_y, z=-1)
        r = d.bolt_hole / 2
        roof = (
            polygon(
                [
                    (x - r / math.sqrt(2), screw_y + r / math.sqrt(2)),
                    (x + r / math.sqrt(2), screw_y + r / math.sqrt(2)),
                    (x, screw_y + r * math.sqrt(2)),
                ]
            )
            .extrude(d.thickness + d.controller_foot + 2)
            .move(z=-1)
        )
        rail = (rail + foot) - bore - roof
        other = (other + foot.mirror(y=1)) - (bore + roof).mirror(y=1)
        holes.append(bore)
    rails = {
        "controller_shell_a": located(rail),
        "controller_shell_b": located(other),
    }
    patch = square(2 * extent + 4, 2 * (outer + 3), center=True).extrude(base)
    cut = (
        opening.extrude(d.thickness + 2).move(z=-1)
        + union(holes)
        + union(p.mirror(y=1) for p in holes)
    )
    hardware, tools = {}, {}
    for x in (-screw_x, screw_x):
        for y in (screw_y, -screw_y):
            name = f"controller_mount_{len(hardware)+1}"
            bolt, tool = _bolt_pack(
                d,
                (cx + x, cy + y, base + d.controller_foot),
                (0, 0, -1),
                grip=base + d.controller_foot,
            )
            hardware[name] = _wall_to_world(bolt, "top", d)
            tools[name] = _wall_to_world(tool, "top", d)
    return {
        "patch": located(patch),
        "cut": located(cut),
        "rails": rails,
        "body": located(body),
        "clearance": located(clearance + knob_keep),
        "ports": located(ports),
        "hardware": hardware,
        "tools": tools,
    }


def bolt_hardware(d=BoxDimensions()):
    hardware, tools = {}, {}
    if not d.bolts:
        controller = _controller_mount(d)
        return (
            (controller["hardware"], controller["tools"])
            if controller
            else (hardware, tools)
        )

    def pair(name, bolt, tool):
        hardware[name], tools[name] = bolt, tool
        hardware[name + "_opposite"] = bolt.mirror(y=1).move(y=d.depth)
        tools[name + "_opposite"] = tool.mirror(y=1).move(y=d.depth)

    half = d.bolt_ear + d.bolt_gap / 2
    for wall in ("bottom", "left", "top", "right"):
        for i, edge in enumerate(_bounds(wall, d)[1:-1], 1):
            name = f"{wall}_seam_{i}"
            bolt, tool = _bolt_pack(
                d, (edge - half, _bolt_y(d), d.thickness + 5), (1, 0, 0)
            )
            pair(name, _wall_to_world(bolt, wall, d), _wall_to_world(tool, wall, d))
    c = _bolt_corner_height(d)
    for left in (False, True):
        for top in (False, True):
            x, z = (c if left else d.span - c), (d.span - c if top else c)
            name = f"corner_{'left' if left else 'right'}_{'top' if top else 'bottom'}"
            pair(
                name,
                *_bolt_pack(d, (x, d.depth - _corner_bolt_y(d) + half, z), (0, -1, 0)),
            )
    controller = _controller_mount(d)
    if controller:
        hardware.update(controller["hardware"])
        tools.update(controller["tools"])
    return hardware, tools


def _corner_males(d):
    tabs = _tabs(d, depth=d.thickness)
    if d.chamfer:
        tabs = union(
            _top_seam_chamfer(tab, tab.project(), d.thickness, d.chamfer)
            # 埋入板内的榫根边不作凹口，避免形成胶无法进入的封闭内腔。
            - _sealant_grip_cutter(tab.project(), d, lambda x, y: x >= 0, z_grips=False)
            for tab in tabs.decompose()
        )
    right = tabs.rotate(y=-90).move(x=d.span + d.thickness, z=d.thickness)
    if d.chamfer and d.grip_depth and d.grip_z_depth:
        # 公榫已转为朝上；在实际打印 Z 方向另开入口，不能旋转带闭合屋顶的槽。
        # 上入口稍宽于横槽，避免两个切口的侧壁恰好共面。
        port_width = d.grip_width + 0.2
        cutter = _z_grip_profile(d).extrude(port_width).rotate(x=90)
        for y in (d.depth / 4, 3 * d.depth / 4):
            right -= cutter.move(x=d.span, y=y + port_width / 2, z=d.thickness)
    return right, right.mirror(x=1).move(x=d.span)


def _bounds(wall, d):
    horizontal = wall in ("bottom", "top")
    start, end = (-d.thickness, d.span + d.thickness) if horizontal else (0, d.span)
    if wall in ("left", "right"):
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
            d.filter_capture + d.stop_thickness + d.gusset_width,
            d.depth - d.filter_capture - d.stop_thickness,
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
    """四边中部的低矮短限位；外框单边留余量，避开角部固定孔。"""
    edge = d.fan_size / 2 + d.fan_locator_clearance
    length, width = d.fan_locator_length, d.fan_locator_width
    footprint = union(
        square(width, length).move(x=x, y=d.fan_center_y - length / 2)
        for x in (center - edge - width, center + edge)
    ) + union(
        square(length, width).move(x=center - length / 2, y=y)
        for y in (d.fan_center_y - edge - width, d.fan_center_y + edge)
    )
    return footprint.extrude(d.fan_locator_height).move(z=d.thickness)


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


def _contour_area(poly):
    return (
        sum(
            poly[i - 1][0] * point[1] - point[0] * poly[i - 1][1]
            for i, point in enumerate(poly)
        )
        / 2
    )


def _corner_relief_cutter(part, start, end, d):
    """四角斜槽连通相邻两条外边，避开燕尾、薄壁和孔群；首层不切。"""
    reach = (
        d.corner_relief_offset + (d.corner_relief_count - 1) * d.corner_relief_spacing
    )
    if reach + d.edge_relief_width >= min(end - start, d.depth) / 2:
        raise ValueError("零件过小，相邻角槽会互相接近")
    bands = []
    half = d.edge_relief_width / 2
    margin = d.edge_relief_width + 0.1
    for x, sx in ((start, 1), (end, -1)):
        for y, sy in ((0, 1), (d.depth, -1)):
            for i in range(d.corner_relief_count):
                distance = d.corner_relief_offset + i * d.corner_relief_spacing
                a = (x + sx * distance, y)
                b = (x, y + sy * distance)
                length = math.dist(a, b)
                tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
                nx, ny = -ty, tx
                bands.append(
                    polygon(
                        [
                            (
                                a[0] - margin * tx - half * nx,
                                a[1] - margin * ty - half * ny,
                            ),
                            (
                                b[0] + margin * tx - half * nx,
                                b[1] + margin * ty - half * ny,
                            ),
                            (
                                b[0] + margin * tx + half * nx,
                                b[1] + margin * ty + half * ny,
                            ),
                            (
                                a[0] - margin * tx + half * nx,
                                a[1] - margin * ty + half * ny,
                            ),
                        ]
                    )
                )
    footprint = union(bands)
    slots = footprint.extrude(d.edge_relief_height)
    if d.edge_relief_lip_chamfer:
        # 两个出口各自按板边法向退让；不把斜槽的整段平顶改成三角形。
        h, c = d.edge_relief_height, d.edge_relief_lip_chamfer
        profile = polygon([(-0.05, h), (c, h), (-0.05, h + c + 0.05)])
        edges = []
        for x, y, nx, ny, length in (
            (start - 1, 0, 0, 1, end - start + 2),
            (end + 1, d.depth, 0, -1, end - start + 2),
            (start, d.depth + 1, 1, 0, d.depth + 2),
            (end, -1, -1, 0, d.depth + 2),
        ):
            edges.append(
                profile.extrude(length)
                .rotate(x=90)
                .rotate(z=math.degrees(math.atan2(ny, nx)))
                .move(x=x, y=y)
            )
        slots += union(edges) & footprint.extrude(h + c + 0.05)
    level = d.first_layer_height + d.edge_relief_height / 2
    contours = part.section(
        normal=(0, 0, 1), origin=(0, 0, level)
    ).cross_section.to_polygons()
    holes = [
        polygon(poly).offset(d.edge_relief_hole_guard)
        for poly in contours
        if _contour_area(poly) < 0
    ]
    if holes:
        slots -= union(holes).extrude(
            d.edge_relief_height + d.edge_relief_lip_chamfer + 0.05
        )
    return slots.move(z=d.first_layer_height)


def _z_grip_profile(d):
    """法向 U / 打印 Z 截面：上开口通道连通两级 V 槽，保留 45° 槽顶。"""
    step, t = d.grip_z_depth, d.thickness
    top = t - step
    bottom = top - 2 * d.grip_z_levels * step
    width = d.grip_z_channel
    channel = square(width + 0.1, t + 0.1 - bottom).move(x=-0.1, y=bottom)
    for level in range(d.grip_z_levels):
        z = top - (2 * level + 1) * step
        channel += polygon([(width, z - step), (width + step, z), (width, z + step)])
    return channel


def _sealant_grip_cutter(profile, d, eligible, z_grips=True):
    """横向短槽保留；板厚方向的两级凹口连通上口，凹口顶面为 45°。"""
    if not d.grip_depth or not d.chamfer:
        return square(1, 1).extrude(1).move(z=-10)
    cuts = []
    c, g, t = d.chamfer, d.grip_depth, d.thickness
    tooth = polygon([(-0.1, t + 0.1), (-0.1, t - c - g - 0.1), (c + g + 0.1, t + 0.1)])
    if z_grips and d.grip_z_depth:
        tooth += _z_grip_profile(d)
    for contour in profile.cross_section.to_polygons():
        if _contour_area(contour) <= 0:
            continue
        for a, b in zip(contour, list(contour[1:]) + [contour[0]]):
            length = math.dist(a, b)
            if length < d.grip_width + 3 or not eligible(*(0.5 * (a + b))):
                continue
            tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            nx, ny = -ty, tx
            count = max(1, math.floor((length - 3 - d.grip_width) / d.grip_pitch) + 1)
            for i in range(count):
                distance = (length - (count - 1) * d.grip_pitch) / 2 + i * d.grip_pitch
                x, y = a[0] + distance * tx, a[1] + distance * ty
                cuts.append(
                    tooth.extrude(d.grip_width)
                    .rotate(x=90)
                    .rotate(z=math.degrees(math.atan2(ny, nx)))
                    .move(x=x - tx * d.grip_width / 2, y=y - ty * d.grip_width / 2)
                )
    return union(cuts) if cuts else square(1, 1).extrude(1).move(z=-10)


def _tape_edge_cutter(start, end, d):
    """前后外边的 45° 倒角；打印从内缩底面向外渐长，不形成悬空底边。"""
    c, eps = d.tape_chamfer, 0.01
    cut = (
        polygon([(-eps, -eps), (c + eps, -eps), (-eps, c + eps)])
        .extrude(end - start + 2)
        .rotate(x=90)
        .rotate(z=90)
        .move(x=start - 1)
    )
    return cut + cut.mirror(y=1).move(y=d.depth)


def _tape_corner_cutter(edge, left, d):
    """水平板外端延续竖板的 Y/外侧面倒角，补齐装配后角部端头的缺口。"""
    c, eps = d.tape_chamfer, 0.01
    cut = (
        polygon([(-eps, -eps), (c + eps, -eps), (-eps, c + eps)])
        .extrude(d.thickness + 2 * eps)
        .move(z=-eps)
    )
    if not left:
        cut = cut.mirror(x=1)
    cut = cut.move(x=edge)
    return cut + cut.mirror(y=1).move(y=d.depth)


def _build_chunk(wall, i, bounds, d, fan_void, corner_males, guides, controller=None):
    start, end = bounds[i : i + 2]
    profile = _chunk_profile(wall, i, bounds, d)
    part = profile.extrude(d.thickness)
    if d.chamfer:
        beveled = _top_seam_chamfer(
            part,
            _chunk_profile(wall, i, bounds, d, extended=True),
            d.thickness,
            d.chamfer,
        )
        xmin, _, _, xmax, _, _ = part.bounding_box()
        margin = d.filter_capture + d.stop_thickness
        interior = (
            square(xmax - xmin + 2, d.depth - 2 * margin)
            .move(x=xmin - 1, y=margin)
            .extrude(d.thickness + 1)
        )
        # 滤网外伸区域不减料；仅在限位条内侧保留原填胶斜面。
        part -= (part - beveled) & interior
        side = wall in ("left", "right")
        joint_edges = ([start] if i > 0 or side else []) + (
            [end] if i < len(bounds) - 2 or side else []
        )
        part -= (
            _sealant_grip_cutter(
                profile,
                d,
                lambda x, y: 0.01 < y < d.depth - 0.01
                and any(
                    abs(x - edge) <= d.joint_depth + 2 * d.joint_clearance
                    for edge in joint_edges
                ),
            )
            & interior
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
    if wall in ("left", "right"):
        center = d.fan_centers_for(wall)[i]
        part -= fan_void.move(x=center, y=d.fan_center_y)
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
    if wall in ("bottom", "top"):
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
    if d.edge_relief_height:
        part -= _corner_relief_cutter(part, start, end, d)
    if d.tape_chamfer:
        part -= _tape_edge_cutter(start, end, d)
        if wall in ("bottom", "top"):
            if i == 0:
                part -= _tape_corner_cutter(start, True, d)
            if i == len(bounds) - 2:
                part -= _tape_corner_cutter(end, False, d)
    if d.bolts:
        if i:
            part += _flat_bolt_ear(start, False, d)
        if i < len(bounds) - 2:
            part += _flat_bolt_ear(end, True, d)
        for left in (False, True):
            for top in (False, True):
                if wall in ("bottom", "top") and top != (wall == "top"):
                    continue
                if wall in ("left", "right") and left != (wall == "left"):
                    continue
                ear = _corner_bolt_ear(wall, left, top, d)
                lo, _, _, hi, _, _ = ear.bounding_box()
                if start <= (lo + hi) / 2 <= end:
                    part += ear
    if wall == "top" and controller and start <= d.span / 2 < end:
        part = (part + controller["patch"]) - controller["cut"]
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
    controller = _controller_mount(d)
    for wall in ("bottom", "left", "top", "right"):
        bounds = _bounds(wall, d)
        guides = _guides(d) if wall in ("bottom", "top") else None
        for i in range(len(bounds) - 1):
            name = f"{wall}_{i + 1}"
            part = _build_chunk(wall, i, bounds, d, fan_void, males, guides, controller)
            if max(part.size().x, part.size().y) > d.bed_size:
                raise ValueError(f"{name} 超出预留后的可用打印平台")
            # 在最终打印坐标中清理切分共面的细碎三角形，避免 float32 STL 退化面。
            parts[name] = (
                part.align(xmin=0, ymin=0, zmin=0).as_original().simplify(1e-5)
            )
            assembled[name] = _wall_to_world(part, wall, d)
    if controller:
        for i, (name, rail) in enumerate(controller["rails"].items()):
            parts[name] = (
                rail.rotate(x=90 if i == 0 else -90)
                .align(xmin=0, ymin=0, zmin=0)
                .as_original()
                .simplify(1e-5)
            )
            assembled[name] = _wall_to_world(rail, "top", d)

    fan_blank = square(d.fan_size, d.fan_size, center=True).extrude(d.fan_thickness)
    airflow = cylinder(h=d.fan_thickness + 2, d=d.fan_opening, fn=128).move(z=-1)
    hub = cylinder(h=d.fan_thickness, d=38, fn=48)
    bridge = square(d.fan_size, 2, center=True).extrude(2)
    fan_proxy = fan_blank - airflow + hub + bridge + bridge.rotate(z=90)
    fans, fan_envelopes = {}, {}
    for wall in ("left", "right"):
        for i, center in enumerate(d.fan_centers_for(wall)):
            position = dict(x=center, y=d.fan_center_y, z=d.thickness)
            name = f"{wall}_fan_{i + 1}"
            fans[name] = _wall_to_world(fan_proxy.move(**position), wall, d)
            fan_envelopes[name] = _wall_to_world(fan_blank.move(**position), wall, d)

    # 每盘只放一块，避免两片同时打印；每面三块，保持 240 mm 内的排版边距。
    plate_names = [
        (name,)
        for wall in ("bottom", "left", "right", "top")
        for name in parts
        if name.startswith(f"{wall}_")
    ]
    if controller:
        plate_names.append(tuple(controller["rails"]))
    plates = []
    for names in plate_names:
        placed, cursor = [], 0.0
        for name in names:
            part = parts[name].move(x=cursor)
            placed.append(part)
            cursor += parts[name].size().x + d.bed_gap
        plate = union(placed)
        if max(plate.size().x, plate.size().y) > d.bed_size:
            raise ValueError("排盘超出预留后的可用平台")
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
_bolt_hardware, _bolt_tools = bolt_hardware(dimensions)
if _bolt_hardware:
    show_fasteners = _preview_group(_bolt_hardware.values())
show_with_fasteners = _preview_group([show_with_fans, *_bolt_hardware.values()])
_controller_model = _controller_mount(dimensions)
if _controller_model:
    show_controller = _wall_to_world(_controller_model["body"], "top", dimensions)
    show_with_controller = _preview_group([show_with_fasteners, show_controller])
    show_controller_ports = _wall_to_world(
        _controller_model["ports"], "top", dimensions
    )
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


def export_project_3mf(
    template,
    output,
    d=BoxDimensions(),
    filament=3,
):
    """复制模板的完整打印配置与自动 Brim 设置，导出多盘项目。

    python air_purifier_box.py --template sample.3mf --output print.3mf
    不写入手动 Brim 点；切片器按零件外轮廓和模板设置生成 Brim。
    布局为模板 Brim 宽度及对象间隙预留空间，导出后需重新切片。
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
        creality = source.read("Metadata/creality.config")
        types = source.read("[Content_Types].xml")
    if not 1 <= filament <= len(settings["filament_settings_id"]):
        raise ValueError("耗材编号超出模板耗材列表")
    if settings.get("brim_type") == "painted":
        raise ValueError("模板仍为手动 Brim；请在切片器中改为自动生成外沿 Brim")
    brim_width = float(settings["brim_width"])
    brim_gap = float(settings["brim_object_gap"])
    if not all(math.isfinite(v) and v >= 0 for v in (brim_width, brim_gap)):
        raise ValueError("模板 Brim 宽度和对象间隙必须为有限非负数")
    brim_extent = 0 if settings["brim_type"] == "no_brim" else brim_width + brim_gap
    if d.edge_relief_height:
        first_layer = float(settings["initial_layer_print_height"])
        if not math.isclose(first_layer, d.first_layer_height, abs_tol=1e-6):
            raise ValueError("模板首层高度与模型保留的首层厚度不一致")
    parts, _, _, _, plate_names, _ = build_box(d)
    bed = [tuple(map(float, point.split("x"))) for point in settings["printable_area"]]
    bx0, by0 = min(p[0] for p in bed), min(p[1] for p in bed)
    bx1, by1 = max(p[0] for p in bed), max(p[1] for p in bed)
    if set(bed) != {(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)}:
        raise ValueError("当前布局需要矩形打印平台")
    bed_width, bed_depth = bx1 - bx0, by1 - by0
    columns = math.ceil(math.sqrt(len(plate_names)))
    # Creality PartPlateList：盘间距为平台尺寸的 1.2 倍，按行向 -Y 排列。
    gap = max(d.bed_gap, 2 * brim_extent + 1.0)
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
    files = {}
    plate_elements = []
    serial = 0
    for plate_index, names in enumerate(plate_names):
        width = sum(parts[name].size().x for name in names) + gap * (len(names) - 1)
        depth = max(parts[name].size().y for name in names)
        # 整盘旋转 90°，与样例相同；连同自动 Brim 外缘检查平台及相邻零件间距。
        if width > d.bed_size or depth > d.bed_size:
            raise ValueError(f"第 {plate_index + 1} 盘含 Brim 间距后超过可用平台")
        if depth + 2 * brim_extent > bed_width or width + 2 * brim_extent > bed_depth:
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
        description="导出净化器多盘 3MF 项目，保留模板的自动 Brim 设置"
    )
    parser.add_argument(
        "--template", required=True, help="提供打印机、耗材和切片参数的样例 3MF"
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--filament", type=int, default=3)
    args = parser.parse_args()
    print(
        export_project_3mf(
            args.template,
            args.output,
            filament=args.filament,
        )
    )
