"""直边锥形燕尾，外端尖角与颈部凹角均为 R1 圆角的小试件，单位 mm。

打印 male 与 female_xloose_yzero 各一件；female 一个凸点标记。
X参照puzzle宽松版，Y参照零余量版；不再同时放大两个方向。
取厚度中层puzzle的X增幅：(8+0.4+0.05)/(8+0.4)，即约1.005952倍。
此比例应用于本件名义female槽，X各处实际间隙依位置而异，孔位不缩放。
Y保持名义尺寸，前端可接触；X间隙与斜边耦合，反向初始松动约0.11。
防拉开检查覆盖整段退出路径；不能仅用就位附近的微小碰撞判定已卡住。
male外端凸角与颈部凹角均为R1，与各层直边相切；female随X余量横向略放宽。
两只M3孔位于Y=5.2、横向约±8.68，垫圈跨住接缝两件。
两件都平底朝下打印；薄板2.4，接缝局部厚4，用45°斜坡过渡。
沿 Z 每升高1，轮廓向外扩大0.2；沿 -Z 装入时逐渐收紧，沿 +Z 拆出。
主板和锥度沿用直边试件；M3孔位已调整，圆角配合应使用本文件的一组male/female。
X方向仍有名义侧隙，若胶粘应先按胶材要求试配。
圆角和间隙保留为参数；不预留过盈，不用螺丝强拉卡住的试件。

每组两套 M3×8、普通螺母及四枚 ID3.2/OD7/厚0.5 平垫圈；两面垫圈都跨缝压住两件。
先手压就位再交替轻拧。M3负责Z向固定，垫圈不可省；可在试配后自行选择胶粘。
底面紧固件外凸；这是连接试件，不是最终窗框避让或气密设计。
show_*仅预览不导出；运行本脚本执行装配、插入和垫圈承托检查。
"""

import math
import unittest

from b4dcad import circle, cylinder, hull_points, is_rendering, polygon, union

WIDTH = 36.0
LENGTH = 26.0
THICKNESS = 2.4
JOINT_HEIGHT = 4.0
TAPER = 0.2
TAIL_DEPTH = 10.0
TAIL_ROOT = -1.0
NECK_HALF = 6.0
TIP_HALF = 10.0
CORNER_RADIUS = 1.0
ROOT_RADIUS = 1.0
ARC_STEPS = 32
PUZZLE_ALLOWANCE_X = 0.05
PUZZLE_ALLOWANCE_Y = 0.0
PUZZLE_SCALE_RADIUS = 8.0
PUZZLE_CENTER_Y = 2.0
FIT_REFERENCE = PUZZLE_SCALE_RADIUS + TAPER * JOINT_HEIGHT / 2
CLEARANCES = (PUZZLE_ALLOWANCE_X,)
HOLE_DIAMETER = 3.4
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4
WASHER_ID = 3.2
WASHER_OD = 7.0
WASHER_THICKNESS = 0.5
BOLT_Y = 5.2
# 横向取中高层交界；按孔所在的直边或外端圆弧计算，保持垫圈跨住两件。
_side_slope = (TIP_HALF - NECK_HALF) / (TAIL_DEPTH - TAIL_ROOT)
_side_norm = math.sqrt(1 + _side_slope**2)
_mid_offset = TAPER * JOINT_HEIGHT / 2
_fillet_y = TAIL_DEPTH + _mid_offset - CORNER_RADIUS
_fillet_x = (
    NECK_HALF
    + _side_slope * (_fillet_y - TAIL_ROOT)
    + (_mid_offset - CORNER_RADIUS) * _side_norm
)
if BOLT_Y < ROOT_RADIUS * (1 + _side_slope / _side_norm):
    raise ValueError("螺孔应位于颈部圆角末端之后")
if BOLT_Y < _fillet_y - CORNER_RADIUS * _side_slope / _side_norm:
    _bolt_x = NECK_HALF + _side_slope * (BOLT_Y - TAIL_ROOT) + _mid_offset * _side_norm
else:
    _bolt_x = _fillet_x + math.sqrt(CORNER_RADIUS**2 - (BOLT_Y - _fillet_y) ** 2)
BOLT_X = (-_bolt_x, _bolt_x)


def _profile_points(offset):
    """外端两角按 CORNER_RADIUS；各层直边平移、圆心随动，固定顶点对应。"""
    slope = (TIP_HALF - NECK_HALF) / (TAIL_DEPTH - TAIL_ROOT)
    normal_length = math.sqrt(1 + slope * slope)
    cy = TAIL_DEPTH + offset - CORNER_RADIUS
    cx = (
        NECK_HALF
        + slope * (cy - TAIL_ROOT)
        + offset * normal_length
        - CORNER_RADIUS * normal_length
    )
    if cx <= 0 or CORNER_RADIUS <= 0:
        raise ValueError("圆角过大，无法保留顶部直边")
    # 各层直边平行扩缩，圆心随之移动，圆弧半径保持不变。
    root_half = NECK_HALF + offset * (normal_length - slope)
    points = [(-root_half, TAIL_ROOT - offset), (root_half, TAIL_ROOT - offset)]
    radius = CORNER_RADIUS
    angle = math.atan(slope)
    for center_x, begin, end in (
        (cx, -angle, math.pi / 2),
        (-cx, math.pi / 2, math.pi + angle),
    ):
        for i in range(ARC_STEPS + 1):
            theta = begin + (end - begin) * i / ARC_STEPS
            points.append(
                (center_x + radius * math.cos(theta), cy + radius * math.sin(theta))
            )
    return points


def _root_blend(clearance, bottom, top):
    """颈部凹角的圆滑补料；直线挤出后剪切，使每层半径保持不变。"""
    slope = (TIP_HALF - NECK_HALF) / (TAIL_DEPTH - TAIL_ROOT)
    norm = math.sqrt(1 + slope * slope)
    side_x = NECK_HALF - slope * TAIL_ROOT
    cx = side_x + ROOT_RADIUS * (norm + slope)
    cy = ROOT_RADIUS
    end_y = cy + ROOT_RADIUS * slope / norm
    tip_start_y = (
        TAIL_DEPTH + TAPER * bottom + clearance - CORNER_RADIUS * (1 + slope / norm)
    )
    if end_y >= tip_start_y:
        raise ValueError("颈部与外端圆角相碰，已没有直边过渡")
    # 与原斜边重叠0.05，保证补料融合；暴露的颈部圆弧与端面、斜边均相切。
    points = [(side_x - 0.05, -0.05), (cx, -0.05)]
    finish = -math.pi - math.atan(slope)
    for i in range(ARC_STEPS + 1):
        theta = -math.pi / 2 + (finish + math.pi / 2) * i / ARC_STEPS
        points.append(
            (cx + ROOT_RADIUS * math.cos(theta), cy + ROOT_RADIUS * math.sin(theta))
        )
    patch = polygon(points).extrude(top - bottom).move(z=bottom)
    patch = patch.transform(
        [
            [1, 0, TAPER * norm, clearance * norm],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
        ]
    )
    return patch + patch.mirror(x=1)


def _tapered(clearance, bottom, top):
    # 主凸轮廓用凸包连接；颈部凹圆角另加剪切挤出的补料，不能整体取凸包。
    tip = hull_points(
        [
            (x, y, z)
            for z in (bottom, top)
            for x, y in _profile_points(TAPER * z + clearance)
        ]
    )
    return tip + _root_blend(clearance, bottom, top)


def _plate(male):
    ramp = JOINT_HEIGHT - THICKNESS
    if male:
        points = [
            (-LENGTH, 0),
            (0, 0),
            (0, JOINT_HEIGHT),
            (-6, JOINT_HEIGHT),
            (-6 - ramp, THICKNESS),
            (-LENGTH, THICKNESS),
        ]
    else:
        points = [
            (0, 0),
            (LENGTH, 0),
            (LENGTH, THICKNESS),
            (12 + ramp, THICKNESS),
            (12, JOINT_HEIGHT),
            (0, JOINT_HEIGHT),
        ]
    return polygon(points).extrude(WIDTH).rotate(x=90, z=90).move(x=-WIDTH / 2)


def _dots(index, male):
    y = -19 if male else 19
    return union(
        [
            cylinder(r=0.75, h=0.42, fn=32).move(
                x=-3 + i * 2.5, y=y, z=THICKNESS - 0.02
            )
            for i in range(index + 1)
        ]
    )


def make_pair(clearance=PUZZLE_ALLOWANCE_X, index=0):
    if clearance < 0:
        raise ValueError("试件不预设过盈；负间隙会阻止名义位置完全就位")
    male = _plate(True) + _tapered(0, 0, JOINT_HEIGHT)
    # 仅用puzzle宽松版在中层的X放大比例；Y名义槽边界不变。
    cavity = (
        _tapered(0, -0.1, JOINT_HEIGHT + 0.1)
        .move(y=-PUZZLE_CENTER_Y)
        .scale(
            x=1 + clearance / FIT_REFERENCE, y=1 + PUZZLE_ALLOWANCE_Y / FIT_REFERENCE
        )
        .move(y=PUZZLE_CENTER_Y)
    )
    female = _plate(False) - cavity
    for x in BOLT_X:
        bore = cylinder(r=HOLE_DIAMETER / 2, h=JOINT_HEIGHT + 2, fn=64).move(
            x=x, y=BOLT_Y, z=-1
        )
        male -= bore
        female -= bore
    female += _dots(index, False)
    return tuple(part.as_original().simplify(1e-5) for part in (male, female))


def washers():
    ring = circle(r=WASHER_OD / 2, fn=64) - circle(r=WASHER_ID / 2, fn=64)
    return tuple(
        ring.extrude(WASHER_THICKNESS).move(x=x, y=BOLT_Y, z=z)
        for x in BOLT_X
        for z in (-WASHER_THICKNESS, JOINT_HEIGHT)
    )


def hardware():
    pieces = list(washers())
    for x in BOLT_X:
        shaft = cylinder(r=1.5, h=BOLT_LENGTH, fn=64).move(
            x=x, y=BOLT_Y, z=-WASHER_THICKNESS
        )
        head = cylinder(r=3.2, h=3, fn=64).move(x=x, y=BOLT_Y, z=-WASHER_THICKNESS - 3)
        nut = cylinder(r=5.5 / 3**0.5, h=NUT_HEIGHT, fn=6)
        nut -= cylinder(r=HOLE_DIAMETER / 2, h=NUT_HEIGHT, fn=64)
        pieces.extend(
            [shaft, head, nut.move(x=x, y=BOLT_Y, z=JOINT_HEIGHT + WASHER_THICKNESS)]
        )
    return union(pieces)


class GeometryTests(unittest.TestCase):
    def assert_clear(self, a, b):
        self.assertLess(abs((a & b).manifold.volume()), 1e-5)

    def test_printable_connected_parts(self):
        for index, clearance in enumerate(CLEARANCES):
            for part in make_pair(clearance, index):
                self.assertEqual(len(part.decompose()), 1)
                self.assertGreater(part.manifold.volume(), 0)
                self.assertAlmostEqual(part.bounding_box()[2], 0, places=6)
                self.assertLess(max(part.size().x, part.size().y), 50)

    def test_vertical_insertion_and_tightening(self):
        for clearance in CLEARANCES:
            male, female = make_pair(clearance)
            for lift in (0, 0.1, 0.5, 1, 2, 4, 8):
                self.assert_clear(male.move(z=lift), female)
            # 未压到底时容许横向晃动，压到底后相同位移受到侧壁阻挡。
            self.assert_clear(male.move(x=0.3, z=2), female)
            self.assertGreater((male.move(x=0.3) & female).manifold.volume(), 0.1)

    def test_directional_fit(self):
        male, female = make_pair()
        # 同为最终Z位置：允许少量X横移，但向前Y移动会碰到名义端面。
        self.assert_clear(male.move(x=0.03), female)
        self.assertGreater((male.move(y=0.03) & female).manifold.volume(), 0.01)

    def test_y_retention_in_both_directions(self):
        male, female = make_pair()
        # X放宽会允许接缝沿-Y拉开，零Y缩放并不等于零活动量。
        self.assert_clear(male.move(y=-0.1), female)
        # 就位后，两方向都应在0.15以内受阻；同时覆盖少量X偏移。
        # 旧R3在-Y移动0.15时仍无碰撞，会被这个检查检出。
        for x in (-0.03, 0, 0.03):
            for y in (-0.15, 0.15):
                with self.subTest(x=x, y=y):
                    self.assertGreater(
                        (male.move(x=x, y=y) & female).manifold.volume(), 1e-5
                    )

    def test_pull_apart_path_has_substantial_interference(self):
        male, female = make_pair()
        # 旧R3在拉开0.5~2.5时只剩不足0.1 mm³的浅干涉，
        # 因而仅检查某个位置“有碰撞”会漏掉实际打印件能滑开的情况。
        # 扫描退出路径，并容许0.2的Z抬升；1 mm³仅作几何回归门槛，
        # 不表示打印件强度或保证不会弹性变形。M3仍需限制Z向抬升。
        for x in (-0.03, 0, 0.03):
            for z in (0, 0.2):
                for step in range(2, 33):
                    pull = step * 0.25
                    with self.subTest(x=x, pull=pull, z=z):
                        self.assertGreater(
                            (male.move(x=x, y=-pull, z=z) & female).manifold.volume(),
                            1.0,
                        )

    def test_hardware_and_washer_bearing(self):
        self.assertGreaterEqual(
            BOLT_LENGTH - JOINT_HEIGHT - 2 * WASHER_THICKNESS - NUT_HEIGHT, 0.5
        )
        for clearance in CLEARANCES:
            male, female = make_pair(clearance)
            self.assert_clear(male + female, hardware())
            for washer in washers():
                # 两侧垫圈分别向实体移动0.5，用重叠体积验证同时压住两件。
                bottom = washer.bounding_box()[2] < 0
                bearing = washer.move(
                    z=WASHER_THICKNESS if bottom else -WASHER_THICKNESS
                )
                for part in (male, female):
                    self.assertGreater((bearing & part).manifold.volume(), 1)
            for x in BOLT_X:
                wrench = cylinder(r=4.5, h=15, fn=48).move(
                    x=x, y=BOLT_Y, z=JOINT_HEIGHT + WASHER_THICKNESS + NUT_HEIGHT
                )
                self.assert_clear(male + female, wrench)


if is_rendering():
    _male, _female = make_pair()
    male = _male.align(xmin=0, ymin=0, zmin=0)
    female_xloose_yzero = _female.align(xmin=0, ymin=0, zmin=0).move(y=48)
    show_seated = (_male + _female + hardware()).move(y=125)
    show_inserting = (_female + _male.move(z=3)).move(x=80)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
