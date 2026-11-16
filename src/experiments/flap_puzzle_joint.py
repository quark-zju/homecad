"""圆头细颈拼图式 Z 向压合接头试件，单位 mm；平底朝下打印。

male 一件通用，female_loose_005 / female_nominal_000 / female_tight_003
分别一/二/三个凸点，对应缩放余量 +0.05 / 0 / -0.03；从一凸点开始试。
板厚2.4，局部加厚至4，45°过渡；轮廓由相切三次 Bezier 曲线采样。
以 (0,2) 为中心相似缩放：比例 1+(0.2*Z+余量)/8；余量不是全轮廓法向间隙。
竖直沿 -Z 压入时渐紧，沿 +Z 拆卸；勿沿板长方向硬推。
负余量用于补偿实印偏松；理想刚体会在高出0.15处接触，不能完全坐平。
不要靠螺丝强拉过盈件。PETG 弹性、首层扩边及实际松紧需实印验证。

每组两套 M3×8、普通螺母、四枚 ID3.2/OD7/厚0.5 平垫圈。
孔骑在接口上，两面垫圈均桥接两件；先手压就位，再从底面穿螺丝，交替轻拧。
垫圈不可省去，无悬空搭接底层或独立打印拼接片。底部紧固件会突出，
这是开口区域接头试验，不代表最终窗框避让或气密方案。
show_* 仅预览不导出；运行脚本执行内置几何检查。
"""

import unittest

from b4dcad import circle, cylinder, is_rendering, polygon, union

WIDTH = 36.0
LENGTH = 26.0
THICKNESS = 2.4
JOINT_HEIGHT = 4.0
TAPER = 0.2
SCALE_RADIUS = 8.0
CURVE_CENTER_Y = 2.0
CLEARANCES = (0.05, 0.0, -0.03)
HOLE_DIAMETER = 3.4
BOLT_LENGTH = 8.0
NUT_HEIGHT = 2.4
WASHER_ID = 3.2
WASHER_OD = 7.0
WASHER_THICKNESS = 0.5
# 螺孔位于球头最宽处的中高层交界线上。
BOLT_Y = 7.0
BOLT_X = (-8.4, 8.4)


def _bezier(points, steps=32):
    result = []
    for i in range(steps):
        t = i / steps
        result.append(
            tuple(
                (1 - t) ** 3 * points[0][j]
                + 3 * (1 - t) ** 2 * t * points[1][j]
                + 3 * (1 - t) * t * t * points[2][j]
                + t**3 * points[3][j]
                for j in (0, 1)
            )
        )
    return result


def _outline():
    # 接续处共享切线：细颈平滑张开为圆头，根部角埋入主板。
    right = []
    for curve in (
        ((6, -3), (6, -1), (3, 0), (3, 2)),
        ((3, 2), (3, 4), (8, 4), (8, 7)),
        ((8, 7), (8, 11), (4, 14), (0, 14)),
    ):
        right.extend(_bezier(curve))
    right.append((0, 14))
    return right + [(-x, y) for x, y in reversed(right[:-1])]


def _profile(expansion):
    # 同心相似缩放，非等距法向 offset；缩放拉伸避免曲线 loft 顶点错配。
    scale = 1 + expansion / SCALE_RADIUS
    return polygon(
        [
            (x * scale, CURVE_CENTER_Y + (y - CURVE_CENTER_Y) * scale)
            for x, y in _outline()
        ]
    )


def _tapered(clearance, bottom, top):
    bottom_scale = 1 + (TAPER * bottom + clearance) / SCALE_RADIUS
    top_scale = 1 + (TAPER * top + clearance) / SCALE_RADIUS
    ratio = top_scale / bottom_scale
    return (
        _profile(TAPER * bottom + clearance)
        .move(y=-CURVE_CENTER_Y)
        .extrude(top - bottom, scale_top=(ratio, ratio))
        .move(y=CURVE_CENTER_Y, z=bottom)
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
            (16 + ramp, THICKNESS),
            (16, JOINT_HEIGHT),
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
    if clearance < -0.1:
        raise ValueError("过盈过大；试件仅用于小幅补偿实测松量")
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
            if clearance >= 0:
                self.assert_clear(male, female)
            else:
                self.assertGreater((male & female).manifold.volume(), 0.01)
                stop = -clearance / TAPER
                self.assert_clear(male.move(z=stop + 0.001), female)
                self.assertGreater(
                    (male.move(z=stop / 2) & female).manifold.volume(), 0.01
                )
            for lift in (0.2, 0.5, 1, 2, 4, 8):
                self.assert_clear(male.move(z=lift), female)
            # 未压到底时容许横向晃动，压到底后相同位移受到侧壁阻挡。
            self.assert_clear(male.move(x=0.05, z=2), female)
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
        _suffix = ("loose_005", "nominal_000", "tight_003")[_i]
        globals()[f"female_{_suffix}"] = _female.align(xmin=0, ymin=0, zmin=0).move(
            x=44 * _i, y=48
        )
        # 负余量预览停在刚接触的高度，理想刚体不能完全压平。
        _lift = max(0, -_clearance / TAPER)
        globals()[f"show_fit_{_suffix}"] = (_male.move(z=_lift) + _female).move(
            x=44 * _i, y=125
        )
    show_hardware_nominal = (_male + make_pair(0)[1] + hardware()).move(x=145, y=125)
    show_inserting = (make_pair(0)[1] + _male.move(z=3)).move(x=145)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
