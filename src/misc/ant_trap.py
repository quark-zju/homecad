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
wall 是底杯及定位圈径向壁厚，shell 是平圆环厚度（默认 1.6 mm）。
slope_wall / ramp_wall 分别为内漏斗 / 外坡法向厚度（默认 1.2 / 0.8 mm），
edge_width 为收口最小径向宽度（默认 1.2 mm）。
建议 0.4 mm 喷嘴、0.2 mm 层高。
"""

import math
from inspect import signature

from b4dcad import cube, cylinder, is_rendering, polygon


def get_parts(
    gap=5.0,
    hole_diameter=7.0,
    funnel_radius=22.0,
    cup_radius=36.0,
    height=34.0,
    ramp_angle=60.0,
    rim_width=8.0,
    curve_angle=18.0,
    shell=1.6,
    slope_wall=1.2,
    ramp_wall=0.8,
    edge_width=1.2,
    wall=1.2,
    floor=1.2,
    clearance=0.2,
    grip_count=12,
    grip_interference=0.17,
    grip_width=2.0,
    grip_height=2.0,
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

    外坡角相对于地面。cup_radius 为底杯内半径，独立于漏斗外半径
    funnel_radius；两者之间用平圆环连接，以扩大外腔而不拉缓内漏斗。
    slope_wall / ramp_wall 为内漏斗 / 外坡法向壁厚；edge_width 为收口最小径向宽度。
    内漏斗以下表面参考圆弧为基准向上加厚，保留底杯和隔壁配合。
    内漏斗中央较陡、外缘较缓；
    curve_angle 为圆弧圆心角（度），0 为直锥。限制两侧坡面至少 45°，以便
    盖子倒扣免支撑打印；较宽漏斗/较大 gap 需相应增加 height。
    clearance 为单侧径向间隙。顶沿压在底杯壁上，
    内外两道定位环夹住底杯壁，入口斜面便于对正；装配高度不依赖摩擦力。
    clearance 为两侧各自的径向间隙；lead_in 为入口额外放宽量，
    lead_height 为斜面的竖向高度。外定位环均布 grip_count 条径向小凸筋，
    宽 grip_width、高 grip_height，两端倒斜导入；筋尖与杯外壁径向过盈
    grip_interference，提供局部摩擦定位。设 grip_count=0 可关闭凸筋。
    过盈值需根据打印机调节，默认 0.17 mm；没有依靠倒扣的锁定机构。
    rim_width 为平圆环在杯内壁半径之外的宽度；圆环总宽还包括
    cup_radius - funnel_radius，倒扣打印时整圈平面贴平台。
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
        cup_radius,
        height,
        rim_width,
        shell,
        slope_wall,
        ramp_wall,
        edge_width,
        wall,
        floor,
        clearance,
        grip_width,
        grip_height,
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
    if not isinstance(grip_count, int) or grip_count < 0:
        raise ValueError("grip_count 需为非负整数")
    if not math.isfinite(grip_interference) or not (0 <= grip_interference < wall / 2):
        raise ValueError("grip_interference 需非负且小于半个壁厚")
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
    if cup_radius < funnel_radius:
        raise ValueError("cup_radius 不能小于 funnel_radius")
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
    if max(slope_wall, ramp_wall) > shell:
        raise ValueError("平圆环 shell 不能薄于坡面 slope_wall")
    if lead_in >= wall or not (lead_in <= lead_height <= collar_depth):
        raise ValueError("需 lead_in < wall 且 lead_in <= lead_height <= collar_depth")
    seat_z = height - shell
    collar_bottom = seat_z - collar_depth
    if collar_bottom <= floor:
        raise ValueError("定位圈过深，需减小 collar_depth 或增加 height")

    # 顶沿依次容纳杯壁、装配间隙、定位圈及少量外侧余量。
    cup_outer = cup_radius + wall
    collar_inner = cup_outer + clearance
    collar_outer = collar_inner + wall
    if rim_width < 2 * (wall + clearance):
        raise ValueError("rim_width 需容纳杯壁、定位圈及两处间隙")
    rim_outer = cup_radius + rim_width
    foot_r = rim_outer + (height - toe_height) / math.tan(math.radians(ramp_angle))

    def revolve(points):
        return polygon(points).revolve(fn=segments)

    base = revolve(
        [
            (0, 0),
            (cup_outer, 0),
            (cup_outer, seat_z),
            (cup_radius, seat_z),
            (cup_radius, floor),
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
    # 保留参考曲面的下表面，使底杯隔壁、5 mm 净间隙及定位配合不变。
    # 对下表面各线段做精确等距偏移，交点采用斜接，保证法向壁厚。
    reference_under = [(r, z - shell) for r, z in funnel]
    normals = []
    for (r0, z0), (r1, z1) in zip(reference_under, reference_under[1:]):
        length = math.hypot(r1 - r0, z1 - z0)
        normals.append((-(z1 - z0) / length, (r1 - r0) / length))
    upper = []
    for i, (r, z) in enumerate(reference_under):
        before = normals[max(0, i - 1)]
        after = normals[min(i, len(normals) - 1)]
        scale = slope_wall / (1 + before[0] * after[0] + before[1] * after[1])
        upper.append(
            (r + scale * (before[0] + after[0]), z + scale * (before[1] + after[1]))
        )
    # 偏移后的曲面与竖直孔壁相交；孔下端另设平底环，不收成薄刃。
    for i, ((r0, z0), (r1, z1)) in enumerate(zip(upper, upper[1:])):
        if r0 <= throat_r < r1:
            upper = [(throat_r, z0 + (z1 - z0) * (throat_r - r0) / (r1 - r0))] + upper[
                i + 1 :
            ]
            break
    else:
        raise ValueError("坡面偏移过大，中央孔与内曲面不相交")
    r0, z0 = upper[-2]
    r1, z1 = upper[-1]
    upper.append((r1 + (height - z1) * (r1 - r0) / (z1 - z0), height))
    if upper[-1][0] >= rim_outer:
        raise ValueError("内曲面超出顶沿，需增大杯半径或减小 shell")

    def reference_z(r):
        for (r0, z0), (r1, z1) in zip(reference_under, reference_under[1:]):
            if r0 <= r <= r1:
                return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
        raise ValueError("收口超出内漏斗范围")

    lip_outer = throat_r + edge_width
    outlet_z = floor + gap
    inner_under = [(lip_outer, reference_z(lip_outer))]
    inner_under += [(r, z) for r, z in reference_under if r > lip_outer]
    # 外坡下表面与上表面平行，再和平台下表面相交，不能逐点截断 z。
    angle = math.radians(ramp_angle)
    slope = math.tan(angle)
    outer_drop = ramp_wall / math.cos(angle)
    outer_seat_r = rim_outer + (shell - outer_drop) / slope
    foot_width = max(edge_width, ramp_wall / math.sin(angle))
    foot_inner = foot_r - foot_width
    foot_join_z = toe_height - outer_drop + slope * foot_width
    if foot_join_z >= seat_z or foot_inner <= outer_seat_r:
        raise ValueError("外沿收口过大，需减小 edge_width/toe_height 或增加 height")
    top = upper + [(rim_outer, height), (foot_r, toe_height)]
    bottom = (
        [
            (foot_r, 0),
            (foot_inner, 0),
            (foot_inner, foot_join_z),
            (outer_seat_r, seat_z),
        ]
        + inner_under[::-1]
        + [(lip_outer, outlet_z), (throat_r, outlet_z)]
    )
    lid = revolve(top + bottom)
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
    inner_outer = cup_radius - clearance
    inner_inner = inner_outer - wall
    if inner_inner <= throat_r:
        raise ValueError("内定位环与中央出口重叠，需增大 funnel_radius 或减小壁厚")

    def underside_at(r):
        if funnel_radius <= r <= rim_outer:
            return seat_z
        return reference_z(r)

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
    # 凸筋在承座让位切除之后添加，只让少量局部表面与杯外壁过盈。
    if grip_count:
        rib_depth = clearance + grip_interference
        bevel = max(0.4, rib_depth)
        rib_top = seat_z - lead_height / 2
        rib_bottom = rib_top - grip_height
        if grip_height <= 2 * bevel or rib_bottom < collar_bottom + lead_height:
            raise ValueError("凸筋高度或定位圈深度不足以容纳双端导入斜面")
        if grip_count > 1 and grip_width >= 2 * collar_inner * math.sin(
            math.pi / grip_count
        ):
            raise ValueError("凸筋过宽或过多，会互相重叠")
        rib = (
            polygon(
                [
                    (collar_inner + wall / 2, rib_bottom),
                    (collar_inner + wall / 2, rib_top),
                    (collar_inner, rib_top),
                    (cup_outer - grip_interference, rib_top - bevel),
                    (cup_outer - grip_interference, rib_bottom + bevel),
                    (collar_inner, rib_bottom),
                ]
            )
            .extrude(grip_width)
            .rotate(x=90)
            .move(y=grip_width / 2)
        )
        for i in range(grip_count):
            lid += rib.rotate(z=i * 360 / grip_count)
    # 隔壁只接到底杯；顶部沿漏斗留缝，拆盖时不需要对准隔壁。
    if inner_chamber_radius is None:
        inner_chamber_radius = throat_r + run * 0.46
    partition_inner = inner_chamber_radius
    partition_outer = partition_inner + wall
    if not math.isfinite(partition_inner) or not (
        throat_r + edge_width + clearance
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


def get_fit_test(grip_interference=0.10, marks=1, margin=0.8, **kwargs):
    """从正式上盖裁出整圈配合试件，已倒置为打印朝向，适配现有底杯。

    只保留双环、导入面、全部凸筋和连接薄板；不重画配合几何。
    margin 为定位环内外侧各保留的平板宽度。marks 为外沿浅缺口数量，
    缺口不接触底杯；1/2/3 个缺口对应默认 0.10/0.15/0.20 mm 三档。
    kwargs 传给 get_parts；找到合适的档位后，将 grip_interference 用于整盖。
    试件没有整盖的漏斗与外坡，刚性有所不同，结果用于筛选松紧。

        b4dcad preview src/misc/ant_trap.py --object get_fit_test
        b4dcad stl src/misc/ant_trap.py ./stl --object get_fit_test

    默认先打印 0.10 mm；get_fit_tests 可一次预览/导出三档。
    """
    if not math.isfinite(margin) or margin < 0.4:
        raise ValueError("margin 至少为 0.4 mm，保留不接触杯壁的标记边缘")
    if not isinstance(marks, int) or not 0 <= marks <= 6:
        raise ValueError("marks 需为 0 到 6 的整数")
    bound = signature(get_parts).bind_partial(
        grip_interference=grip_interference, **kwargs
    )
    bound.apply_defaults()
    params = bound.arguments
    _, lid = get_parts(**params)
    cup_r, wall, clearance = (params[k] for k in ("cup_radius", "wall", "clearance"))
    height, shell, depth = (params[k] for k in ("height", "shell", "collar_depth"))
    inner_r = cup_r - clearance - wall - margin
    outer_r = cup_r + wall + clearance + wall + margin
    bottom = height - shell - depth
    if inner_r <= 0:
        raise ValueError("margin 过大，配合环内孔消失")
    clip = (
        cylinder(h=shell + depth + 2, r=outer_r, fn=params["segments"])
        - cylinder(h=shell + depth + 2, r=inner_r, fn=params["segments"])
    ).move(z=bottom - 1)
    part = lid & clip
    notch = cube(margin + 1, 1.2, shell + depth + 2).move(
        x=outer_r - margin / 2, y=-0.6, z=bottom - 1
    )
    for i in range(marks):
        part -= notch.rotate(z=30 + 3 * (i - (marks - 1) / 2))
    return part.rotate(x=180).align(zmin=0)


def get_fit_test_017():
    """下一轮试配：0.17 mm 径向过盈、12 个凸筋，外沿四个缺口作标记。

    正式整盖也采用本档参数。保留双端导入斜面，齿数增加也会增加夹紧力，
    需先在现有底杯上试配。本试环和 get_parts 中同参数盖子的配合面一致。

        b4dcad preview src/misc/ant_trap.py --object get_fit_test_017
        b4dcad stl src/misc/ant_trap.py ./stl --object get_fit_test_017
    """
    return get_fit_test(0.17, marks=4, grip_count=12)


def get_fit_tests():
    """三档整圈试件：1/2/3 个缺口分别对应 0.10/0.15/0.20 mm 过盈。

    三档沿用正式盖子的默认齿数；以三角形排版，约 166 x 154 mm。

        b4dcad preview src/misc/ant_trap.py --object get_fit_tests
        b4dcad stl src/misc/ant_trap.py ./stl --object get_fit_tests
    """
    part1 = get_fit_test(0.10, marks=1)
    spacing = part1.size().x + 8
    part2 = get_fit_test(0.15, marks=2).move(x=spacing)
    part3 = get_fit_test(0.20, marks=3).move(
        x=spacing / 2, y=spacing * math.sqrt(3) / 2
    )
    return part1 + part2 + part3


if is_rendering():
    _base, _lid = get_parts()
    base = _base
    lid = _lid.rotate(x=180).align(zmin=0).move(x=_lid.size().x + 8)
    show_assembly = _base + _lid
    _clip = cube(_lid.size().x + 2, _lid.size().y / 2 + 1, _lid.size().z + 2)
    _clip = _clip.move(x=-_lid.size().x / 2 - 1, z=-1)
    show_section = show_assembly - _clip
