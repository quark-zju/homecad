"""局部加厚的 Z 向压合锥形燕尾试件，单位 mm；两件都底面朝下打印。

male_000/female_000、male_005/female_005、male_010/female_010 各一件。
一/二/三个凸点对应最终侧壁法向余量 0 / 0.05 / 0.10；先试三个点，再逐级收紧。
三个 male 的配合尺寸相同，凸点仅用于标记，可只印一个 male 配所有 female。
female_tight_003 / female_tight_006 用四/五个点标记，侧壁分别收小0.03/0.06。
这是补偿实际打印松量的过盈试验；理想刚体分别会在高出0.15/0.30处接触，
不能在几何上强压到底，需确认打印后的实际配合，不要靠螺丝强拉。
每块板约36×26，male 另带约11长燕尾；薄板2.4，接缝附近增厚到4，45°过渡。
燕尾沿 Z 每升高1，轮廓向外扩大0.2；竖直压入时从宽松逐渐收紧。
最终两板背面齐平，接缝端面不人为留缝；000 是名义接触，非预设过盈。
005/010 压到底仍保留侧壁余量，螺丝只夹紧Z，不能消除该余量。
首层象脚可能影响小间隙配合，需与真实打印的松紧一起观察。
从上方沿 -Z 装入，勿沿板长方向硬推。精确贴紧和 PETG 松紧需要实印验证。

每组另需两套 M3×8、普通螺母及四枚平垫圈（内径3.2、外径7、厚0.5）。
两只螺孔骑在交界线上，两面垫圈都跨住两件，负责 Z 向夹紧并限制翘起。
先手压就位，再从底面穿螺丝，放上垫圈与螺母，交替轻拧；不要用螺丝强拉卡死的试件。
底面螺丝头与垫圈会外凸；这是开口区域连接的试验，不代表最终窗框避让或气密方案。
连接不设悬空搭接底层，不使用独立打印 splice；垫圈不可省去。
拆卸时卸下螺丝后沿 +Z 提起。无胶、无弹性卡扣，松开螺丝后不保证自行锁住。
show_* 含紧固件占位，仅预览不导出。运行本脚本执行装配、插入和压紧承托检查。
"""

import unittest

from b4dcad import circle, cylinder, is_rendering, loft, polygon, union

WIDTH = 36.0
LENGTH = 26.0
THICKNESS = 2.4
JOINT_HEIGHT = 4.0
TAPER = 0.2
TAIL_DEPTH = 10.0
TAIL_ROOT = -1.0
NECK_HALF = 6.0
TIP_HALF = 10.0
CLEARANCES = (0.0, 0.05, 0.10)
TIGHT_CLEARANCES = (-0.03, -0.06)
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


def _profile(offset):
    profile = polygon(
        [
            (-NECK_HALF, TAIL_ROOT),
            (NECK_HALF, TAIL_ROOT),
            (TIP_HALF, TAIL_DEPTH),
            (-TIP_HALF, TAIL_DEPTH),
        ]
    )
    return profile.offset(offset, "miter") if offset else profile


def _tapered(clearance, bottom, top):
    return loft(
        [_profile(TAPER * z + clearance) for z in (bottom, top)],
        [bottom, top],
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
    male += _dots(index, True)
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
        for index, clearance in enumerate(CLEARANCES + TIGHT_CLEARANCES):
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

    def test_tight_females_stop_above_nominal(self):
        for clearance in TIGHT_CLEARANCES:
            male, female = make_pair(clearance)
            stop = -clearance / TAPER
            for lift in (stop + 0.001, stop + 0.1, stop + 1, stop + 4):
                self.assert_clear(male.move(z=lift), female)
            self.assertGreater((male & female).manifold.volume(), 0.1)
            self.assert_clear(male + female, hardware())

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
    for _i, _clearance in enumerate(CLEARANCES):
        _male, _female = make_pair(_clearance, _i)
        _suffix = f"{round(_clearance * 100):03d}"
        globals()[f"male_{_suffix}"] = _male.align(xmin=0, ymin=0, zmin=0).move(
            x=44 * _i
        )
        globals()[f"female_{_suffix}"] = _female.align(xmin=0, ymin=0, zmin=0).move(
            x=44 * _i, y=48
        )
        globals()[f"show_seated_{_suffix}"] = (_male + _female + hardware()).move(
            x=44 * _i, y=125
        )
    for _i, _clearance in enumerate(TIGHT_CLEARANCES):
        _male, _female = make_pair(_clearance, _i + 3)
        _suffix = f"{round(-_clearance * 100):03d}"
        globals()[f"female_tight_{_suffix}"] = _female.align(
            xmin=0, ymin=0, zmin=0
        ).move(x=44 * _i, y=86)
        globals()[f"show_tight_{_suffix}"] = (
            _female + _male.move(z=-_clearance / TAPER)
        ).move(x=160 + 44 * _i, y=125)
    _male, _female = make_pair(0.05, 1)
    show_inserting = (_female + _male.move(z=3)).move(x=145)

if __name__ == "__main__" and not is_rendering():
    unittest.main()
