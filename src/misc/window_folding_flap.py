"""窗框磁吸折叠挡片：主板总高1040，五段；仅第五段延长，补高板总高仍为1008。
flap 正面有高0.4的凸点，shim 朝板内侧长边有深0.5的凹点；
每件1–5个直径1.5、中心距2.5的圆点表示对应编号。

flap_1..5、shim_1..5 各一件，mount 五件；按导出朝向平放，主板第五段长约240，其余件最长约208。
主板五段用燕尾定位，八套 M3×8 和普通 5.5 对边/2.4 厚螺母夹紧。
female燕尾同一截面横向每侧留0.10，纵向端面留0.20；male尺寸保持原样。
补高板每段另用两套 M3×8，共十套；整件共十八套 M3×8。螺丝从磁条侧装入，
头部沉入补高板，主板正面用普通螺母夹紧；无需胶粘固定螺母。
沉孔为外六角头防转槽，对边5.94（边长约3.429），深3.3，入口倒角0.15。
按头部对边5.44、头高3.0设计，头顶低于贴条面0.3；使用外六角头M3×8。
装好后连续12.7宽磁条盖住沉孔，入口最宽处两侧各保留约2.75粘贴宽度。
补高板整面平齐、厚5.3，与主板直接夹紧。需要气密时沿接口外缘及段间拼缝
连续封胶；不预留胶层厚度。先装配并封缝，再粘连续磁条。
主板原来的平背面、铰链和 M3 耳保持同侧可平放打印；补高板与主板接触的平面朝打印板，大沉孔朝上。
补高板先绕Y轴翻面，再从实际打印底面生成防翘槽；装配预览会转回安装姿态。
板面四角加入防翘试验槽：宽0.6、高1，保留0.2完整首层，孔口0.4×0.4斜坡。
主板截距12/24，窄补高板和胶条背板按宽度缩短；燕尾、立耳和铰链根部避空。
RELIEF_HEIGHT=0关闭；按首层0.2切片。无Brim防翘效果仍需实印验证。
十根 0.8×16 裸回形针销从 +Y 插入，入口胶带封住；孔径 1.0、轴向间隙 0.4。

坐标 X 横向、Y 高度、Z 朝室内；窗框面 Z=0，左侧窗户面 Z=-5.3；右侧窗框更靠室内。
窗框可贴平宽 34，分为活动磁条边 14.7、间隙 0.8、固定座 18.5。
磁条宽 12.7；右侧直接贴窗框与活动主板，左侧贴窗户与活动补高板。
固定座仅用 Command strip 粘贴，不跨过右侧磁吸密封线，也不承托磁条。
固定座连续竖筋厚2.4，胶条在竖筋与外缘之间居中，保留全宽拉片通道。
Command strip 宽15.625、长46；厚度暂按1；单条磁条按0.06英寸=1.524，若不含背胶需实测更新。
主板背面深度由右侧窗框面和磁条厚度决定，补高量不扣除 Command strip 厚度。
胶条拉片朝 -Y，上下各留25开放空间，先穿销对齐再粘固定座。
净开口87.3，两侧各搭接14.7，板面宽116.7；轴心到左外缘117.1。
OPENING_WIDTH只输入净开口，左右磁条、补高板、加强筋与接缝位置由板宽推导。
FLAP_HEIGHT只调整主板第五段顶部；最高32范围暂不延长补高板或磁条。
show_* 含磁条和紧固件占位，仅预览不导出；0°摊开，105°收起。
顶部接条、管道封口待设计；磁吸力、承载和气密需实装验证。运行本脚本执行几何检查。
"""

import math
import unittest

from b4dcad import circle, cube, cylinder, is_rendering, polygon, union

HEIGHT = 1000.0  # 原分段基准，保持接口、铰链和其他零件位置。
SEGMENTS = 5
PITCH = HEIGHT / SEGMENTS
OPENING_WIDTH = 87.3  # 实测横向净开口，不含窗户/窗框上的贴条搭接。
FRAME_WIDTH = 34.0
MAGNET_WIDTH = 12.7
MAGNET_LAND = MAGNET_WIDTH + 2.0
EDGE = 0.4
FRAME_LEFT = -(MAGNET_LAND + EDGE)
FIXED_WIDTH = FRAME_LEFT + FRAME_WIDTH
WINDOW_EDGE_X = FRAME_LEFT - OPENING_WIDTH
FLAP_PANEL_WIDTH = OPENING_WIDTH + 2 * MAGNET_LAND
FLAP_EXTENT = FLAP_PANEL_WIDTH + EDGE
DEPTH_STEP = 5.3  # 右侧窗框比左侧窗户向室内凸出。
WINDOW_PLANE_Z = -DEPTH_STEP
COMMAND_STRIP_STACK = 1.0  # 占位值：实测胶条装好后的总厚度（含配对胶条）。
MAGNET_THICKNESS = 0.06 * 25.4  # 单条 0.06 inch；若标称不含背胶，需改为安装总厚度。
FLAP_HEIGHT = 1040.0  # 仅调整 flap_5 上端；其余四段与连接位置固定。
SHIM_HEIGHT = HEIGHT + 8.0  # shim_5 保持原高度，上沿深度另行适配。
FLAP_Z = 2 * MAGNET_THICKNESS
SHIM_Z = WINDOW_PLANE_Z + 2 * MAGNET_THICKNESS
RIGHT_MAGNET_X = FRAME_LEFT + (MAGNET_LAND - MAGNET_WIDTH) / 2
LEFT_MAGNET_X = -FLAP_EXTENT + (MAGNET_LAND - MAGNET_WIDTH) / 2
THICKNESS = 2.4
RIB_HEIGHT = 6.0
RIB_WIDTH = 3.0
BED = 260.0
BARREL_RADIUS = 2.2
AXIS_Z = FLAP_Z + RIB_HEIGHT + 2 * BARREL_RADIUS + 0.8
PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BORE_DIAMETER = 1.0
BLIND_BOTTOM = 1.5
HINGE_LENGTH = 19.0
END_KNUCKLE = 6.0
AXIAL_GAP = 0.4
HINGE_STARTS = (25.0, PITCH - 40.0)
STRIP_WIDTH = (63 - 0.2 - 0.3) / 4
STRIP_HEIGHT = 46.0
SPINE_THICKNESS = 2.4
SPINE_END = EDGE + SPINE_THICKNESS
STRIP_X = (SPINE_END + FIXED_WIDTH - STRIP_WIDTH) / 2
PAD_START = (PITCH - STRIP_HEIGHT) / 2
ACCESS_HEIGHT = 25.0
JOINT_X = tuple(-FLAP_EXTENT + FLAP_PANEL_WIDTH * f for f in (0.25, 0.75))
JOINT_DEPTH = 8.0
JOINT_CLEARANCE_X = 0.10  # female 同一高度处的单侧横向间隙。
JOINT_CLEARANCE_Y = 0.20  # 纵向端面间隙独立保留。
SEAM = 0.2
BOLT_X = (-FLAP_EXTENT + 6.6, -FLAP_EXTENT + FLAP_PANEL_WIDTH / 2)
BOLT_EAR = 2.0
BOLT_HOLE = 3.4
BOLT_Z = FLAP_Z + RIB_HEIGHT + 5.0
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4

SHIM_X = -FLAP_EXTENT
SHIM_BOLT_X = SHIM_X + MAGNET_LAND / 2
SHIM_BOLT_Y = (PITCH / 3, 2 * PITCH / 3)
SHIM_HEAD_AF = 5.44
SHIM_HEAD_HEIGHT = 3.0
SHIM_SOCKET_AF = SHIM_HEAD_AF + 0.50  # 沿用已选定的 fit_050 对边总增量。
SHIM_ENTRY_CHAMFER = 0.15
SHIM_SOCKET_RADIUS = (SHIM_SOCKET_AF + 2 * SHIM_ENTRY_CHAMFER) / math.sqrt(3)
SHIM_COUNTERBORE_DEPTH = 3.3
SHIM_NUT_TOOL_RADIUS = 4.5

FIRST_LAYER_HEIGHT = 0.2
RELIEF_WIDTH = 0.6
RELIEF_HEIGHT = 1.0  # 设为 0 关闭角槽。
RELIEF_LIP = 0.4


def _corner_relief(part, x0, x1, y0, y1, base, protected=()):
    """仅切首层上方的四角对角槽，窄板等比例缩短截距，保留受力根部。"""
    if not RELIEF_HEIGHT:
        return part
    distance = min(12.0, (x1 - x0) / 5, (y1 - y0) / 5)
    bands = []
    guard = union(protected) if protected else None
    half, margin = RELIEF_WIDTH / 2, RELIEF_WIDTH + 0.1
    for x, sx in ((x0, 1), (x1, -1)):
        for y, sy in ((y0, 1), (y1, -1)):
            for reach in (distance, 2 * distance):
                a, b = (x + sx * reach, y), (x, y + sy * reach)
                length = math.dist(a, b)
                tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
                nx, ny = -ty, tx
                band = polygon(
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
                if guard is not None:
                    envelope = band.extrude(RELIEF_HEIGHT + RELIEF_LIP + 0.06).move(
                        z=base + FIRST_LAYER_HEIGHT
                    )
                    if abs((envelope & guard).manifold.volume()) > 1e-8:
                        continue
                bands.append(band)
    if not bands:
        return part
    footprint = union(bands)
    slots = footprint.extrude(RELIEF_HEIGHT)
    if RELIEF_LIP:
        h, c = RELIEF_HEIGHT, RELIEF_LIP
        profile = polygon([(-0.05, h), (c, h), (-0.05, h + c + 0.05)])
        edges = []
        for x, y, nx, ny, length in (
            (x0 - 1, y0, 0, 1, x1 - x0 + 2),
            (x1 + 1, y1, 0, -1, x1 - x0 + 2),
            (x0, y1 + 1, 1, 0, y1 - y0 + 2),
            (x1, y0 - 1, -1, 0, y1 - y0 + 2),
        ):
            edges.append(
                profile.extrude(length)
                .rotate(x=90)
                .rotate(z=math.degrees(math.atan2(ny, nx)))
                .move(x=x, y=y)
            )
        slots += union(edges) & footprint.extrude(h + c + 0.05)
    slots = slots.move(z=base + FIRST_LAYER_HEIGHT)
    return (part - slots).as_original().simplify(1e-5)


def _part_dots(index):
    """1–5 个直径1.5、中心距2.5的圆点表示分段编号。"""
    return union([circle(r=0.75, fn=32).move(x=i * 2.5) for i in range(index + 1)])


def _box(x0, x1, y0, y1, z0=FLAP_Z, z1=FLAP_Z + THICKNESS):
    return cube(x1 - x0, y1 - y0, z1 - z0).move(x=x0, y=y0, z=z0)


def _rib_ramp(x, direction, y0, y1, floor=FLAP_Z + THICKNESS, top=FLAP_Z + RIB_HEIGHT):
    """XZ 三角截面沿 Y 拉伸，斜面水平宽度等于筋高差。"""
    rise = top - floor
    return (
        polygon(
            [
                (x - direction * 0.1, floor - 0.1),
                (x - direction * 0.1, top),
                (x, top),
                (x + direction * (rise + 0.1), floor - 0.1),
            ]
        )
        .extrude(y1 - y0)
        .rotate(x=90)
        .move(y=y1)
    )


def _axial(diameter, start, end):
    return (
        cylinder(r=diameter / 2, h=end - start, fn=64)
        .rotate(x=-90)
        .move(y=start, z=AXIS_Z)
    )


def _bore(start, end):
    r = BORE_DIAMETER / 2
    t = r / math.sqrt(2)
    profile = circle(r=r, fn=64) + polygon([(-t, t), (t, t), (0, r * math.sqrt(2))])
    return profile.extrude(end - start).rotate(x=90).move(y=end, z=AXIS_Z)


def _hinge(start, fixed):
    intervals = (
        ((0, END_KNUCKLE), (HINGE_LENGTH - END_KNUCKLE, HINGE_LENGTH))
        if fixed
        else ((END_KNUCKLE + AXIAL_GAP, HINGE_LENGTH - END_KNUCKLE - AXIAL_GAP),)
    )
    pieces = []
    for low, high in intervals:
        a, b = start + low, start + high
        barrel = _axial(2 * BARREL_RADIUS, a, b)
        # 轴套抬到加强筋上方；仅在所属一侧设置立柱，另一侧板边可连续靠近。
        barrel += _box(
            0 if fixed else -BARREL_RADIUS,
            BARREL_RADIUS if fixed else 0,
            a,
            b,
            COMMAND_STRIP_STACK if fixed else FLAP_Z,
            AXIS_Z,
        )
        # 跨到对侧的轴套下方用 45° 斜撑托起，斜撑最低点仍高于连续加强筋。
        side = -1 if fixed else 1
        support = (
            polygon(
                [
                    (0, AXIS_Z - 2 * BARREL_RADIUS),
                    (side * BARREL_RADIUS, AXIS_Z - BARREL_RADIUS),
                    (side * BARREL_RADIUS, AXIS_Z),
                    (0, AXIS_Z),
                ]
            )
            .extrude(b - a)
            .rotate(x=90)
            .move(y=b)
        )
        barrel += support
        barrel -= _bore(a + BLIND_BOTTOM if fixed and low == 0 else a - 0.1, b + 0.1)
        pieces.append(barrel)
    return union(pieces)


def _tab(x, seam, female=False):
    # 同一 Y 截面处独立控制 X 间隙，保留斜边斜率；不再用等距 offset 同时放大两轴。
    low, high = -1.0, JOINT_DEPTH
    neck, tip = 6.0, 10.0
    if female:
        slope = (tip - neck) / (high - low)
        low -= JOINT_CLEARANCE_Y
        high += JOINT_CLEARANCE_Y
        neck += JOINT_CLEARANCE_X - slope * JOINT_CLEARANCE_Y
        tip += JOINT_CLEARANCE_X + slope * JOINT_CLEARANCE_Y
    profile = polygon([(-neck, low), (neck, low), (tip, high), (-tip, high)])
    return profile.extrude(THICKNESS + (2 if female else 0)).move(
        x=x, y=seam, z=FLAP_Z - 1 if female else FLAP_Z
    )


def flap_segment(index):
    if not 0 <= index < SEGMENTS:
        raise ValueError("segment index out of range")
    low = SEAM / 2 if index else 0
    high = (
        PITCH - SEAM / 2
        if index < SEGMENTS - 1
        else FLAP_HEIGHT - (SEGMENTS - 1) * PITCH
    )
    part = _box(-FLAP_EXTENT, -EDGE, low, high)
    for x in (
        -FLAP_EXTENT,
        -FLAP_EXTENT + (FLAP_PANEL_WIDTH - RIB_WIDTH) / 2,
        -EDGE - RIB_WIDTH,
    ):
        part += _box(
            x, x + RIB_WIDTH, low, high, FLAP_Z + THICKNESS, FLAP_Z + RIB_HEIGHT
        )
        if x > -FLAP_EXTENT:
            part += _rib_ramp(x, -1, low, high)
        if x + RIB_WIDTH < -EDGE:
            part += _rib_ramp(x + RIB_WIDTH, 1, low, high)
    for x in JOINT_X:
        if index < SEGMENTS - 1:
            part += _tab(x, PITCH)
        if index:
            part -= _tab(x, 0, female=True)
    for x in BOLT_X:
        if index < SEGMENTS - 1:
            part += _bolt_ear(x, PITCH, True)
        if index:
            part += _bolt_ear(x, 0, False)
    for y in SHIM_BOLT_Y:
        part -= cylinder(r=BOLT_HOLE / 2, h=THICKNESS + 2).move(
            x=SHIM_BOLT_X, y=y, z=FLAP_Z - 1
        )
        # 正面螺母压在完整板厚上，局部削开筋条，留出套筒的通道。
        part -= cylinder(r=SHIM_NUT_TOOL_RADIUS + 0.2, h=20).move(
            x=SHIM_BOLT_X, y=y, z=FLAP_Z + THICKNESS
        )
    for start in HINGE_STARTS:
        part += _hinge(start, False)
    guards = []
    for seam in ([0] if index else []) + ([PITCH] if index < SEGMENTS - 1 else []):
        for x in JOINT_X:
            guards.append(
                _box(
                    x - 11.5,
                    x + 11.5,
                    seam - 2,
                    seam + JOINT_DEPTH + 1,
                    FLAP_Z - 1,
                    FLAP_Z + THICKNESS + 1,
                )
            )
        for x in BOLT_X:
            guards.append(
                _box(
                    x - 7, x + 7, seam - 7, seam + 7, FLAP_Z - 1, FLAP_Z + THICKNESS + 1
                )
            )
    for start in HINGE_STARTS:
        guards.append(
            _box(
                -EDGE - RIB_WIDTH - 0.8,
                BARREL_RADIUS + 1,
                start - 0.8,
                start + HINGE_LENGTH + 0.8,
                FLAP_Z - 1,
                FLAP_Z + THICKNESS + 1,
            )
        )
    part += (
        _part_dots(index)
        .extrude(0.42)
        .align(xmin=JOINT_X[0], ymin=20, zmin=FLAP_Z + THICKNESS - 0.02)
    )
    return _corner_relief(part, -FLAP_EXTENT, -EDGE, low, high, FLAP_Z, guards)


def fixed_segment():
    low, high = SEAM / 2, PITCH - SEAM / 2
    part = _box(EDGE, SPINE_END, low, high, COMMAND_STRIP_STACK, FLAP_Z + RIB_HEIGHT)
    part += _box(
        EDGE,
        FIXED_WIDTH,
        PAD_START,
        PAD_START + STRIP_HEIGHT,
        COMMAND_STRIP_STACK,
        COMMAND_STRIP_STACK + THICKNESS,
    )
    for y in (PAD_START, PAD_START + STRIP_HEIGHT - THICKNESS):
        part += _rib_ramp(
            SPINE_END,
            1,
            y,
            y + THICKNESS,
            floor=COMMAND_STRIP_STACK + THICKNESS,
            top=FLAP_Z + RIB_HEIGHT - 0.2,
        )
    for start in HINGE_STARTS:
        part += _hinge(start, True)
    guard = _box(EDGE - 1, SPINE_END + 0.8, low - 1, high + 1, 0, AXIS_Z + 1)
    return _corner_relief(
        part,
        EDGE,
        FIXED_WIDTH,
        PAD_START,
        PAD_START + STRIP_HEIGHT,
        COMMAND_STRIP_STACK,
        [guard],
    )


def _hex(af, height, top_af=None):
    radius = af / math.sqrt(3)
    top_radius = radius if top_af is None else top_af / math.sqrt(3)
    return cylinder(h=height, r=radius, r2=top_radius, fn=6)


def shim_segment(index, *, for_print=False):
    """装配姿态默认；for_print=True 时沉孔朝上，角槽始终靠打印底面。"""
    low = SEAM / 2 if index else 0
    high = (
        PITCH - SEAM / 2
        if index < SEGMENTS - 1
        else SHIM_HEIGHT - (SEGMENTS - 1) * PITCH
    )
    part = _box(SHIM_X, SHIM_X + MAGNET_LAND, low, high, SHIM_Z, FLAP_Z)
    for y in SHIM_BOLT_Y:
        part -= _hex(SHIM_SOCKET_AF, SHIM_COUNTERBORE_DEPTH + 0.1).move(
            x=SHIM_BOLT_X, y=y, z=SHIM_Z - 0.1
        )
        part -= _hex(
            SHIM_SOCKET_AF + 2 * SHIM_ENTRY_CHAMFER, SHIM_ENTRY_CHAMFER, SHIM_SOCKET_AF
        ).move(x=SHIM_BOLT_X, y=y, z=SHIM_Z)
        part -= cylinder(r=BOLT_HOLE / 2, h=DEPTH_STEP + 2).move(
            x=SHIM_BOLT_X, y=y, z=SHIM_Z - 1
        )
    number = _part_dots(index)
    part -= (
        number.extrude(0.52)
        .rotate(x=90, z=90)
        .align(
            xmax=SHIM_X + MAGNET_LAND + 0.02,
            ymin=20,
            zmin=SHIM_Z + DEPTH_STEP / 2 - 0.75,
        )
    )
    # 先翻面，再切角槽；不能将旧槽随实体一起翻到打印顶面。
    part = _corner_relief(
        part.rotate(y=180),
        -(SHIM_X + MAGNET_LAND),
        -SHIM_X,
        low,
        high,
        -FLAP_Z,
    )
    if for_print:
        return part.align(xmin=0, ymin=0, zmin=0).as_original().simplify(1e-5)
    return part.rotate(y=180).as_original().simplify(1e-5)


def shim_hardware():
    """沉孔侧 M3×8 向 +Z 穿过补高板和主板，正面普通螺母夹紧。"""
    pieces = []
    seat = SHIM_Z + SHIM_COUNTERBORE_DEPTH
    for y in SHIM_BOLT_Y:
        shaft = cylinder(r=1.5, h=BOLT_LENGTH).move(x=SHIM_BOLT_X, y=y, z=seat)
        head = _hex(SHIM_HEAD_AF, SHIM_HEAD_HEIGHT).move(
            x=SHIM_BOLT_X, y=y, z=seat - SHIM_HEAD_HEIGHT
        )
        nut = _hex(5.5, NUT_HEIGHT) - cylinder(r=BOLT_HOLE / 2, h=NUT_HEIGHT)
        pieces.append(shaft + head + nut.move(x=SHIM_BOLT_X, y=y, z=FLAP_Z + THICKNESS))
    return union(pieces)


def magnetic_strips(moving, height=SHIM_HEIGHT):
    """右侧直接贴窗框，左侧贴窗户；两侧环境贴条面相差 5.3。"""
    z0 = MAGNET_THICKNESS if moving else 0
    return _box(
        RIGHT_MAGNET_X,
        RIGHT_MAGNET_X + MAGNET_WIDTH,
        0,
        height,
        z0,
        z0 + MAGNET_THICKNESS,
    ) + _box(
        LEFT_MAGNET_X,
        LEFT_MAGNET_X + MAGNET_WIDTH,
        0,
        height,
        z0 + WINDOW_PLANE_Z,
        z0 + WINDOW_PLANE_Z + MAGNET_THICKNESS,
    )


def _bolt_ear(x, seam, lower):
    """成对立耳沿 Y 夹紧；两侧三角筋避开螺母及工具。"""
    top = BOLT_Z + 4
    shape = polygon(
        [
            (x - 6, FLAP_Z + THICKNESS - 0.4),
            (x + 6, FLAP_Z + THICKNESS - 0.4),
            (x + 6, top - 1),
            (x + 5, top),
            (x - 5, top),
            (x - 6, top - 1),
        ]
    )
    r = BOLT_HOLE / 2
    t = r / math.sqrt(2)
    bore = circle(r=r, fn=48).move(x=x, y=BOLT_Z) + polygon(
        [(x - t, BOLT_Z + t), (x + t, BOLT_Z + t), (x, BOLT_Z + r * math.sqrt(2))]
    )
    end = seam - SEAM / 2 if lower else seam + SEAM / 2 + BOLT_EAR
    ear = (shape - bore).extrude(BOLT_EAR).rotate(x=90).move(y=end)
    side = seam - SEAM / 2 - BOLT_EAR if lower else seam + SEAM / 2 + BOLT_EAR
    direction = -1 if lower else 1
    for dx in (-5.3, 5.3):
        # Y/Z 截面；斜撑根部与板、立耳均有实体重叠。
        rib = polygon(
            [
                (side - direction * 0.2, FLAP_Z + THICKNESS - 0.4),
                (side + direction * 4, FLAP_Z + THICKNESS - 0.4),
                (side - direction * 0.2, FLAP_Z + THICKNESS + 10),
            ]
        )
        ear += rib.extrude(1.2).rotate(x=90, z=90).move(x=x + dx - 0.6)
    return ear


def _bolt_envelopes(x, seam):
    """螺丝/螺母外包络及直线工具通道，仅用于预览和避让。"""
    near = seam - SEAM / 2 - BOLT_EAR
    far = seam + SEAM / 2 + BOLT_EAR

    def axial(radius, start, end):
        return (
            cylinder(r=radius, h=end - start, fn=48)
            .rotate(x=-90)
            .move(x=x, y=start, z=BOLT_Z)
        )

    shaft = axial(1.5, near, near + BOLT_LENGTH)
    head = axial(3.2, near - 3, near)
    nut = axial(5.5 / math.sqrt(3), far, far + NUT_HEIGHT) - axial(
        BOLT_HOLE / 2, far - 0.1, far + NUT_HEIGHT + 0.1
    )
    tools = axial(3.5, near - 23, near - 3) + axial(
        4.5, far + NUT_HEIGHT, far + NUT_HEIGHT + 5
    )
    return shaft + head + nut, tools


def fold(part, angle):
    return part.move(z=-AXIS_Z).rotate(y=angle).move(z=AXIS_Z)


def assembly(angle):
    fixed = union([fixed_segment().move(y=i * PITCH) for i in range(SEGMENTS)])
    moving = union(
        [
            (flap_segment(i) + shim_segment(i) + shim_hardware()).move(y=i * PITCH)
            for i in range(SEGMENTS)
        ]
    )
    for seam in range(1, SEGMENTS):
        for x in BOLT_X:
            hardware, _ = _bolt_envelopes(x, seam * PITCH)
            moving += hardware
    return fixed + magnetic_strips(False) + fold(moving + magnetic_strips(True), angle)


class GeometryTests(unittest.TestCase):
    def assert_clear(self, a, b):
        self.assertLess(abs((a & b).manifold.volume()), 1e-5)

    def test_printable_connected_parts(self):
        parts = [fixed_segment()]
        parts.extend(flap_segment(i) for i in range(SEGMENTS))
        parts.extend(shim_segment(i, for_print=True) for i in range(SEGMENTS))
        for part in parts:
            self.assertEqual(len(part.decompose()), 1)
            self.assertLessEqual(max(part.size().x, part.size().y), BED - 10)
            self.assertGreater(part.manifold.volume(), 0)

    def test_relief_keeps_first_layer(self):
        blank = _box(0, 30, 0, 50, 0, THICKNESS)
        cut = _corner_relief(blank, 0, 30, 0, 50, 0)
        first_layer = _box(0, 30, 0, 50, 0, FIRST_LAYER_HEIGHT)
        self.assert_clear(blank - cut, first_layer)
        self.assert_clear(
            blank - cut,
            _box(
                0,
                30,
                0,
                50,
                FIRST_LAYER_HEIGHT + RELIEF_HEIGHT + RELIEF_LIP + 0.06,
                THICKNESS,
            ),
        )
        if RELIEF_HEIGHT:
            self.assertGreater((blank - cut).manifold.volume(), 1)

    def test_shim_print_orientation(self):
        part = shim_segment(0, for_print=True)
        floor = _box(0, MAGNET_LAND, 0, PITCH - SEAM / 2, 0, FIRST_LAYER_HEIGHT)
        for y in SHIM_BOLT_Y:
            floor -= cylinder(r=BOLT_HOLE / 2, h=FIRST_LAYER_HEIGHT).move(
                x=MAGNET_LAND / 2, y=y
            )
            # 底部先打印小通孔，上部才扩大为沉孔，避免沉孔顶面的悬空肩部。
            lower = _hex(SHIM_HEAD_AF, 0.1).move(x=MAGNET_LAND / 2, y=y, z=0.5)
            upper = lower.move(z=DEPTH_STEP - SHIM_COUNTERBORE_DEPTH)
            self.assertGreater((part & lower).manifold.volume(), 1)
            self.assert_clear(part, upper)
        self.assert_clear(floor - part, floor)
        if RELIEF_HEIGHT:
            # 新底面附近有角槽，上部角落仍完整。
            corner = _box(
                0, 6.5, 0, 6.5, FIRST_LAYER_HEIGHT, FIRST_LAYER_HEIGHT + RELIEF_HEIGHT
            )
            self.assertLess(
                (part & corner).manifold.volume(), corner.manifold.volume() - 1
            )
            upper_corner = corner.move(
                z=DEPTH_STEP - FIRST_LAYER_HEIGHT - RELIEF_HEIGHT
            )
            self.assert_clear(upper_corner - part, upper_corner)

    def test_rotation_clearance(self):
        fixed = fixed_segment() + magnetic_strips(False, PITCH)
        moving = (
            flap_segment(1)
            + shim_segment(1)
            + shim_hardware()
            + magnetic_strips(True, PITCH)
        )
        # 实体窗户/窗框和紧固件一起检查，不重复验证已实测的销、燕尾配合。
        fixed += _box(
            WINDOW_EDGE_X - MAGNET_LAND,
            WINDOW_EDGE_X,
            0,
            PITCH,
            WINDOW_PLANE_Z - 3,
            WINDOW_PLANE_Z,
        )
        fixed += _box(
            FRAME_LEFT,
            FIXED_WIDTH,
            0,
            PITCH,
            -3,
            0,
        )
        for seam in (0, PITCH):
            for x in BOLT_X:
                hardware, _ = _bolt_envelopes(x, seam)
                moving += hardware
        for angle in range(0, 111, 2):
            self.assert_clear(fixed, fold(moving, angle))

    def test_magnets_overlap_measured_opening(self):
        # 从独立的实测净开口构造两个实体贴合面，避免用磁条位置反推窗户边界。
        window = _box(
            WINDOW_EDGE_X - MAGNET_LAND,
            WINDOW_EDGE_X,
            0,
            PITCH,
            WINDOW_PLANE_Z - 0.1,
            WINDOW_PLANE_Z,
        )
        frame = _box(FRAME_LEFT, FIXED_WIDTH, 0, PITCH, -0.1, 0)
        contact = magnetic_strips(False, PITCH).move(z=-0.1)
        for substrate in (window, frame):
            self.assertAlmostEqual(
                (contact & substrate).manifold.volume(),
                MAGNET_WIDTH * PITCH * 0.1,
                places=4,
            )

    def test_shim_hex_head_capture(self):
        shim = shim_segment(0)
        z = SHIM_Z + SHIM_COUNTERBORE_DEPTH - SHIM_HEAD_HEIGHT
        for y in SHIM_BOLT_Y:
            head = _hex(SHIM_HEAD_AF, SHIM_HEAD_HEIGHT)
            self.assert_clear(shim, head.move(x=SHIM_BOLT_X, y=y, z=z))
            # 配合余量允许插入，但头部无法在槽内自由转过平角与尖角的中间姿态。
            turned = head.rotate(z=30).move(x=SHIM_BOLT_X, y=y, z=z)
            self.assertGreater((shim & turned).manifold.volume(), 0.01)

    def test_magnetic_lands_and_shim(self):
        flap, shim = flap_segment(1), shim_segment(1)
        self.assert_clear(flap, shim)
        self.assert_clear(flap + shim, shim_hardware())
        seat = SHIM_Z + SHIM_COUNTERBORE_DEPTH
        self.assertGreaterEqual(SHIM_COUNTERBORE_DEPTH - SHIM_HEAD_HEIGHT, 0.25)
        self.assertGreaterEqual(FLAP_Z - seat, 1.6)
        self.assertGreaterEqual(
            seat + BOLT_LENGTH - (FLAP_Z + THICKNESS + NUT_HEIGHT), 0.5
        )
        self.assert_clear(shim_hardware(), magnetic_strips(True, PITCH))
        # 左磁条完整盖住沉孔，两侧仍有连续承托和粘贴面。
        hole_left = SHIM_BOLT_X - SHIM_SOCKET_RADIUS
        hole_right = SHIM_BOLT_X + SHIM_SOCKET_RADIUS
        self.assertGreaterEqual(hole_left - LEFT_MAGNET_X, 2.5)
        self.assertGreaterEqual(LEFT_MAGNET_X + MAGNET_WIDTH - hole_right, 2.5)
        for x0, x1, base, part in (
            (LEFT_MAGNET_X, hole_left, SHIM_Z, shim),
            (hole_right, LEFT_MAGNET_X + MAGNET_WIDTH, SHIM_Z, shim),
            (RIGHT_MAGNET_X, RIGHT_MAGNET_X + MAGNET_WIDTH, FLAP_Z, flap),
        ):
            bearing = _box(x0, x1, 10, PITCH - 10, base, base + 0.1)
            self.assertAlmostEqual(
                (part & bearing).manifold.volume(),
                (x1 - x0) * (PITCH - 20) * 0.1,
                places=4,
            )
        for y in SHIM_BOLT_Y:
            socket = cylinder(r=SHIM_NUT_TOOL_RADIUS, h=20).move(
                x=SHIM_BOLT_X, y=y, z=FLAP_Z + THICKNESS
            )
            driver = cylinder(r=2.5, h=20).move(
                x=SHIM_BOLT_X, y=y, z=seat - SHIM_HEAD_HEIGHT - 20
            )
            self.assert_clear(flap + shim, socket + driver)
        # 两个胶带区在 34 mm 窗框内，且固定座不挡住右侧磁条。
        self.assertGreaterEqual(RIGHT_MAGNET_X, FRAME_LEFT)
        self.assertLessEqual(STRIP_X + STRIP_WIDTH, FIXED_WIDTH)
        self.assertLess(RIGHT_MAGNET_X + MAGNET_WIDTH, EDGE)
        self.assert_clear(fixed_segment(), magnetic_strips(False, PITCH))

    def test_bolted_seams(self):
        self.assertGreaterEqual(BOLT_LENGTH, 2 * BOLT_EAR + SEAM + NUT_HEIGHT + 0.5)
        for index in range(SEGMENTS - 1):
            lower = flap_segment(index)
            upper = flap_segment(index + 1).move(y=PITCH)
            self.assert_clear(lower, upper)
            for x in BOLT_X:
                hardware, tools = _bolt_envelopes(x, PITCH)
                self.assert_clear(lower + upper, hardware)
                self.assert_clear(lower + upper, tools)
            self.assert_clear(fixed_segment(), fixed_segment().move(y=PITCH))

    def test_strip_access(self):
        fixed = fixed_segment()
        for a, b in (
            (PAD_START - ACCESS_HEIGHT, PAD_START),
            (PAD_START + STRIP_HEIGHT, PAD_START + STRIP_HEIGHT + ACCESS_HEIGHT),
        ):
            opening = _box(STRIP_X, FIXED_WIDTH + 20, a, b, -2, 15)
            self.assert_clear(fixed, opening)
        adhesive = _box(
            STRIP_X,
            STRIP_X + STRIP_WIDTH,
            PAD_START,
            PAD_START + STRIP_HEIGHT,
            0,
            COMMAND_STRIP_STACK,
        )
        self.assert_clear(fixed, adhesive)
        contact = _box(
            STRIP_X,
            STRIP_X + STRIP_WIDTH,
            PAD_START,
            PAD_START + STRIP_HEIGHT,
            COMMAND_STRIP_STACK,
            COMMAND_STRIP_STACK + FIRST_LAYER_HEIGHT,
        )
        self.assertAlmostEqual(
            (contact & fixed).manifold.volume(),
            STRIP_WIDTH * STRIP_HEIGHT * FIRST_LAYER_HEIGHT,
            places=3,
        )


if is_rendering():
    for _i in range(SEGMENTS):
        globals()[f"flap_{_i + 1}"] = flap_segment(_i).align(xmin=0, ymin=0, zmin=0)
        globals()[f"shim_{_i + 1}"] = shim_segment(_i, for_print=True)
    mount = fixed_segment().align(xmin=0, ymin=0, zmin=0)
    show_open = assembly(0)
    show_folded = assembly(105)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
