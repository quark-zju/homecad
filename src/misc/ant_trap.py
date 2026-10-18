"""环形外坡蚂蚁陷阱，单位 mm；底杯和漏斗盖各打印一件。

底杯开口朝上；盖子已翻面，环形顶沿贴平台，两件默认免支撑。
gap 是中央出口下缘到底杯内底面的净高，不是入口孔径；
hole_diameter 独立控制中央孔径。诱饵放底杯，盖子向上拔出清理。
这是几何原型，防逃效果需要实测；不要把漏斗视为单向阀。

    b4dcad preview src/misc/ant_trap.py
    b4dcad stl src/misc/ant_trap.py ./stl

预览 show_assembly / show_section 为装配和半剖视图，不导出 STL。
wall 是底杯及定位圈径向壁厚，shell 是坡面竖向厚度；默认
45° 坡面法向厚度约 1.13 mm，建议 0.4 mm 喷嘴、0.2 mm 层高。
"""

import math

from b4dcad import cube, is_rendering, polygon


def get_parts(
    gap=5.0,
    hole_diameter=7.0,
    funnel_radius=22.0,
    height=30.0,
    ramp_angle=45.0,
    curvature=0.12,
    shell=1.6,
    wall=1.2,
    floor=1.2,
    clearance=0.3,
    collar_depth=2.4,
    toe_height=0.6,
    curve_steps=48,
    segments=192,
):
    """返回 (底杯, 盖子)，均为装配坐标，地面 z=0。

    外坡角相对于地面。曲面采用二次径向函数，curvature > 0 时
    中央较陡、外缘较缓，0 为直锥。限制两侧坡面至少 45°，以便
    盖子倒扣免支撑打印；较宽漏斗/较大 gap 需相应增加 height。
    clearance 为单侧径向间隙，不强行压配。顶沿压在底杯壁上，
    下垂定位圈套在底杯外侧；装配高度不依赖摩擦力。
    """
    positive = (
        gap,
        hole_diameter,
        funnel_radius,
        height,
        shell,
        wall,
        floor,
        clearance,
        collar_depth,
        toe_height,
    )
    if not all(math.isfinite(v) and v > 0 for v in positive):
        raise ValueError("尺寸必须为有限正数")
    if not (45 <= ramp_angle < 80):
        raise ValueError("免支撑外坡角需在 [45, 80) 度之间")
    if not math.isfinite(curvature) or abs(curvature) >= 1:
        raise ValueError("curvature 需在 (-1, 1) 内，保证漏斗单调")
    if not isinstance(curve_steps, int) or curve_steps < 4:
        raise ValueError("curve_steps 需为至少 4 的整数")
    if not isinstance(segments, int) or segments < 32:
        raise ValueError("segments 需为至少 32 的整数")
    throat_r = hole_diameter / 2
    throat_z = floor + gap + shell
    run = funnel_radius - throat_r
    rise = height - throat_z
    if run <= 0 or rise <= 0:
        raise ValueError("漏斗外缘必须高于且宽于中央出口")
    if rise / run * (1 - abs(curvature)) < 1:
        raise ValueError("内漏斗过缓：增大 height 或减小半径/gap/curvature")
    if toe_height > shell:
        raise ValueError("toe_height 不能大于 shell，否则坡脚会悬空")
    seat_z = height - shell
    collar_bottom = seat_z - collar_depth
    if collar_bottom <= floor:
        raise ValueError("定位圈过深，需减小 collar_depth 或增加 height")

    # 顶沿依次容纳杯壁、装配间隙、定位圈及少量外侧余量。
    cup_outer = funnel_radius + wall
    collar_inner = cup_outer + clearance
    collar_outer = collar_inner + wall
    rim_outer = collar_outer + clearance
    foot_r = rim_outer + (height - toe_height) / math.tan(math.radians(ramp_angle))

    def revolve(points):
        return polygon(points).revolve(fn=segments)

    base = revolve(
        [
            (0, 0),
            (cup_outer, 0),
            (cup_outer, seat_z),
            (funnel_radius, seat_z),
            (funnel_radius, floor),
            (0, floor),
        ]
    )

    # 同一截面贯通外坡、顶沿和内漏斗；下方留空，避免实心填料。
    funnel = []
    for i in range(curve_steps + 1):
        u = i / curve_steps
        funnel.append(
            (
                throat_r + run * u,
                throat_z + rise * (u + curvature * u * (1 - u)),
            )
        )
    top = [(foot_r, toe_height), (rim_outer, height)] + funnel[::-1]
    underside = [(r, max(0, z - shell)) for r, z in top[::-1]]
    lid = revolve(top + underside)
    collar = revolve(
        [
            (collar_inner, collar_bottom),
            (collar_outer, collar_bottom),
            (collar_outer, seat_z + shell / 2),
            (collar_inner, seat_z + shell / 2),
        ]
    )
    return base, lid + collar


if is_rendering():
    _base, _lid = get_parts()
    base = _base
    lid = _lid.rotate(x=180).align(zmin=0).move(x=_lid.size().x + 8)
    show_assembly = _base + _lid
    _clip = cube(_lid.size().x + 2, _lid.size().y / 2 + 1, _lid.size().z + 2)
    _clip = _clip.move(x=-_lid.size().x / 2 - 1, z=-1)
    show_section = show_assembly - _clip
