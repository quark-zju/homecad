"""实验性窗框磁吸折叠挡片：名义高 1000、摊开总宽 127，固定侧宽 25.4。

flap_1..5 各一件，mount 五件；按导出朝向平放，最长约 208，适配 260×260。
顶段额外留 TOP_ALLOWANCE=8 高度，装配总高 1008；顶部磁吸接条及下部管道件待设计。
五段用燕尾定位、八套 M3×8 和普通 5.5 对边/2.4 厚螺母夹紧；立耳孔径 3.4。
十根 0.8×16 裸回形针销，从 +Y 插入；-Y 端 1.5 盲底，入口用胶带封住。
铰链抬到加强筋上方，板间缝 0.6；两侧轴套根部交错，孔径 1.0、轴向间隙 0.4。
板厚 2.4、筋高 6（含板厚），筋根与胶条背板两端保留斜撑。

建模坐标 X 为横向、Y 为高度、Z 为朝室内的进深（用户讨论中的 Y 向）。
固定座背面 Z=0，窗框面 Z=-COMMAND_STRIP_STACK，窗户面比窗框凸出 5.3。
Command strip 总厚暂按 1.0，单条磁条含胶暂按 1.0；购买后修改参数核对。
固定座左伸搭接板上表面与窗户面等深，右侧磁吸与左侧磁吸均有两条 12.7 宽磁条。
活动板背面整片平齐；通过加厚固定搭接底板补偿深度，无需在活动板底面做悬空台阶。
胶条在固定座右侧背面（15.625×46），磁条在其左伸搭接面和活动板背面。
胶条拉片朝 -Y，上下 25 开放空间保留；先穿销对齐，再粘贴固定座。
磁条连续粘贴覆盖打印分段处；横缝仍需密封，磁条占位不表示已验证气密。
show_* 含磁条/紧固件占位，仅预览不导出；折叠 0 为摊开，105 为收起。
无角度锁定；胶条承载、磁吸力、翘曲与漏气需实装验证。运行本脚本执行几何检查。
"""

import math
import unittest

from b4dcad import circle, cube, cylinder, is_rendering, polygon, union

HEIGHT = 1000.0
SEGMENTS = 5
PITCH = HEIGHT / SEGMENTS
FIXED_WIDTH = 25.4
WINDOW_DEPTH_OFFSET = 5.3  # 窗户贴合面相对窗框向室内凸出。
COMMAND_STRIP_STACK = 1.0  # 占位值：实测胶条装好后的总厚度（含配对胶条）。
MAGNET_WIDTH = 12.7
MAGNET_THICKNESS = 1.0  # 占位值：单条磁条含背胶的厚度。
MAGNET_LAND = 15.0
TOP_ALLOWANCE = 8.0  # 顶段可裁/可改余量，不计入名义高度。
LAP_TOP = WINDOW_DEPTH_OFFSET - COMMAND_STRIP_STACK
FLAP_Z = LAP_TOP + 2 * MAGNET_THICKNESS
LAP_LEFT = -18.0
RIGHT_MAGNET_X = -16.5
LEFT_MAGNET_X = -100.6
FLAP_EXTENT = 127.0 - FIXED_WIDTH
THICKNESS = 2.4
RIB_HEIGHT = 6.0
RIB_WIDTH = 3.0
BED = 260.0
BARREL_RADIUS = 2.2
AXIS_Z = FLAP_Z + RIB_HEIGHT + 2 * BARREL_RADIUS + 0.8
EDGE = 0.3
PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BORE_DIAMETER = 1.0
BLIND_BOTTOM = 1.5
HINGE_LENGTH = 19.0
END_KNUCKLE = 6.0
AXIAL_GAP = 0.4
HINGE_STARTS = (25.0, PITCH - 60.0)
STRIP_WIDTH = (63 - 0.2 - 0.3) / 4
STRIP_HEIGHT = 46.0
STRIP_X = FIXED_WIDTH - STRIP_WIDTH - 0.8
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
            0 if fixed else FLAP_Z,
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
    for start in HINGE_STARTS:
        part += _hinge(start, False)
    return part.as_original().simplify(1e-5)


def fixed_segment():
    if LAP_TOP < THICKNESS:
        raise ValueError("胶条厚度使搭接底板小于结构板厚，需重新安排贴合面")
    low, high = SEAM / 2, PITCH - SEAM / 2
    # 连续搭接底板跨过铰链缝，磁条粘在左侧上表面；胶条在右侧背面。
    part = _box(LAP_LEFT, 8.0, low, high, 0, LAP_TOP)
    part += _box(EDGE, 8.0, low, high, LAP_TOP, FLAP_Z + RIB_HEIGHT)
    part += _box(7.5, FIXED_WIDTH, PAD_START, PAD_START + STRIP_HEIGHT, 0, LAP_TOP)
    for y in (PAD_START, PAD_START + STRIP_HEIGHT - THICKNESS):
        part += _rib_ramp(8.0, 1, y, y + THICKNESS, floor=LAP_TOP)
    for start in HINGE_STARTS:
        part += _hinge(start, True)
    return part.as_original().simplify(1e-5)


def magnetic_strips(moving, height=HEIGHT + TOP_ALLOWANCE):
    """全长软磁条占位；买来的磁条不作为打印件导出。"""
    z0 = LAP_TOP + MAGNET_THICKNESS if moving else LAP_TOP
    right_height = height if moving else min(height, HEIGHT)
    return _box(
        RIGHT_MAGNET_X,
        RIGHT_MAGNET_X + MAGNET_WIDTH,
        0,
        right_height,
        z0,
        z0 + MAGNET_THICKNESS,
    ) + _box(
        LEFT_MAGNET_X,
        LEFT_MAGNET_X + MAGNET_WIDTH,
        0,
        height,
        z0,
        z0 + MAGNET_THICKNESS,
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
    moving = union([flap_segment(i).move(y=i * PITCH) for i in range(SEGMENTS)])
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
        for part in parts:
            self.assertEqual(len(part.decompose()), 1)
            self.assertLessEqual(max(part.size().x, part.size().y), BED - 10)
            self.assertGreater(part.manifold.volume(), 0)

    def test_rotation_clearance(self):
        fixed = fixed_segment() + magnetic_strips(False, PITCH)
        moving = flap_segment(1) + magnetic_strips(True, PITCH)
        # 实体窗户/窗框和紧固件一起检查，不重复验证已实测的销、燕尾配合。
        fixed += _box(
            LEFT_MAGNET_X - 1,
            LEFT_MAGNET_X + MAGNET_LAND,
            0,
            PITCH,
            LAP_TOP - 3,
            LAP_TOP,
        )
        fixed += _box(
            LAP_LEFT,
            FIXED_WIDTH,
            0,
            PITCH,
            -COMMAND_STRIP_STACK - 3,
            -COMMAND_STRIP_STACK,
        )
        for seam in (0, PITCH):
            for x in BOLT_X:
                hardware, _ = _bolt_envelopes(x, seam)
                moving += hardware
        for angle in range(0, 111, 2):
            self.assert_clear(fixed, fold(moving, angle))

    def test_magnetic_lands(self):
        self.assertGreater(MAGNET_LAND, MAGNET_WIDTH)
        self.assertAlmostEqual(COMMAND_STRIP_STACK + LAP_TOP, WINDOW_DEPTH_OFFSET)
        flap = flap_segment(1)
        fixed = fixed_segment()
        for x in (LEFT_MAGNET_X, RIGHT_MAGNET_X):
            bearing = _box(x, x + MAGNET_WIDTH, 10, PITCH - 10, FLAP_Z, FLAP_Z + 0.1)
            self.assertAlmostEqual(
                (flap & bearing).manifold.volume(),
                MAGNET_WIDTH * (PITCH - 20) * 0.1,
                places=4,
            )
        bearing = _box(
            RIGHT_MAGNET_X,
            RIGHT_MAGNET_X + MAGNET_WIDTH,
            10,
            PITCH - 10,
            LAP_TOP - 0.1,
            LAP_TOP,
        )
        self.assertAlmostEqual(
            (fixed & bearing).manifold.volume(),
            MAGNET_WIDTH * (PITCH - 20) * 0.1,
            places=4,
        )

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
            STRIP_X, STRIP_X + STRIP_WIDTH, PAD_START, PAD_START + STRIP_HEIGHT, -1, 0
        )
        self.assert_clear(fixed, adhesive)
        self.assertAlmostEqual(
            (adhesive.move(z=1) & fixed).manifold.volume(),
            STRIP_WIDTH * STRIP_HEIGHT,
            places=3,
        )


if is_rendering():
    for _i in range(SEGMENTS):
        globals()[f"flap_{_i + 1}"] = flap_segment(_i).align(xmin=0, ymin=0, zmin=0)
    mount = fixed_segment().align(xmin=0, ymin=0, zmin=0)
    show_open = assembly(0)
    show_folded = assembly(105)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
