"""直边锥形燕尾，仅外端两尖角改为 R3 圆角的小试件，单位 mm。

打印通用 male 一件，female_000 / female_005 / female_010 分别一/二/三个凸点。
最终直边侧壁法向余量分别为0 / 0.05 / 0.10；先试000或005，010可作松配合对照。
只改外端两角，颈部与斜直边保留；R3 沿厚度保持，与各层直边相切，根部尖角埋在板内。
两件都平底朝下打印；薄板2.4，接缝局部厚4，用45°斜坡过渡。
沿 Z 每升高1，轮廓向外扩大0.2；沿 -Z 装入时逐渐收紧，沿 +Z 拆出。
主板、M3孔位和锥度沿用直边试件，但圆角配合应使用本文件的一组 male/female。
000是名义接触；正余量版本压到底仍有侧隙，若胶粘应先按胶材要求试配。
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
CORNER_RADIUS = 3.0
ARC_STEPS = 32
CLEARANCES = (0.0, 0.05, 0.10)
HOLE_DIAMETER = 3.4
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4
WASHER_ID = 3.2
WASHER_OD = 7.0
WASHER_THICKNESS = 0.5
BOLT_Y = 4.0
# 固定孔轴取锥面中高处的交界，垫圈在上下两个面均须跨住两件。
_side_slope = (TIP_HALF - NECK_HALF) / (TAIL_DEPTH - TAIL_ROOT)
_bolt_x = (
    NECK_HALF
    + _side_slope * (BOLT_Y - TAIL_ROOT)
    + TAPER * JOINT_HEIGHT / 2 * (1 + _side_slope**2) ** 0.5
)
BOLT_X = (-_bolt_x, _bolt_x)


def _profile_points(offset):
    """仅外端两角 R3；各层直边平移、圆心随动，固定顶点对应。"""
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
    # 各层直边平行扩缩，圆心随之移动，圆弧半径始终保持 R3。
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


def _tapered(clearance, bottom, top):
    # 圆角梯形是凸轮廓；两端层凸包连接直边平行、圆角等半径的各层轮廓，避免曲线 loft 错配顶点。
    return hull_points(
        [
            (x, y, z)
            for z in (bottom, top)
            for x, y in _profile_points(TAPER * z + clearance)
        ]
    )


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


def make_pair(clearance=0, index=0):
    if clearance < 0:
        raise ValueError("试件不预设过盈；负间隙会阻止名义位置完全就位")
    male = _plate(True) + _tapered(0, 0, JOINT_HEIGHT)
    female = _plate(False) - _tapered(clearance, -0.1, JOINT_HEIGHT + 0.1)
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
    _male, _ = make_pair()
    male = _male.align(xmin=0, ymin=0, zmin=0)
    for _i, _clearance in enumerate(CLEARANCES):
        _, _female = make_pair(_clearance, _i)
        _suffix = f"{round(_clearance * 100):03d}"
        globals()[f"female_{_suffix}"] = _female.align(xmin=0, ymin=0, zmin=0).move(
            x=44 * _i, y=48
        )
        globals()[f"show_seated_{_suffix}"] = (_male + _female + hardware()).move(
            x=44 * _i, y=125
        )
    show_inserting = (make_pair(0)[1] + _male.move(z=3)).move(x=145)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
