"""窗框磁吸折叠挡片：主体 1000 高，五段，顶段另留 8 高度余量。

flap_1..5、shim_1..5 各一件，mount 五件；按导出朝向平放，最长约 208。
主板五段用燕尾定位，八套 M3×8 和普通 5.5 对边/2.4 厚螺母夹紧。
补高板每段另用两套 M3×8，共十套；整件共十八套 M3×8。螺丝从磁条侧装入，
头部沉入补高板，主板正面用普通螺母夹紧；无需胶粘固定螺母。
沉孔直径6.8、深3.3，按头径不超过6.4、头高不超过3.0设计，头顶低于贴条面0.3。
装好并拧紧后，连续12.7宽磁条盖住沉孔；孔两侧各保留约2.95粘贴宽度。
补高板整面平齐、厚5.3，与主板直接夹紧。需要气密时沿接口外缘及段间拼缝
连续封胶；不预留胶层厚度。先装配并封缝，再粘连续磁条。
主板原来的平背面、铰链和 M3 耳保持同侧可平放打印；补高板磁条面朝打印板。
十根 0.8×16 裸回形针销从 +Y 插入，入口胶带封住；孔径 1.0、轴向间隙 0.4。

坐标 X 横向、Y 高度、Z 朝室内；窗框面 Z=0，左侧窗户面 Z=-5.3；右侧窗框更靠室内。
窗框可贴平宽 34，分为活动磁条边 14.7、间隙 0.8、固定座 18.5。
磁条宽 12.7；右侧直接贴窗框与活动主板，左侧贴窗户与活动补高板。
固定座仅用 Command strip 粘贴，不跨过右侧磁吸密封线，也不承托磁条。
Command strip 宽15.625、长46；厚度暂按1，单条磁条含背胶也暂按1，购入后核对。
主板背面深度由右侧窗框面和磁条厚度决定，补高量不扣除 Command strip 厚度。
胶条拉片朝 -Y，上下各留25开放空间，先穿销对齐再粘固定座。
主板轴心到左外缘101.6，实际横向覆盖仍需按窗框搭接位置核对。
show_* 含磁条和紧固件占位，仅预览不导出；0°摊开，105°收起。
顶部接条、管道封口待设计；磁吸力、承载和气密需实装验证。运行本脚本执行几何检查。
"""

import math
import unittest

from b4dcad import circle, cube, cylinder, is_rendering, polygon, union

HEIGHT = 1000.0
SEGMENTS = 5
PITCH = HEIGHT / SEGMENTS
FRAME_WIDTH = 34.0
FRAME_LEFT = -15.1
FIXED_WIDTH = FRAME_LEFT + FRAME_WIDTH
DEPTH_STEP = 5.3  # 右侧窗框比左侧窗户向室内凸出。
WINDOW_PLANE_Z = -DEPTH_STEP
COMMAND_STRIP_STACK = 1.0  # 占位值：实测胶条装好后的总厚度（含配对胶条）。
MAGNET_WIDTH = 12.7
MAGNET_THICKNESS = 1.0  # 占位值：单条磁条含背胶的厚度。
MAGNET_LAND = 14.7
TOP_ALLOWANCE = 8.0  # 顶段可裁/可改余量，不计入名义高度。
FLAP_Z = 2 * MAGNET_THICKNESS
SHIM_Z = WINDOW_PLANE_Z + 2 * MAGNET_THICKNESS
RIGHT_MAGNET_X = FRAME_LEFT + 1.0
LEFT_MAGNET_X = -100.6
FLAP_EXTENT = 101.6
THICKNESS = 2.4
RIB_HEIGHT = 6.0
RIB_WIDTH = 3.0
BED = 260.0
BARREL_RADIUS = 2.2
AXIS_Z = FLAP_Z + RIB_HEIGHT + 2 * BARREL_RADIUS + 0.8
EDGE = 0.4
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
STRIP_X = (EDGE + FIXED_WIDTH - STRIP_WIDTH) / 2
SPINE_END = 1.6
PAD_START = (PITCH - STRIP_HEIGHT) / 2
ACCESS_HEIGHT = 25.0
JOINT_X = (-77.0, -29.0)
JOINT_DEPTH = 8.0
JOINT_CLEARANCE = 0.2
SEAM = 0.2
BOLT_X = (-95.0, -52.5)
BOLT_EAR = 2.0
BOLT_HOLE = 3.4
BOLT_Z = FLAP_Z + RIB_HEIGHT + 5.0
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4

SHIM_X = -FLAP_EXTENT
SHIM_BOLT_X = SHIM_X + MAGNET_LAND / 2
SHIM_BOLT_Y = (PITCH / 3, 2 * PITCH / 3)
SHIM_HEAD_DIAMETER = 6.4
SHIM_HEAD_HEIGHT = 3.0
SHIM_COUNTERBORE = 6.8
SHIM_COUNTERBORE_DEPTH = 3.3
SHIM_NUT_TOOL_RADIUS = 4.5


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


def _tab(x, seam, clearance=0):
    # 从板面法向嵌合的平面燕尾，根部伸回板内 1 mm。
    profile = polygon([(-6, -1), (6, -1), (10, JOINT_DEPTH), (-10, JOINT_DEPTH)])
    if clearance:
        profile = profile.offset(clearance, "miter")
    return profile.extrude(THICKNESS + (2 if clearance else 0)).move(
        x=x, y=seam, z=FLAP_Z - 1 if clearance else FLAP_Z
    )


def flap_segment(index):
    if not 0 <= index < SEGMENTS:
        raise ValueError("segment index out of range")
    low = SEAM / 2 if index else 0
    high = PITCH - SEAM / 2 if index < SEGMENTS - 1 else PITCH + TOP_ALLOWANCE
    part = _box(-FLAP_EXTENT, -EDGE, low, high)
    for x in (-FLAP_EXTENT, -54.0, -EDGE - RIB_WIDTH):
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
            part -= _tab(x, 0, JOINT_CLEARANCE)
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
    return part.as_original().simplify(1e-5)


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
    return part.as_original().simplify(1e-5)


def _hex_nut(af, height):
    radius = af / math.sqrt(3)
    return polygon(
        [
            (radius * math.cos(i * math.pi / 3), radius * math.sin(i * math.pi / 3))
            for i in range(6)
        ]
    ).extrude(height)


def shim_segment(index):
    """磁条面朝下平放打印，螺丝从该面的沉孔装入。"""
    low = SEAM / 2 if index else 0
    high = PITCH - SEAM / 2 if index < SEGMENTS - 1 else PITCH + TOP_ALLOWANCE
    part = _box(SHIM_X, SHIM_X + MAGNET_LAND, low, high, SHIM_Z, FLAP_Z)
    for y in SHIM_BOLT_Y:
        part -= cylinder(r=SHIM_COUNTERBORE / 2, h=SHIM_COUNTERBORE_DEPTH + 0.1).move(
            x=SHIM_BOLT_X, y=y, z=SHIM_Z - 0.1
        )
        part -= cylinder(r=BOLT_HOLE / 2, h=DEPTH_STEP + 2).move(
            x=SHIM_BOLT_X, y=y, z=SHIM_Z - 1
        )
    return part.as_original().simplify(1e-5)


def shim_hardware():
    """沉孔侧 M3×8 向 +Z 穿过补高板和主板，正面普通螺母夹紧。"""
    pieces = []
    seat = SHIM_Z + SHIM_COUNTERBORE_DEPTH
    for y in SHIM_BOLT_Y:
        shaft = cylinder(r=1.5, h=BOLT_LENGTH).move(x=SHIM_BOLT_X, y=y, z=seat)
        head = cylinder(r=SHIM_HEAD_DIAMETER / 2, h=SHIM_HEAD_HEIGHT).move(
            x=SHIM_BOLT_X, y=y, z=seat - SHIM_HEAD_HEIGHT
        )
        nut = _hex_nut(5.5, NUT_HEIGHT) - cylinder(r=BOLT_HOLE / 2, h=NUT_HEIGHT)
        pieces.append(shaft + head + nut.move(x=SHIM_BOLT_X, y=y, z=FLAP_Z + THICKNESS))
    return union(pieces)


def magnetic_strips(moving, height=HEIGHT + TOP_ALLOWANCE):
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
        parts.extend(shim_segment(i) for i in range(SEGMENTS))
        for part in parts:
            self.assertEqual(len(part.decompose()), 1)
            self.assertLessEqual(max(part.size().x, part.size().y), BED - 10)
            self.assertGreater(part.manifold.volume(), 0)

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
            LEFT_MAGNET_X - 1,
            LEFT_MAGNET_X + MAGNET_LAND,
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
        hole_left = SHIM_BOLT_X - SHIM_COUNTERBORE / 2
        hole_right = SHIM_BOLT_X + SHIM_COUNTERBORE / 2
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
        self.assertAlmostEqual(
            (adhesive.move(z=1) & fixed).manifold.volume(),
            STRIP_WIDTH * STRIP_HEIGHT * min(1, COMMAND_STRIP_STACK),
            places=3,
        )


if is_rendering():
    for _i in range(SEGMENTS):
        globals()[f"flap_{_i + 1}"] = flap_segment(_i).align(xmin=0, ymin=0, zmin=0)
        globals()[f"shim_{_i + 1}"] = shim_segment(_i).align(xmin=0, ymin=0, zmin=0)
    mount = fixed_segment().align(xmin=0, ymin=0, zmin=0)
    show_open = assembly(0)
    show_folded = assembly(105)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
