"""实验性窗框折叠挡片，单位 mm；摊开总高 900、总宽 127，固定侧宽 25.4。

flap_1..4 各印一件，mount 印四件，splice 印六件；均底面朝下平放。
主件最长 233，适配 260×260 平台。
两枚燕尾从板面法向嵌合定位，接缝及跨缝加强片胶粘；先在平面上拼好整片。
加强片覆盖燕尾，位于加强筋之间。接缝不是免胶卡扣。
加强筋内侧根部连续补 45° 斜面；胶条背板两端各加一片 45° 三角撑。
每段固定侧一条中号胶条，粘贴区 15.625×46，背面朝窗框；拉片朝 -Y。
粘贴区上下各留 25 高开放空间，正面可按住背板，拉片从下方缺口露出。
安装时按实际胶条的非粘性拉片位置调整粘贴，勿将拉片粘住或压在背板后。
四段固定座先穿销与整片对齐，再贴窗框，避免各段轴线错位。
八根直径 0.8、长 16 的裸回形针销从各铰链 +Y 端插入，-Y 端有 1.5 厚盲底；
装好后用小片胶带封住入口防销退出，勿把胶粘进转动面。
板厚 2.4、加强筋总高 6；孔径 1.0，轴向间隙 0.4，燕尾单边间隙 0.2。
show_open / show_folded 为摊开和折叠 105° 预览（0° 为摊开）。
本版自由铰链，不含角度锁定；靠窗框放置的角度及风下稳定性需实装验证。
胶条承载、板件翘曲和胶接强度尚未实测。运行本脚本执行内置几何测试。
"""

import math
import unittest

from b4dcad import circle, cube, cylinder, is_rendering, polygon, union

HEIGHT = 900.0
SEGMENTS = 4
PITCH = HEIGHT / SEGMENTS
FIXED_WIDTH = 25.4
FLAP_EXTENT = 127.0 - FIXED_WIDTH
THICKNESS = 2.4
RIB_HEIGHT = 6.0
RIB_WIDTH = 3.0
BED = 260.0
BARREL_RADIUS = 2.2
AXIS_Z = 3.2
EDGE = 4.6
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
SPLICE_WIDTH = 25.0
SPLICE_LENGTH = 42.0
GLUE_GAP = 0.15


def _box(x0, x1, y0, y1, z0=0, z1=THICKNESS):
    return cube(x1 - x0, y1 - y0, z1 - z0).move(x=x0, y=y0, z=z0)


def _rib_ramp(x, direction, y0, y1):
    """XZ 三角截面沿 Y 拉伸，斜面水平宽度等于筋高差。"""
    rise = RIB_HEIGHT - THICKNESS
    return (
        polygon(
            [
                (x - direction * 0.1, THICKNESS - 0.1),
                (x - direction * 0.1, RIB_HEIGHT),
                (x, RIB_HEIGHT),
                (x + direction * (rise + 0.1), THICKNESS - 0.1),
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
        barrel += _box(-BARREL_RADIUS, BARREL_RADIUS, a, b, 0, AXIS_Z)
        barrel += _box(
            0 if fixed else -EDGE - 0.5,
            EDGE + 0.5 if fixed else 0,
            a,
            b,
            0,
            AXIS_Z,
        )
        barrel -= _bore(a + BLIND_BOTTOM if fixed and low == 0 else a - 0.1, b + 0.1)
        pieces.append(barrel)
    return union(pieces)


def _tab(x, seam, clearance=0):
    # 从板面法向嵌合的平面燕尾，根部伸回板内 1 mm。
    profile = polygon([(-6, -1), (6, -1), (10, JOINT_DEPTH), (-10, JOINT_DEPTH)])
    if clearance:
        profile = profile.offset(clearance, "miter")
    return profile.extrude(THICKNESS + (2 if clearance else 0)).move(
        x=x, y=seam, z=-1 if clearance else 0
    )


def flap_segment(index):
    if not 0 <= index < SEGMENTS:
        raise ValueError("segment index out of range")
    low = SEAM / 2 if index else 0
    high = PITCH - SEAM / 2 if index < SEGMENTS - 1 else PITCH
    part = _box(-FLAP_EXTENT, -EDGE, low, high)
    for x in (-FLAP_EXTENT, -54.0, -EDGE - RIB_WIDTH):
        part += _box(x, x + RIB_WIDTH, low, high, THICKNESS, RIB_HEIGHT)
        if x > -FLAP_EXTENT:
            part += _rib_ramp(x, -1, low, high)
        if x + RIB_WIDTH < -EDGE:
            part += _rib_ramp(x + RIB_WIDTH, 1, low, high)
    for x in JOINT_X:
        if index < SEGMENTS - 1:
            part += _tab(x, PITCH)
        if index:
            part -= _tab(x, 0, JOINT_CLEARANCE)
    for start in HINGE_STARTS:
        part += _hinge(start, False)
    return part.as_original().simplify(1e-5)


def fixed_segment():
    # 窄脊柱保留连续轴线；胶条区的上下开口一直通向右侧。
    part = _box(EDGE, 8.0, SEAM / 2, PITCH - SEAM / 2, 0, RIB_HEIGHT)
    part += _box(7.5, FIXED_WIDTH, PAD_START, PAD_START + STRIP_HEIGHT)
    for y in (PAD_START, PAD_START + STRIP_HEIGHT - THICKNESS):
        part += _rib_ramp(8.0, 1, y, y + THICKNESS)
    for start in HINGE_STARTS:
        part += _hinge(start, True)
    return part.as_original().simplify(1e-5)


def splice_plate():
    return cube(SPLICE_WIDTH, SPLICE_LENGTH, 2.0)


def _splice_at(x, seam):
    return splice_plate().move(
        x=x - SPLICE_WIDTH / 2,
        y=seam + JOINT_DEPTH / 2 - SPLICE_LENGTH / 2,
        z=THICKNESS + GLUE_GAP,
    )


def fold(part, angle):
    return part.move(z=-AXIS_Z).rotate(y=angle).move(z=AXIS_Z)


def assembly(angle):
    fixed = union([fixed_segment().move(y=i * PITCH) for i in range(SEGMENTS)])
    moving = union([flap_segment(i).move(y=i * PITCH) for i in range(SEGMENTS)])
    for seam in range(1, SEGMENTS):
        for x in JOINT_X:
            moving += _splice_at(x, seam * PITCH)
    return fixed + fold(moving, angle)


class GeometryTests(unittest.TestCase):
    def assert_clear(self, a, b):
        self.assertLess(abs((a & b).manifold.volume()), 1e-5)

    def test_printable_connected_parts(self):
        parts = [fixed_segment(), splice_plate()]
        parts.extend(flap_segment(i) for i in range(SEGMENTS))
        for part in parts:
            self.assertEqual(len(part.decompose()), 1)
            self.assertLessEqual(max(part.size().x, part.size().y), BED - 10)
            self.assertGreater(part.manifold.volume(), 0)

    def test_rotation_clearance(self):
        fixed, moving = fixed_segment(), flap_segment(1)
        for angle in range(0, 111, 2):
            self.assert_clear(fixed, fold(moving, angle))

    def test_seams_and_splices(self):
        for index in range(SEGMENTS - 1):
            lower = flap_segment(index)
            upper = flap_segment(index + 1).move(y=PITCH)
            self.assert_clear(lower, upper)
            for x in JOINT_X:
                strap = _splice_at(x, PITCH)
                self.assert_clear(strap, lower + upper)
                # 胶层下必须有两侧有效搭接，而不是加强片悬空。
                footprint = strap.move(z=-2)
                self.assertGreater((footprint & lower).manifold.volume(), 200)
                self.assertGreater((footprint & upper).manifold.volume(), 200)
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
    splice = splice_plate()
    show_open = assembly(0)
    show_folded = assembly(105)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
