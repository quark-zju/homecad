"""环形外坡蚂蚁陷阱，单位 mm；底杯和漏斗盖各打印一件。

底杯开口朝上；盖子已翻面，环形顶沿贴平台，两件默认免支撑。
gap 是中央出口下缘到底杯内底面的净高，不是入口孔径；
hole_diameter 独立控制中央孔径。底杯分中央腔和外侧环形盲腔，
两腔仅通过隔壁下部通道及顶部微小装配缝连通。诱饵放中央腔，
盖子向上拔出清理；外侧盲腔没有直接通向杯外的开口。
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
    height=34.0,
    ramp_angle=45.0,
    rim_width=8.0,
    curve_angle=18.0,
    shell=1.6,
    wall=1.2,
    floor=1.2,
    clearance=0.3,
    collar_depth=4.0,
    lead_in=0.5,
    lead_height=1.0,
    toe_height=0.6,
    inner_chamber_radius=None,
    passage_width=5.0,
    passage_height=5.0,
    passage_count=4,
    partition_clearance=0.2,
    curve_steps=48,
    segments=192,
):
    """返回 (底杯, 盖子)，均为装配坐标，地面 z=0。

    外坡角相对于地面。内漏斗截面为圆弧，中央较陡、外缘较缓；
    curve_angle 为圆弧圆心角（度），0 为直锥。限制两侧坡面至少 45°，以便
    盖子倒扣免支撑打印；较宽漏斗/较大 gap 需相应增加 height。
    clearance 为单侧径向间隙，不强行压配。顶沿压在底杯壁上，
    内外两道定位环夹住底杯壁，入口斜面便于对正；装配高度不依赖摩擦力。
    clearance 为两侧各自的径向间隙；lead_in 为入口额外放宽量，
    lead_height 为斜面的竖向高度。此配合为松套，不是弹性卡扣。
    rim_width 是顶部平圆环的径向宽度，也是倒扣打印的接触宽度。
    inner_chamber_radius 为中央腔净半径，None 时按漏斗径向跨度分配。
    隔壁厚度沿用 wall，上缘随漏斗下表面，留 partition_clearance 竖向缝。
    passage_count 个下部通道均布，默认十字四出口，宽 passage_width、高 passage_height；
    通道顶部为 45° 尖拱，默认两件均无需额外打印支撑。
    此结构增加返回路径复杂度，但不保证防逃，也不作为独立承重支撑。
    """
    positive = (
        gap,
        hole_diameter,
        funnel_radius,
        height,
        rim_width,
        shell,
        wall,
        floor,
        clearance,
        collar_depth,
        lead_in,
        lead_height,
        toe_height,
        passage_width,
        passage_height,
        partition_clearance,
    )
    if not all(math.isfinite(v) and v > 0 for v in positive):
        raise ValueError("尺寸必须为有限正数")
    if not (45 <= ramp_angle < 80):
        raise ValueError("免支撑外坡角需在 [45, 80) 度之间")
    if not math.isfinite(curve_angle) or not (0 <= curve_angle < 90):
        raise ValueError("curve_angle 需在 [0, 90) 度内")
    if not isinstance(curve_steps, int) or curve_steps < 4:
        raise ValueError("curve_steps 需为至少 4 的整数")
    if not isinstance(segments, int) or segments < 32:
        raise ValueError("segments 需为至少 32 的整数")
    if not isinstance(passage_count, int) or passage_count < 1:
        raise ValueError("passage_count 需为至少 1 的整数")
    if passage_height < passage_width / 2:
        raise ValueError("通道需保留 45° 尖拱：passage_height >= passage_width / 2")
    throat_r = hole_diameter / 2
    throat_z = floor + gap + shell
    run = funnel_radius - throat_r
    rise = height - throat_z
    if run <= 0 or rise <= 0:
        raise ValueError("漏斗外缘必须高于且宽于中央出口")
    chord_angle = math.atan2(rise, run)
    half_arc = math.radians(curve_angle) / 2
    if chord_angle - half_arc < math.pi / 4:
        raise ValueError("外缘过缓：增大 height 或减小半径/gap/curve_angle")
    if chord_angle + half_arc >= math.pi / 2:
        raise ValueError("中央圆弧回折：减小 height/curve_angle 或增大半径")
    if toe_height > shell:
        raise ValueError("toe_height 不能大于 shell，否则坡脚会悬空")
    if lead_in >= wall or not (lead_in <= lead_height <= collar_depth):
        raise ValueError("需 lead_in < wall 且 lead_in <= lead_height <= collar_depth")
    seat_z = height - shell
    collar_bottom = seat_z - collar_depth
    if collar_bottom <= floor:
        raise ValueError("定位圈过深，需减小 collar_depth 或增加 height")

    # 顶沿依次容纳杯壁、装配间隙、定位圈及少量外侧余量。
    cup_outer = funnel_radius + wall
    collar_inner = cup_outer + clearance
    collar_outer = collar_inner + wall
    if rim_width < 2 * (wall + clearance):
        raise ValueError("rim_width 需容纳杯壁、定位圈及两处间隙")
    rim_outer = funnel_radius + rim_width
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
    # 在弦坐标系中计算圆弧，避免小圆心角时两个大半径直接相减。
    # 正矢使用有理化形式；curve_angle=0 时连续退化为直线。
    chord = math.hypot(run, rise)
    sin_half = math.sin(half_arc)
    for i in range(curve_steps + 1):
        u = i / curve_steps
        along = 2 * u - 1
        sag = (
            chord
            / 2
            * sin_half
            * (1 - along * along)
            / (math.sqrt(1 - (along * sin_half) ** 2) + math.cos(half_arc))
        )
        funnel.append(
            (
                throat_r + run * u - sag * rise / chord,
                throat_z + rise * u + sag * run / chord,
            )
        )
    top = [(foot_r, toe_height), (rim_outer, height)] + funnel[::-1]
    underside = [(r, max(0, z - shell)) for r, z in top[::-1]]
    lid = revolve(top + underside)
    # 外环的内侧、内环的外侧分别向杯壁退让，形成双侧导入斜面。
    outer_collar = revolve(
        [
            (collar_inner + lead_in, collar_bottom),
            (collar_outer, collar_bottom),
            (collar_outer, seat_z + shell / 2),
            (collar_inner, seat_z + shell / 2),
            (collar_inner, collar_bottom + lead_height),
        ]
    )
    inner_outer = funnel_radius - clearance
    inner_inner = inner_outer - wall
    if inner_inner <= throat_r:
        raise ValueError("内定位环与中央出口重叠，需增大 funnel_radius 或减小壁厚")

    def underside_at(r):
        for (r0, z0), (r1, z1) in zip(funnel, funnel[1:]):
            if r0 <= r <= r1:
                return z0 + (z1 - z0) * (r - r0) / (r1 - r0) - shell
        raise ValueError("定位环超出漏斗曲面")

    if underside_at(inner_inner) <= collar_bottom + lead_height:
        raise ValueError("内定位环高度不足，需增加 collar_depth 或减小 lead_height")
    # 上边沿跟随漏斗下表面，埋入半个壁厚连接，不穿出漏斗上表面。
    roof = [(inner_inner, underside_at(inner_inner) + shell / 2)]
    roof += [(r, z - shell / 2) for r, z in funnel if inner_inner < r < inner_outer]
    roof += [(inner_outer, underside_at(inner_outer) + shell / 2)]
    inner_collar = revolve(
        [
            (inner_inner, collar_bottom),
            (inner_outer - lead_in, collar_bottom),
            (inner_outer, collar_bottom + lead_height),
        ]
        + roof[::-1]
    )
    # 给杯口内外两侧均留出 clearance，避免略偏小的杯口顶到曲面下方。
    seat_relief = revolve(
        [
            (inner_outer, collar_bottom - wall),
            (collar_inner, collar_bottom - wall),
            (collar_inner, seat_z),
            (inner_outer, seat_z),
        ]
    )
    lid = lid + outer_collar + inner_collar - seat_relief
    # 隔壁只接到底杯；顶部沿漏斗留缝，拆盖时不需要对准隔壁。
    if inner_chamber_radius is None:
        inner_chamber_radius = throat_r + run * 0.46
    partition_inner = inner_chamber_radius
    partition_outer = partition_inner + wall
    if not math.isfinite(partition_inner) or not (
        throat_r + clearance
        < partition_inner
        < partition_outer
        < inner_inner - clearance
    ):
        raise ValueError("中央腔需包住出口，且隔壁与盖口内定位环之间需有外腔空间")
    half_pitch = math.pi / max(passage_count, 2)
    if passage_width >= 2 * partition_inner * math.sin(half_pitch):
        raise ValueError("通道过宽或过多，隔壁无法保留连续立柱")
    partition_roof = [
        (partition_inner, underside_at(partition_inner) - partition_clearance)
    ]
    partition_roof += [
        (r, z - shell - partition_clearance)
        for r, z in funnel
        if partition_inner < r < partition_outer
    ]
    partition_roof += [
        (partition_outer, underside_at(partition_outer) - partition_clearance)
    ]
    if partition_roof[0][1] <= floor + passage_height + wall:
        raise ValueError("隔壁过低，需减小 passage_height 或增大中央腔半径/height")
    partition = revolve(
        [(partition_inner, floor / 2), (partition_outer, floor / 2)]
        + partition_roof[::-1]
    )
    # 切口只作用于隔壁，再并入底杯，保证外壁、杯底和定位结构完整。
    half_w = passage_width / 2
    passage = (
        polygon(
            [
                (-half_w, 0),
                (half_w, 0),
                (half_w, passage_height - half_w),
                (0, passage_height),
                (-half_w, passage_height - half_w),
            ]
        )
        .extrude(partition_outer + wall)
        .rotate(x=90)
        .move(y=partition_outer + wall, z=floor)
    )
    for i in range(passage_count):
        partition -= passage.rotate(z=i * 360 / passage_count)
    return base + partition, lid


if is_rendering():
    _base, _lid = get_parts()
    base = _base
    lid = _lid.rotate(x=180).align(zmin=0).move(x=_lid.size().x + 8)
    show_assembly = _base + _lid
    _clip = cube(_lid.size().x + 2, _lid.size().y / 2 + 1, _lid.size().z + 2)
    _clip = _clip.move(x=-_lid.size().x / 2 - 1, z=-1)
    show_section = show_assembly - _clip
