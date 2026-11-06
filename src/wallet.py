"""约 10 mm 目标的长边三折四槽卡包，单位 mm；每槽 1–2 张 0.9 厚卡。

outer_a / outer_b 各一件，middle_half 两件，spring_strip 四件，均按导出姿态平放。
外壳底板 0.6，中间半片底板 0.4，固定导轨与主体一体打印，不粘贴框架。
仅隐藏弹簧长条单独打印：从卡片侧水平推入，舌片在扣沿下方定位；两个短端面均补到底板，上方扣沿仅向槽内伸出。
两端仅在扣沿下局部让位，插入导角越过定位点后落座；更换时抬起约 0.2 抽出，不涂胶。
底板连续，外表面没有弹片贯穿缝。入口在卡片侧，背面封闭，扣沿限制 Z 向脱出。
弹片井顶桥接宽 3.4、净空 0.4，只有压头露在卡片侧。
将两片中间件背面对粘，其中一片绕 Y 翻转 180 度。
用 0.2 层高（含首层）。卡片限位三层：0.4 高的 45 度斜坡加 0.2 顶层，
斜坡从卡高 1.6 开始，投影 0.4；在名义卡边处给 1.8 双卡留 0.1 高度余量。
每面高度为中间 0.4+2.2=2.6，外层 0.6+2.2=2.8，闭合名义总厚 10.8。
弹簧条侧面留 0.2、两端留 0.15 装配余量，定位点高 0.2；装配手感需实测。

四段直径 0.8、约 16 长裸回形针，三节轴套、水平 1.0 尖顶孔沿用实测试片。
先装轴并检查折叠，再封胶；两片 L 形圆角边框互补封住四边，保留 0.2 接缝。
竖直边框与底板共用圆角轮廓，不留半圆取卡口，卡片从开放短边滑入/抽出。

中间件无磁铁。两片外壳共放四枚 5.02×2.58 磁铁，平放在内侧。
两对只吸合两片外壳；中间层四处侧边缺口让开磁铁座，不缩小卡片空间。
磁铁座高 5.2，孔宽 5.32、深 2.8，沿用实测配合；先核对两对磁极，再胶粘。
磁吸力、薄限位和隐藏弹片均待实测。
不做埋箔夹层；贴箔和胶会占用本版有限的卡槽余量。
show_* 仅装配预览，不导出；折叠角 0 为摊开，180 为闭合。
"""

import math

from b4dcad import circle, cube, cylinder, polygon, square

CARD_LENGTH = 85.6
CARD_WIDTH = 53.98
CARD_THICKNESS = 0.9
CARD_CLEARANCE = 0.6
OUTER_FLOOR = 0.6
MIDDLE_FLOOR = 0.4
END_BAND = 7.6
SIDE_MARGIN = 3.0
LENGTH = CARD_WIDTH + CARD_CLEARANCE + 2 * END_BAND
WIDTH = CARD_LENGTH + CARD_CLEARANCE + 2 * SIDE_MARGIN
GUIDE_HEIGHT = 2 * CARD_THICKNESS + 0.4
LIP_UPPER_REACH = 0.4
LIP_RAMP_HEIGHT = 0.4
LIP_TOP_THICKNESS = 0.2
SPRING_WIDTH = 1.6
SPRING_INTRUSION = 0.95
SPRING_HEIGHT = 1.2
WELL_ROOF = 1.6

PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BORE_DIAMETER = 1.0
AXIS_HEIGHT = (MIDDLE_FLOOR + OUTER_FLOOR + 2 * GUIDE_HEIGHT) / 2
BARREL_RADIUS = 1.5
HINGE_OFFSET = 1.9
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
MAGNET_DIAMETER = 5.32
MAGNET_DEPTH = 2.8
MAGNET_HEIGHT = 2.58
MAGNET_SEAT_HEIGHT = 2 * AXIS_HEIGHT - 0.2
MAGNET_WALL = 0.6
MAGNET_RADIUS = MAGNET_DIAMETER / 2 + MAGNET_WALL
MAGNET_X = 3.2
MAGNET_Y = WIDTH * 0.32
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


def _spring():
    """藏在左导轨井内的横向悬臂，只有自由端压头穿过侧口。"""
    tip_y = WIDTH / 2 + 7
    root_y = tip_y - 14
    root = END_BAND - 2
    tip = END_BAND - 1.2
    arm = polygon(
        [
            (root - SPRING_WIDTH, root_y - 4),
            (root, root_y - 4),
            (root, root_y),
            (tip, tip_y),
            (tip - SPRING_WIDTH, tip_y),
            (root - SPRING_WIDTH, root_y),
        ]
    ).extrude(SPRING_HEIGHT)
    head = polygon(
        [
            (tip - SPRING_WIDTH, tip_y - 1),
            (END_BAND + SPRING_INTRUSION - 0.25, tip_y - 1),
            (END_BAND + SPRING_INTRUSION, tip_y),
            (END_BAND + SPRING_INTRUSION - 0.25, tip_y + 1.2),
            (tip - SPRING_WIDTH, tip_y + 1.2),
        ]
    ).extrude(SPRING_HEIGHT)
    return arm + head


def _well():
    tip_y = WIDTH / 2 + 7
    pocket = _box(3.6, END_BAND - 0.6, tip_y - 16, tip_y + 2.6, -0.1, WELL_ROOF)
    return pocket + _box(
        END_BAND - 0.7, END_BAND + 1.5, tip_y - 1.4, tip_y + 1.6, -0.1, WELL_ROOF
    )


STRIP_Y0 = WIDTH / 2 - 13
STRIP_Y1 = WIDTH / 2 + 12
STRIP_BACK_WALL = 2.4
STRIP_X0 = STRIP_BACK_WALL + 0.2
STRIP_END_WALL = 0.8
DETENT_X = STRIP_X0 + 0.7
DETENT_Y = STRIP_Y0 + 2


def _rail(right=False):
    slope_start = GUIDE_HEIGHT - LIP_TOP_THICKNESS - LIP_RAMP_HEIGHT
    strip = polygon(
        [
            (0, 0),
            (END_BAND, 0),
            (END_BAND, slope_start),
            (END_BAND + LIP_UPPER_REACH, slope_start + LIP_RAMP_HEIGHT),
            (END_BAND + LIP_UPPER_REACH, GUIDE_HEIGHT),
            (0, GUIDE_HEIGHT),
        ]
    )
    if right:
        strip &= square(2.2, GUIDE_HEIGHT + 0.1).move(x=END_BAND - 1.4)
    rail = strip.extrude(WIDTH + 0.02).rotate(x=90).move(y=WIDTH + 0.01)
    return rail.mirror(x=1).move(x=LENGTH) if right else rail


def spring_panel():
    """侧向插入的短条，两端舌片置于有背墙支撑的扣沿下。"""
    footprint = _rounded(
        STRIP_X0,
        END_BAND + LIP_UPPER_REACH,
        STRIP_Y0 + STRIP_END_WALL + 0.9,
        STRIP_Y1 - STRIP_END_WALL - 0.9,
        0.3,
    )
    part = _rail() & footprint.extrude(GUIDE_HEIGHT + 0.1)
    for a, b in (
        (STRIP_Y0 + STRIP_END_WALL + 0.15, STRIP_Y0 + STRIP_END_WALL + 1),
        (STRIP_Y1 - STRIP_END_WALL - 1, STRIP_Y1 - STRIP_END_WALL - 0.15),
    ):
        part += _box(STRIP_X0, END_BAND, a, b, 0, 1.2)
    part = part - _well() + _spring()
    part -= cylinder(h=0.35, r=0.6, fn=48).move(x=DETENT_X, y=DETENT_Y, z=-0.1)
    lead_in = polygon(
        [
            (STRIP_X0 - 0.01, -0.01),
            (STRIP_X0 - 0.01, 0.25),
            (STRIP_X0 + 0.7, 0),
            (STRIP_X0 + 0.7, -0.01),
        ]
    )
    part -= lead_in.extrude(STRIP_Y1 - STRIP_Y0 + 1).rotate(x=90).move(y=STRIP_Y1 + 0.5)
    return part.as_original().simplify(1e-4).as_original().simplify(1e-4)


def _fixed_guides(outline=None):
    left = _rail()
    part = left + _rail(True)
    part -= _box(
        STRIP_BACK_WALL,
        END_BAND + LIP_UPPER_REACH + 0.2,
        STRIP_Y0 + STRIP_END_WALL,
        STRIP_Y1 - STRIP_END_WALL,
        -0.1,
        GUIDE_HEIGHT + 0.1,
    )
    # 封闭侧整段实心；每个扣沿与背墙重叠 0.2，不留断开的浮边。
    for a, b in (
        (STRIP_Y0 + STRIP_END_WALL - 0.02, STRIP_Y0 + STRIP_END_WALL + 0.6),
        (STRIP_Y1 - STRIP_END_WALL - 0.6, STRIP_Y1 - STRIP_END_WALL + 0.02),
    ):
        part += left & _box(
            STRIP_BACK_WALL - 0.2,
            END_BAND + LIP_UPPER_REACH + 0.1,
            a,
            b,
            GUIDE_HEIGHT - 0.4,
            GUIDE_HEIGHT + 0.1,
        )
    part -= _magnet_notches()
    # 定位凸点从完整底板上长出，装条时抬高 0.2 即可越过。
    part += cylinder(h=0.2, r=0.45, fn=48).move(x=DETENT_X, y=DETENT_Y)
    if outline is None:
        outline = _rounded(0, LENGTH, 0, WIDTH, RIM_RADIUS)
    return part & (outline & square(LENGTH, WIDTH)).extrude(GUIDE_HEIGHT + 0.1)


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

    return split(outer), split(ring)


def _magnet_notches():
    """通用导轨和中间层均让开四个组合位置，以保持中间两半完全相同。"""
    part = None
    for right in (False, True):
        for y in (MAGNET_Y, WIDTH - MAGNET_Y):
            cut = _box(
                -0.1,
                MAGNET_X + MAGNET_RADIUS + MAGNET_CLEARANCE,
                y - MAGNET_RADIUS - MAGNET_CLEARANCE,
                y + MAGNET_RADIUS + MAGNET_CLEARANCE,
                -0.1,
                2 * AXIS_HEIGHT + 0.1,
            )
            if right:
                cut = cut.mirror(x=1).move(x=LENGTH)
            part = cut if part is None else part + cut
    return part


def _magnet_seats():
    part = None
    for x, y in ((MAGNET_X, MAGNET_Y), (LENGTH - MAGNET_X, WIDTH - MAGNET_Y)):
        seat = cylinder(h=MAGNET_SEAT_HEIGHT, r=MAGNET_RADIUS, fn=96).move(x=x, y=y)
        seat -= cylinder(h=MAGNET_DEPTH + 0.1, r=MAGNET_DIAMETER / 2, fn=96).move(
            x=x, y=y, z=MAGNET_SEAT_HEIGHT - MAGNET_DEPTH
        )
        part = seat if part is None else part + seat
    return part


def _outer_rim():
    _, ring = _rim_profiles()
    part = ring.extrude(RIM_HEIGHT)
    # 给对侧铰链和其运动的根部留出空间。
    for start, end in ((0, PIN_SPAN), (HINGE_LENGTH - PIN_SPAN, HINGE_LENGTH)):
        part -= _box(
            -RIM_EXTENT - 0.1,
            0.1,
            HINGE_Y + start - AXIAL_GAP,
            HINGE_Y + end + AXIAL_GAP,
            2 * AXIS_HEIGHT - 0.4,
            RIM_HEIGHT + 0.1,
        )
    # 内侧磁铁座翻转经过对侧长边时，局部降低边框顶缘。
    part -= _box(
        -RIM_EXTENT - 0.1,
        0.1,
        MAGNET_Y - MAGNET_RADIUS - 0.4,
        MAGNET_Y + MAGNET_RADIUS + 0.4,
        RIM_HEIGHT - 1.0,
        RIM_HEIGHT + 0.1,
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
    part += _hinge(False, True) + _fixed_guides(floor_profile).move(z=OUTER_FLOOR)
    return part.as_original().simplify(1e-4).as_original().simplify(1e-4)


def middle_panel_half():
    part = _rounded(0, LENGTH, 0, WIDTH).extrude(MIDDLE_FLOOR)
    part = (
        part
        - _magnet_notches()
        + _hinge(True, False)
        + _fixed_guides().move(z=MIDDLE_FLOOR)
    )
    return part.as_original().simplify(1e-4)


def mounted_spring(floor):
    # 两种外壳均使用同向插槽和相同弹簧条，不需要镜像小件。
    return spring_panel().move(z=floor)


def folded_outer(angle=180, reverse=False, springs=True):
    part = outer_panel(reverse)
    if springs:
        part += mounted_spring(OUTER_FLOOR)
    return (
        part.move(x=-LENGTH - HINGE_OFFSET, z=-AXIS_HEIGHT)
        .rotate(y=angle)
        .move(x=-HINGE_OFFSET, z=AXIS_HEIGHT)
    )


def middle_assembly():
    return middle_panel_half() + mounted_spring(MIDDLE_FLOOR)


outer_a = outer_panel()
outer_b = outer_panel(True)
middle_half = middle_panel_half()
spring_strip = spring_panel()

show_closed = (
    middle_assembly()
    + middle_assembly().rotate(y=180).move(x=LENGTH)
    + folded_outer()
    + folded_outer(reverse=True).rotate(y=180).move(x=LENGTH)
).move(y=WIDTH + 25)
show_open = (
    middle_assembly()
    + middle_assembly().rotate(y=180).move(x=LENGTH)
    + folded_outer(45)
    + folded_outer(45, True).rotate(y=180).move(x=LENGTH)
).move(y=2 * WIDTH + 50)
