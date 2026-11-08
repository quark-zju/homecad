"""长边三折四槽卡包：外层每槽 1–2 张，中间层每面单卡，总容量 4–6 张。

outer_a / outer_b 各一件，middle_a / middle_b 各一件；均按导出朝向平放打印。
cover_double / cover_single 各两件，薄面朝下打印；装配时翻面，两端燕尾脚向下。
为首层 0.20 mm、后续层高 0.08 mm 设计。建议降低首层打印速度。
同盘打印多个组件时，建议逐件打印，不按层交替打印。
薄面直接贴打印板，不加筏层。
中间两半背面对粘，其中一片绕 Y 翻转 180 度。

卡槽有效宽由 54.58 收至 54.28（总宽减少 0.3），卡片尺寸仍为 85.6×53.98。
本版按单卡 0.8、双卡 1.6 设计；中间单卡槽另留一层 0.08 高度余量。
外层导轨仍与双卡高齐平，不另做上沿限位。
相向盖板沿 Y 错开。每个折叠界面额外留 0.16，容纳实测首层偏厚。
盖板对面仅在两端导轨开避空槽，槽底与卡片底板平齐，X/Y 每侧留 0.8。
中间板两侧导轨各宽 7.6，外壳导轨宽 7.1、铰链侧宽 6.5；短边挡条限定各面的抽卡方向。
中间卡从仍闭合的对侧外壳没有边框的一端抽出，只需打开一片外壳。
中间底板两层为 0.28，外壳底板三层为 0.36，整版名义厚度 6.96。
先前实测 0.9/1.8 的卡需设 CARD_THICKNESS=0.9。
STAGGER_COVERS=False 时相向盖板对齐在磁铁一侧，名义厚度增加 0.4。

盖板 Y 向薄面宽 13.82，X 向两端各缩短 0.2。相向盖板对调原有 Y 位置，增加抽卡侧的露出长度。
盖板薄面为 0.20。通过 COVER_FOOT_TRIM_LAYERS 按 0.08 缩短燕尾脚，本版各缩短一层。
盖板两端用整面 45 度梯形燕尾配合，薄面限制卡片沿 Z 向脱出。
盖板两端装入局部燕尾盲槽，槽壁限制 Y/Z 移动，外侧实体挡壁限制 X 移动。
先插入一端，再临时轻弯薄面装入另一端；空槽时反向弯曲拆卸，不设插销。
盖板以外不拓宽卡槽。
没有弹簧、弹簧井和小条扣沿。盖板内侧的一只脚留 45 度凹槽，薄涂热熔胶，
冷却后形成弹性接触面；胶不进入燕尾轨，可剥除重涂来调整单/双卡松紧。
局部燕尾座固定相向盖板的错开位置，X 向每端留 0.35 装配余量。
薄盖板弯装、刚度、燕尾松紧与热熔胶量需试印验证；建议先打印一套外壳和盖板。

四段直径 0.8、约 16 长裸回形针；三节轴套及水平 1.0 尖顶孔沿用实测配合。
轴套外径 2.8，外圆距板边 0.2；尖顶孔上方最薄约 0.69，缩小版需试印。
外壳开放短边的底板延伸到对侧外壁边缘，覆盖俯视缝隙；长边中段保留搭接唇。
两侧燕尾槽外端封实，外层轴套根部局部加宽。
四枚 10×5×2 磁铁分装在两片外壳上。每片沿两条长边各装一枚，长边沿 Y，Y 向居中。
磁铁槽按实测配合尺寸 10.1×5.0×2.2 建模，中间板为磁铁座留 0.4 活动余量。
先核对两对磁极，再胶粘。
不做埋箔夹层。show_* 仅预览，不导出；折叠角 0 为摊开，180 为闭合。
"""

import math

from b4dcad import circle, cube, cylinder, polygon, square

CARD_LENGTH = 85.6
CARD_WIDTH = 53.98
CARD_THICKNESS = 0.8
CARD_CLEARANCE_X = 0.3
CARD_CLEARANCE_Y = 0.6
FIRST_LAYER_HEIGHT = 0.20
LAYER_HEIGHT = 0.08
OUTER_FLOOR = FIRST_LAYER_HEIGHT + 2 * LAYER_HEIGHT
MIDDLE_FLOOR = FIRST_LAYER_HEIGHT + LAYER_HEIGHT
END_BAND = 7.6
SIDE_MARGIN = 3.0
LENGTH = CARD_WIDTH + CARD_CLEARANCE_X + 2 * END_BAND
WIDTH = CARD_LENGTH + CARD_CLEARANCE_Y + 2 * SIDE_MARGIN
OUTER_CARD_HEIGHT = 2 * CARD_THICKNESS
MIDDLE_CARD_HEIGHT = math.ceil(CARD_THICKNESS / LAYER_HEIGHT) * LAYER_HEIGHT
OUTER_GUIDE_HEIGHT = OUTER_CARD_HEIGHT
MIDDLE_GUIDE_HEIGHT = MIDDLE_CARD_HEIGHT + LAYER_HEIGHT
COVER_THICKNESS = FIRST_LAYER_HEIGHT
COVER_FOOT_TRIM_LAYERS = 1
COVER_CLOSURE_CLEARANCE = 2 * LAYER_HEIGHT
COVER_WIDTH = 14.0  # 主体燕尾槽名义宽度，同时确定原盖板中心位置。
COVER_Y_TRIM = 0.3
COVER_Y_FIT_ADD = 0.12  # 两边均分，仅用于盖条公件。
COVER_X_TRIM = 0.4
STAGGER_COVERS = True
COVER_CENTER_OFFSET = 16.0
COVER_RELIEF_CLEARANCE = 0.8
MIDDLE_STOP_HEIGHT = 0.8
FOOT_BOTTOM = 0.2
COVER_FOOT_BOTTOM = FOOT_BOTTOM + COVER_FOOT_TRIM_LAYERS * LAYER_HEIGHT
FOOT_LENGTH = 2.0
DOVETAIL_CLEARANCE = 0.15
OUTER_GUIDE_EDGE_CLEARANCE = 0.5
OUTER_HINGE_GUIDE_TRIM = 0.6

PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BORE_DIAMETER = 1.0
AXIS_HEIGHT = (
    MIDDLE_FLOOR
    + OUTER_FLOOR
    + MIDDLE_GUIDE_HEIGHT
    + OUTER_GUIDE_HEIGHT
    + COVER_THICKNESS * (1 if STAGGER_COVERS else 2)
    + COVER_CLOSURE_CLEARANCE
) / 2
BARREL_RADIUS = 1.4
HINGE_OFFSET = 1.6
AXIAL_GAP = 0.3
BLIND_WALL = 0.8
PIN_RECESS = 0.5
PIN_SPAN = BLIND_WALL + PIN_LENGTH + PIN_RECESS
END_KNUCKLE = 5.6
HINGE_LENGTH = WIDTH - 8
HINGE_Y = (WIDTH - HINGE_LENGTH) / 2

RIM_WALL = 1.2
RIM_GAP = 0.4
RIM_EXTENT = RIM_WALL + RIM_GAP
RIM_RADIUS = 2.0
RIM_SEAM = 0.2
RIM_HEIGHT = 4 * AXIS_HEIGHT - OUTER_FLOOR - 0.2
RIM_LAP = 0.4
MAGNET_SLOT_X = 5.0
MAGNET_SLOT_Y = 10.1
MAGNET_DEPTH = 2.2
MAGNET_SEAT_HEIGHT = 2 * AXIS_HEIGHT - 0.2
MAGNET_WALL = 0.6
MAGNET_HALF_X = MAGNET_SLOT_X / 2 + MAGNET_WALL
MAGNET_HALF_Y = MAGNET_SLOT_Y / 2 + MAGNET_WALL
MAGNET_X = MAGNET_HALF_X + 0.2
MAGNET_Y = WIDTH / 2
MAGNET_CLEARANCE = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return cube(x1 - x0, y1 - y0, z1 - z0).move(x=x0, y=y0, z=z0)


def _rounded(x0, x1, y0, y1, radius=2):
    return (
        square(x1 - x0 - 2 * radius, y1 - y0 - 2 * radius)
        .offset(radius, "round")
        .align(xmin=x0, ymin=y0)
    )


def _axial_cylinder(diameter, start, end, x=0, height=AXIS_HEIGHT):
    return (
        cylinder(h=end - start, r=diameter / 2, fn=96)
        .rotate(x=-90)
        .move(x=x, y=start, z=height)
    )


def _roof_bore(start, end, x):
    r = BORE_DIAMETER / 2
    t = r / math.sqrt(2)
    profile = circle(r=r, fn=64) + polygon([(-t, t), (t, t), (0, r * math.sqrt(2))])
    return profile.extrude(end - start).rotate(x=90).move(x=x, y=end, z=AXIS_HEIGHT)


def _hinge(ends, right_edge):
    x = LENGTH + HINGE_OFFSET if right_edge else -HINGE_OFFSET
    side = -1 if right_edge else 1
    if ends:
        intervals = (
            (0, END_KNUCKLE),
            (PIN_SPAN - END_KNUCKLE, PIN_SPAN),
            (HINGE_LENGTH - PIN_SPAN, HINGE_LENGTH - PIN_SPAN + END_KNUCKLE),
            (HINGE_LENGTH - END_KNUCKLE, HINGE_LENGTH),
        )
    else:
        intervals = (
            (END_KNUCKLE + AXIAL_GAP, PIN_SPAN - END_KNUCKLE - AXIAL_GAP),
            (
                HINGE_LENGTH - PIN_SPAN + END_KNUCKLE + AXIAL_GAP,
                HINGE_LENGTH - END_KNUCKLE - AXIAL_GAP,
            ),
        )
    part = None
    for start, end in intervals:
        y0, y1 = start + HINGE_Y, end + HINGE_Y
        knuckle = _axial_cylinder(2 * BARREL_RADIUS, y0, y1, x)
        knuckle += _box(x - BARREL_RADIUS, x + BARREL_RADIUS, y0, y1, 0, AXIS_HEIGHT)
        reach = side * (HINGE_OFFSET + 0.2)
        knuckle += _box(x + min(0, reach), x + max(0, reach), y0, y1, 0, AXIS_HEIGHT)
        low = HINGE_Y + BLIND_WALL if start == 0 else y0 - 0.1
        high = HINGE_Y + HINGE_LENGTH - BLIND_WALL if end == HINGE_LENGTH else y1 + 0.1
        knuckle -= _roof_bore(low, high, x)
        part = knuckle if part is None else part + knuckle
    if ends:
        for a, b in (
            (PIN_SPAN - 1, PIN_SPAN + 0.1),
            (HINGE_LENGTH - PIN_SPAN - 0.1, HINGE_LENGTH - PIN_SPAN + 1),
        ):
            part -= _axial_cylinder(1.8, a + HINGE_Y, b + HINGE_Y, x)
    return part


def _foot_profile(height, reverse=False):
    """Y/Z 截面，脚的整个高度均为 45 度梯形，沿 X 拉伸。"""
    half_width = (COVER_WIDTH - COVER_Y_TRIM + COVER_Y_FIT_ADD) / 2
    center = _cover_y(height, reverse)
    y0, y1 = center - half_width, center + half_width
    flare = height - COVER_FOOT_BOTTOM
    return polygon(
        [
            (y0 - flare, COVER_FOOT_BOTTOM),
            (y1 + flare, COVER_FOOT_BOTTOM),
            (y1, height),
            (y1, height + COVER_THICKNESS),
            (y0, height + COVER_THICKNESS),
            (y0, height),
        ]
    )


def _along_x(profile, x0, x1):
    return profile.extrude(x1 - x0).rotate(x=90, z=90).move(x=x0)


def _along_y(profile, y0, y1):
    return profile.extrude(y1 - y0).rotate(x=90).move(y=y1)


def _dovetail_slot(height, reverse):
    center = _cover_y(height, reverse)
    y0, y1 = center - COVER_WIDTH / 2, center + COVER_WIDTH / 2
    y0 -= DOVETAIL_CLEARANCE
    y1 += DOVETAIL_CLEARANCE
    flare = height - FOOT_BOTTOM + 0.1
    return polygon(
        [
            (y0 - flare, FOOT_BOTTOM - 0.1),
            (y1 + flare, FOOT_BOTTOM - 0.1),
            (y1, height),
            (y1, height + 0.3),
            (y0, height + 0.3),
            (y0, height),
        ]
    )


def _cover_y(height, reverse=False):
    # 中间板与相向外壳从相反的 Y 端抽卡。
    direction = 1 if STAGGER_COVERS and height == MIDDLE_GUIDE_HEIGHT else -1
    return WIDTH / 2 + (-direction if reverse else direction) * COVER_CENTER_OFFSET


def _opposite_cover_relief(height, reverse):
    opposite = (
        MIDDLE_GUIDE_HEIGHT if height == OUTER_GUIDE_HEIGHT else OUTER_GUIDE_HEIGHT
    )
    y = _cover_y(opposite, reverse)
    half_width = (COVER_WIDTH - COVER_Y_TRIM) / 2 + opposite - FOOT_BOTTOM
    half_width += COVER_RELIEF_CLEARANCE
    x0 = END_BAND - FOOT_LENGTH + COVER_X_TRIM / 2 - COVER_RELIEF_CLEARANCE
    return _box(x0, LENGTH - x0, y - half_width, y + half_width, -0.01, height + 0.1)


def _fixed_guides(height, outline=None, reverse=False):
    edge = -0.01 if outline is None else 0
    # 外壳导轨从外缘退让，铰链侧再缩进以增加边框转动间隙。
    start_x = OUTER_GUIDE_EDGE_CLEARANCE if height == OUTER_GUIDE_HEIGHT else edge
    left = _box(start_x, END_BAND, edge, WIDTH - edge, 0, height)
    # 两侧槽只容纳现有燕尾脚，外端封实；盖板通过临时弯曲装入。
    slot_start = END_BAND - FOOT_LENGTH - DOVETAIL_CLEARANCE
    left -= _along_x(_dovetail_slot(height, reverse), slot_start, END_BAND + 0.02)
    right = left
    if height == OUTER_GUIDE_HEIGHT:
        right -= _box(
            edge, start_x + OUTER_HINGE_GUIDE_TRIM, edge, WIDTH - edge, 0, height
        )
        for start, end in (
            (END_KNUCKLE + AXIAL_GAP, PIN_SPAN - END_KNUCKLE - AXIAL_GAP),
            (
                HINGE_LENGTH - PIN_SPAN + END_KNUCKLE + AXIAL_GAP,
                HINGE_LENGTH - END_KNUCKLE - AXIAL_GAP,
            ),
        ):
            right += _box(0, END_BAND, start + HINGE_Y, end + HINGE_Y, 0, height)
    part = left + right.mirror(x=1).move(x=LENGTH)
    if height == OUTER_GUIDE_HEIGHT:
        part -= _magnet_notches(0)
    if STAGGER_COVERS:
        part -= _opposite_cover_relief(height, reverse)
    if outline is None:
        outline = _rounded(0, LENGTH, 0, WIDTH, RIM_RADIUS)
    return part & outline.extrude(height + 0.1)


def cover_panel(height, reverse=False):
    """装配姿态：面片在上，燕尾脚在下；胶槽朝向卡片一侧。"""
    center = _cover_y(height, reverse)
    half_width = (COVER_WIDTH - COVER_Y_TRIM + COVER_Y_FIT_ADD) / 2
    y0, y1 = center - half_width, center + half_width
    underside = height
    foot_start = END_BAND - FOOT_LENGTH + COVER_X_TRIM / 2
    left = _along_x(_foot_profile(height, reverse), foot_start, END_BAND)
    right = left.mirror(x=1).move(x=LENGTH)
    face_profile = polygon(
        [
            (y0, height),
            (y1, height),
            (y1, height + COVER_THICKNESS),
            (y0, height + COVER_THICKNESS),
        ]
    )
    face = _along_x(face_profile, foot_start, LENGTH - foot_start)
    part = face + left + right
    # 仅左脚朝卡片的一面开胶槽，另一脚保持完整定位。
    low, high = COVER_FOOT_BOTTOM + 0.1, underside - 0.1
    depth = min(0.3, (high - low) / 2)
    glue = polygon(
        [
            (END_BAND + 0.01, low),
            (END_BAND - depth, low + depth),
            (END_BAND - depth, high - depth),
            (END_BAND + 0.01, high),
        ]
    )
    part -= _along_y(glue, y0 + 1, y1 - 1)
    return part.as_original().simplify(1e-4).as_original().simplify(1e-4)


def cover_for_print(height):
    return (
        cover_panel(height)
        .rotate(y=180)
        .move(x=LENGTH, z=height + COVER_THICKNESS)
        .align(xmin=0, ymin=0, zmin=0)
        .as_original()
        .simplify(1e-4)
    )


def _rim_profiles():
    outer = _rounded(
        -RIM_EXTENT, LENGTH + RIM_EXTENT, -RIM_EXTENT, WIDTH + RIM_EXTENT, RIM_RADIUS
    )
    ring = outer - outer.offset(-RIM_WALL)
    slope = (WIDTH + 2 * RIM_EXTENT) / (LENGTH + 2 * RIM_EXTENT)
    intercept = (WIDTH + slope * LENGTH) / 2 - RIM_SEAM / 2 * math.sqrt(
        1 + slope * slope
    )
    far = 3 * (LENGTH + WIDTH)
    half = polygon(
        [
            (-far, -far),
            (far, -far),
            (far, intercept - slope * far),
            (-far, intercept + slope * far),
        ]
    )

    def split(profile):
        result = profile & half
        zones = (
            (
                -RIM_EXTENT - 0.1,
                2,
                WIDTH - 2,
                WIDTH + RIM_EXTENT + 0.1,
                WIDTH - RIM_SEAM / 2,
            ),
            (
                LENGTH - 2,
                LENGTH + RIM_EXTENT + 0.1,
                -RIM_EXTENT - 0.1,
                2,
                -RIM_SEAM / 2,
            ),
        )
        for x0, x1, y0, y1, limit in zones:
            zone = square(x1 - x0, y1 - y0).move(x=x0, y=y0)
            lower = square(2 * far, limit + far).move(x=-far, y=-far)
            result = (result - zone) + (profile & zone & lower)
        return result

    # 底板接满 L 框端部；装配缝仅保留在上方竖直边框，避免底缘出现 0.1 缺口。
    flange = split(outer).offset(RIM_SEAM / 2) & outer
    # 开放短边的底板遮住对侧短边框，圆角跟随外框轮廓。
    cap = square(LENGTH + 2 * RIM_EXTENT, RIM_RADIUS + RIM_EXTENT).move(
        x=-RIM_EXTENT, y=WIDTH - RIM_RADIUS
    )
    # 圆角处略微外放，避免叠合近重合轮廓时生成退化三角形。
    flange += outer.offset(0.02) & cap
    return flange, split(ring)


def _magnet_notches(clearance, open_edge=False):
    """为两条长边中央的磁铁座留出空间。"""
    half_y = MAGNET_HALF_Y + clearance
    x0 = -0.1 if open_edge else MAGNET_X - MAGNET_HALF_X - clearance
    left = _box(
        x0,
        MAGNET_X + MAGNET_HALF_X + clearance,
        MAGNET_Y - half_y,
        MAGNET_Y + half_y,
        -0.1,
        2 * AXIS_HEIGHT + 0.1,
    )
    return left + left.mirror(x=1).move(x=LENGTH)


def _magnet_seats():
    seat = _box(
        MAGNET_X - MAGNET_HALF_X,
        MAGNET_X + MAGNET_HALF_X,
        MAGNET_Y - MAGNET_HALF_Y,
        MAGNET_Y + MAGNET_HALF_Y,
        0,
        MAGNET_SEAT_HEIGHT,
    )
    seat -= _box(
        MAGNET_X - MAGNET_SLOT_X / 2,
        MAGNET_X + MAGNET_SLOT_X / 2,
        MAGNET_Y - MAGNET_SLOT_Y / 2,
        MAGNET_Y + MAGNET_SLOT_Y / 2,
        MAGNET_SEAT_HEIGHT - MAGNET_DEPTH,
        MAGNET_SEAT_HEIGHT + 0.1,
    )
    return seat + seat.mirror(x=1).move(x=LENGTH)


def _outer_rim():
    _, ring = _rim_profiles()
    part = ring.extrude(RIM_HEIGHT)
    # 长边只在两组轴套之间搭接，轴套和磁铁仍从原避空区通过。
    y0 = HINGE_Y + PIN_SPAN + AXIAL_GAP
    long_lip = ring & square(RIM_EXTENT, WIDTH - 2 * y0).move(x=-RIM_EXTENT, y=y0)
    part += long_lip.extrude(RIM_LAP).move(z=RIM_HEIGHT)
    # 给对侧铰链和其运动的根部留出空间。
    for start, end in ((0, PIN_SPAN), (HINGE_LENGTH - PIN_SPAN, HINGE_LENGTH)):
        part -= _box(
            -RIM_EXTENT - 0.1,
            0.1,
            HINGE_Y + start - AXIAL_GAP,
            HINGE_Y + end + AXIAL_GAP,
            2 * AXIS_HEIGHT - 0.6,
            RIM_HEIGHT + 0.1,
        )
    # 长条磁铁座经过边框的中段，避空贯穿加高的搭接唇。
    half_y = MAGNET_HALF_Y + MAGNET_CLEARANCE
    part -= _box(
        -RIM_EXTENT - 0.1,
        0.1,
        MAGNET_Y - half_y,
        MAGNET_Y + half_y,
        RIM_HEIGHT - 1.6,
        RIM_HEIGHT + RIM_LAP + 0.1,
    )
    return part


def outer_panel(reverse=False):
    flange, _ = _rim_profiles()
    floor_profile = _rounded(0, LENGTH, 0, WIDTH) + flange
    # 与 L 外框相邻的三个内角补实，仅开放端保留底板自身的圆角。
    for x, y in ((0, 0), (LENGTH - RIM_RADIUS, 0), (0, WIDTH - RIM_RADIUS)):
        floor_profile += square(RIM_RADIUS, RIM_RADIUS).move(x=x, y=y)
    floor_profile = floor_profile.simplify(0.001)
    part = floor_profile.extrude(OUTER_FLOOR) + _outer_rim() + _magnet_seats()
    if reverse:
        part = part.mirror(y=1).move(y=WIDTH)
        floor_profile = floor_profile.mirror(y=1).move(y=WIDTH)
    # L 边框下的底板已经包住端角，导轨随实际底板轮廓补齐，避免另切一个小圆缺口。
    part += _hinge(False, True) + _fixed_guides(
        OUTER_GUIDE_HEIGHT, floor_profile, reverse
    ).move(z=OUTER_FLOOR)
    return part.as_original().simplify(1e-4).as_original().simplify(1e-4)


def middle_panel_half(reverse=False):
    outline = _rounded(0, LENGTH, 0, WIDTH)
    part = outline.extrude(MIDDLE_FLOOR)
    stop_y = 0 if reverse else WIDTH - SIDE_MARGIN
    # 挡条两端接入导轨，导轨继续沿底板圆角延伸。
    stop = _box(
        END_BAND - 0.1,
        LENGTH - END_BAND + 0.1,
        stop_y,
        stop_y + SIDE_MARGIN,
        MIDDLE_FLOOR - 0.01,
        MIDDLE_FLOOR + MIDDLE_STOP_HEIGHT,
    )
    part = (
        part
        + stop
        + _hinge(True, False)
        + _fixed_guides(MIDDLE_GUIDE_HEIGHT, reverse=reverse).move(z=MIDDLE_FLOOR)
    )
    part -= _magnet_notches(MAGNET_CLEARANCE, open_edge=True)
    return part.as_original().simplify(1e-4)


def folded_outer(angle=180, reverse=False, covers=True):
    part = outer_panel(reverse)
    if covers:
        part += cover_panel(OUTER_GUIDE_HEIGHT, reverse).move(z=OUTER_FLOOR)
    return (
        part.move(x=-LENGTH - HINGE_OFFSET, z=-AXIS_HEIGHT)
        .rotate(y=angle)
        .move(x=-HINGE_OFFSET, z=AXIS_HEIGHT)
    )


def middle_assembly(reverse=False):
    return middle_panel_half(reverse) + cover_panel(MIDDLE_GUIDE_HEIGHT, reverse).move(
        z=MIDDLE_FLOOR
    )


outer_a = outer_panel()
outer_b = outer_panel(True)
middle_a = middle_panel_half()
middle_b = middle_panel_half(True)
cover_single = cover_for_print(MIDDLE_GUIDE_HEIGHT)
cover_double = cover_for_print(OUTER_GUIDE_HEIGHT)

# 闭合预览留微小间隙，避免接触面合并后在单精度网格中产生零面积三角形。
_preview_gap = 0.001
show_closed = (
    middle_assembly()
    + middle_assembly(True).rotate(y=180).move(x=LENGTH)
    + folded_outer().move(z=_preview_gap)
    + folded_outer(reverse=True).rotate(y=180).move(x=LENGTH, z=-_preview_gap)
).move(y=WIDTH + 25)
show_open = (
    middle_assembly()
    + middle_assembly(True).rotate(y=180).move(x=LENGTH)
    + folded_outer(45)
    + folded_outer(45, True).rotate(y=180).move(x=LENGTH)
).move(y=2 * WIDTH + 50)
show_open_one = (
    middle_assembly()
    + middle_assembly(True).rotate(y=180).move(x=LENGTH)
    + folded_outer(90)
    + folded_outer(reverse=True).rotate(y=180).move(x=LENGTH, z=-_preview_gap)
).move(y=3 * WIDTH + 75)
