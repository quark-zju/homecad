"""R1 圆角锥形燕尾接头，单位 mm；通过 PETG、0.4 mm 喷嘴、0.2 mm 层高试印。

male、female 各打印一件，均平底朝下。板厚2.4，接缝局部厚4，45°斜坡过渡。
female 槽仅在X向放宽约0.30%，Y向零余量；配合轮廓沿Z每升高1向外扩大0.2。
沿-Z压入逐渐收紧，沿+Z拆出。两套M3×8及普通螺母负责Z向固定，
四枚ID3.2/OD7/厚0.5平垫圈在两面跨缝承托；底面紧固件外凸。
运行脚本检查装配、退出路径及垫圈承托。
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
FILLET_RADIUS = 1.0
ARC_STEPS = 32
FEMALE_X_SCALE = 1 + 0.025 / 8.4
HOLE_DIAMETER = 3.4
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4
WASHER_ID = 3.2
WASHER_OD = 7.0
WASHER_THICKNESS = 0.5
BOLT_Y = 5.2
SIDE_SLOPE = (TIP_HALF - NECK_HALF) / (TAIL_DEPTH - TAIL_ROOT)
SIDE_NORM = math.sqrt(1 + SIDE_SLOPE**2)
# 孔心在斜直边的中高层交界上，使垫圈跨住两件。
BOLT_X = tuple(
    sign
    * (
        NECK_HALF
        + SIDE_SLOPE * (BOLT_Y - TAIL_ROOT)
        + TAPER * JOINT_HEIGHT / 2 * SIDE_NORM
    )
    for sign in (-1, 1)
)


def _profile_points(offset):
    """外端两角的切圆弧；各层保持半径不变，固定顶点对应。"""
    cy = TAIL_DEPTH + offset - FILLET_RADIUS
    cx = (
        NECK_HALF + SIDE_SLOPE * (cy - TAIL_ROOT) + (offset - FILLET_RADIUS) * SIDE_NORM
    )
    if cx <= 0 or FILLET_RADIUS <= 0:
        raise ValueError("圆角过大，无法保留顶部直边")
    # 各层直边平行扩缩，圆心随之移动，圆弧半径保持不变。
    root_half = NECK_HALF + offset * (SIDE_NORM - SIDE_SLOPE)
    points = [(-root_half, TAIL_ROOT - offset), (root_half, TAIL_ROOT - offset)]
    angle = math.atan(SIDE_SLOPE)
    for center_x, begin, end in (
        (cx, -angle, math.pi / 2),
        (-cx, math.pi / 2, math.pi + angle),
    ):
        for i in range(ARC_STEPS + 1):
            theta = begin + (end - begin) * i / ARC_STEPS
            points.append(
                (
                    center_x + FILLET_RADIUS * math.cos(theta),
                    cy + FILLET_RADIUS * math.sin(theta),
                )
            )
    return points


def _root_blend(bottom, top):
    """颈部凹角的圆滑补料；直线挤出后剪切，使每层半径保持不变。"""
    side_x = NECK_HALF - SIDE_SLOPE * TAIL_ROOT
    cx = side_x + FILLET_RADIUS * (SIDE_NORM + SIDE_SLOPE)
    cy = FILLET_RADIUS
    end_y = cy + FILLET_RADIUS * SIDE_SLOPE / SIDE_NORM
    tip_start_y = (
        TAIL_DEPTH + TAPER * bottom - FILLET_RADIUS * (1 + SIDE_SLOPE / SIDE_NORM)
    )
    if end_y >= tip_start_y:
        raise ValueError("颈部与外端圆角相碰，已没有直边过渡")
    # 与原斜边重叠0.05，保证补料融合；暴露的颈部圆弧与端面、斜边均相切。
    points = [(side_x - 0.05, -0.05), (cx, -0.05)]
    finish = -math.pi - math.atan(SIDE_SLOPE)
    for i in range(ARC_STEPS + 1):
        theta = -math.pi / 2 + (finish + math.pi / 2) * i / ARC_STEPS
        points.append(
            (cx + FILLET_RADIUS * math.cos(theta), cy + FILLET_RADIUS * math.sin(theta))
        )
    patch = polygon(points).extrude(top - bottom).move(z=bottom)
    patch = patch.transform(
        [
            [1, 0, TAPER * SIDE_NORM, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
        ]
    )
    return patch + patch.mirror(x=1)


def _tapered(bottom, top):
    # 主凸轮廓用凸包连接；颈部凹圆角另加剪切挤出的补料，不能整体取凸包。
    tip = hull_points(
        [(x, y, z) for z in (bottom, top) for x, y in _profile_points(TAPER * z)]
    )
    return tip + _root_blend(bottom, top)


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


def make_pair():
    male = _plate(True) + _tapered(0, JOINT_HEIGHT)
    cavity = _tapered(-0.1, JOINT_HEIGHT + 0.1).scale(x=FEMALE_X_SCALE)
    female = _plate(False) - cavity
    for x in BOLT_X:
        bore = cylinder(r=HOLE_DIAMETER / 2, h=JOINT_HEIGHT + 2, fn=64).move(
            x=x, y=BOLT_Y, z=-1
        )
        male -= bore
        female -= bore
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
        for part in make_pair():
            self.assertEqual(len(part.decompose()), 1)
            self.assertGreater(part.manifold.volume(), 0)
            self.assertAlmostEqual(part.bounding_box()[2], 0, places=6)
            self.assertLess(max(part.size().x, part.size().y), 50)

    def test_vertical_insertion_and_tightening(self):
        male, female = make_pair()
        for lift in (0, 0.1, 0.5, 1, 2, 4, 8):
            self.assert_clear(male.move(z=lift), female)
        # 未压到底时容许横向晃动，压到底后相同位移受到侧壁阻挡。
        self.assert_clear(male.move(x=0.3, z=2), female)
        self.assertGreater((male.move(x=0.3) & female).manifold.volume(), 0.1)

    def test_directional_fit(self):
        male, female = make_pair()
        # 同为最终Z位置：允许少量X横移，但向前Y移动会碰到名义端面。
        self.assert_clear(male.move(x=0.015), female)
        self.assertGreater((male.move(y=0.03) & female).manifold.volume(), 0.01)

    def test_y_retention_in_both_directions(self):
        male, female = make_pair()
        # X放宽会允许接缝沿-Y拉开，零Y缩放并不等于零活动量。
        self.assert_clear(male.move(y=-0.05), female)
        # 就位后，两方向都应在0.1以内受阻；同时覆盖少量X偏移。
        for x in (-0.015, 0, 0.015):
            for y in (-0.1, 0.1):
                with self.subTest(x=x, y=y):
                    self.assertGreater(
                        (male.move(x=x, y=y) & female).manifold.volume(), 1e-5
                    )

    def test_pull_apart_path_has_substantial_interference(self):
        male, female = make_pair()
        # 扫描退出路径，容许0.2的Z抬升，排除仅有浅干涉的情况。
        # 1 mm³仅作几何门槛，不模拟打印件的弹性或强度。
        for x in (-0.03, 0, 0.03):
            for z in (0, 0.2):
                for step in range(2, 33):
                    pull = step * 0.25
                    with self.subTest(x=x, pull=pull, z=z):
                        collision = male.move(x=x, y=-pull, z=z) & female
                        self.assertGreater(collision.manifold.volume(), 1.0)

    def test_hardware_and_washer_bearing(self):
        self.assertGreaterEqual(
            BOLT_LENGTH - JOINT_HEIGHT - 2 * WASHER_THICKNESS - NUT_HEIGHT, 0.5
        )
        male, female = make_pair()
        self.assert_clear(male + female, hardware())
        for washer in washers():
            # 两侧垫圈分别向实体移动0.5，用重叠体积验证同时压住两件。
            bottom = washer.bounding_box()[2] < 0
            bearing = washer.move(z=WASHER_THICKNESS if bottom else -WASHER_THICKNESS)
            for part in (male, female):
                self.assertGreater((bearing & part).manifold.volume(), 1)
        for x in BOLT_X:
            wrench = cylinder(r=4.5, h=15, fn=48).move(
                x=x, y=BOLT_Y, z=JOINT_HEIGHT + WASHER_THICKNESS + NUT_HEIGHT
            )
            self.assert_clear(male + female, wrench)


def show_objects():
    male, female = make_pair()
    return {
        "male": male.align(xmin=0, ymin=0, zmin=0),
        "female": female.align(xmin=0, ymin=0, zmin=0).move(y=48),
        "show_seated": (male + female + hardware()).move(y=125),
        "show_inserting": (female + male.move(z=3)).move(x=80),
    }


if is_rendering():
    globals().update(show_objects())

if __name__ == "__main__" and not is_rendering():
    unittest.main()
