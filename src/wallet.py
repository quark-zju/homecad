"""沿卡片长边折叠的三折四槽卡包，单位 mm；总容量 4–8 张。

outer_a / outer_b 各打印一件，middle_half 打印两件，均平放，孔内不用支撑。
中间两半背面对粘，其中一半绕 Y 翻转 180 度，两边对齐；背面两端对应弹片
与切缝的位置均不涂胶，以免将任一面的弹片粘在另一半底板上。
两处铰链各用两段约 16 长、直径 0.8 的裸回形针，共四段。每处左—右—左
三节轴套，水平尖顶孔 1.0、外径 3，配合沿用已验证试片；轴高按满载提高。
零件对齐后从中间向外插轴到盲孔底，确认转动后在中间半片的两个凹口点胶。
每片外层内侧一槽，中间层正反各一槽，均可放 1–2 张卡；不留半圆取卡口。
两片外壳各有一个 L 形边框，闭合后互补封住四边。外层从未封的短边滑动取卡，
中间层两短边均可取卡；闭合后两端挡墙阻挡四槽卡片，不只依赖弹片摩擦力。
侧边一体弹片横向压住卡边，兼容单卡/双卡；其手感尚需实物验证。
导轨上唇有 0.8 悬伸及 45 度下斜面，最小厚度 0.4，检查切片中上唇连续。

八枚磁铁：直径实测 5.02、高 2.58；孔径 5.32、深 2.8，沿用实测配合。
每折自由长边有两个吸合点，安装前干装核对四对磁极，再胶粘磁铁。
边框仅沿板面外侧加厚，无向内折边；长边在对侧铰链处局部避让。
外壳挡墙跨过四槽高度，离对侧底板内面留 0.2；相邻边框转角留 0.4 间隙。
不做暂停埋箔，卡槽底面可贴箔。
铝箔与胶层占用卡槽余量，避开弹片切缝；本版不保证屏蔽效果。
show_* 为不导出的装配预览，折叠角 0 为摊开，180 为闭合。
"""

import math

from b4dcad import circle, cube, cylinder, polygon, square

CARD_LENGTH = 85.6
CARD_WIDTH = 53.98
CARD_THICKNESS = 0.8
CARD_CLEARANCE = 0.6
FLOOR = 1.0
END_BAND = 7.2
SIDE_MARGIN = 3.0
# X 为折叠横向，Y 为铰链轴向；卡片长边沿 Y，像手机沿长边翻开。
SLOT_LENGTH = CARD_WIDTH + CARD_CLEARANCE
SLOT_WIDTH = CARD_LENGTH + CARD_CLEARANCE
LENGTH = SLOT_LENGTH + 2 * END_BAND
WIDTH = SLOT_WIDTH + 2 * SIDE_MARGIN
RAIL_HEIGHT = 4.0
LIP_OVERLAP = 0.8
LIP_UNDERSIDE = FLOOR + 2 * CARD_THICKNESS + 0.2
SPRING_INTRUSION = 0.95
SPRING_WIDTH = 1.4

PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BORE_DIAMETER = 1.0
AXIS_HEIGHT = (2 * RAIL_HEIGHT + 0.2) / 2
BARREL_RADIUS = 1.5
HINGE_OFFSET = 2.6
AXIAL_GAP = 0.3
BLIND_WALL = 0.8
PIN_RECESS = 0.5
PIN_SPAN = BLIND_WALL + PIN_LENGTH + PIN_RECESS
END_KNUCKLE = 5.6
HINGE_LENGTH = max(2 * PIN_SPAN + PIN_LENGTH + 2, WIDTH - 8)
HINGE_Y = (WIDTH - HINGE_LENGTH) / 2
MAGNET_DIAMETER = 5.32
MAGNET_DEPTH = 2.8
MAGNET_POSITIONS = (0.3, 0.7)
RIM_WALL = 1.2
RIM_GAP = 0.4
RIM_EXTENT = RIM_WALL + RIM_GAP
RIM_HEIGHT = 4 * AXIS_HEIGHT - FLOOR - 0.2
OUTER_OPEN_EDGE_HEIGHT = FLOOR + 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return cube(x1 - x0, y1 - y0, z1 - z0).move(x=x0, y=y0, z=z0)


def _axial_cylinder(diameter, start, end, x=0):
    return (
        cylinder(h=end - start, r=diameter / 2, fn=64)
        .rotate(x=-90)
        .move(x=x, y=start, z=AXIS_HEIGHT)
    )


def _roof_bore(start, end, x):
    r = BORE_DIAMETER / 2
    t = r / math.sqrt(2)
    profile = circle(r=r, fn=64) + polygon([(-t, t), (t, t), (0, r * math.sqrt(2))])
    return profile.extrude(end - start).rotate(x=90).move(x=x, y=end, z=AXIS_HEIGHT)


def _hinge(ends, right_edge):
    """ends 件承两端轴套及封胶口，中间节件连接外层；轴向几何沿用试片。"""
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
        for y0, y1 in (
            (HINGE_Y + PIN_SPAN - 1, HINGE_Y + PIN_SPAN + 0.1),
            (
                HINGE_Y + HINGE_LENGTH - PIN_SPAN - 0.1,
                HINGE_Y + HINGE_LENGTH - PIN_SPAN + 1,
            ),
        ):
            part -= _axial_cylinder(1.8, y0, y1, x)
    return part


def _left_rail():
    # X/Z 截面：厚边上唇向卡片投影 0.8，下表面 45 度过渡。
    return (
        polygon(
            [
                (0, 0),
                (END_BAND, 0),
                (END_BAND, LIP_UNDERSIDE),
                (END_BAND + LIP_OVERLAP, LIP_UNDERSIDE + LIP_OVERLAP),
                (END_BAND + LIP_OVERLAP, RAIL_HEIGHT),
                (0, RAIL_HEIGHT),
            ]
        )
        .extrude(WIDTH)
        .rotate(x=90)
        .move(y=WIDTH)
    )


def _spring():
    """1.4 宽、有效长 14 的平面悬臂，尖端导入卡片；仅压卡片侧边。"""
    root = END_BAND - 0.4
    tip = END_BAND + SPRING_INTRUSION
    tip_y = WIDTH - 11.6
    root_y = tip_y - 14
    return polygon(
        [
            (root - SPRING_WIDTH, root_y - 4),
            (root, root_y - 4),
            (root, root_y),
            (tip, tip_y),
            (tip - 0.25, tip_y + 2),
            (tip - SPRING_WIDTH - 0.25, tip_y + 2),
            (tip - SPRING_WIDTH, tip_y),
            (root - SPRING_WIDTH, root_y),
        ]
    ).extrude(FLOOR + 2 * CARD_THICKNESS + 0.2)


def _tray(magnet_left, back_stop=True):
    part = _box(0, LENGTH, 0, WIDTH, 0, FLOOR)
    rail = _left_rail()
    part += rail + rail.rotate(z=180).move(x=LENGTH, y=WIDTH)
    if back_stop:
        part += _box(
            END_BAND - 0.1, LENGTH - END_BAND + 0.1, 0, SIDE_MARGIN, 0, FLOOR + 1.8
        )
    # 留出弹片两侧及自由端的贯穿切缝，避免弹片与底板连死。
    cut = _box(
        END_BAND - 0.4 - SPRING_WIDTH - 0.8,
        END_BAND + SPRING_INTRUSION + 0.55,
        WIDTH - 27.6,
        WIDTH - 8.6,
        -0.1,
        RAIL_HEIGHT + 0.1,
    )
    spring = _spring()
    if magnet_left:
        cut = cut.mirror(x=1).move(x=LENGTH)
        spring = spring.mirror(x=1).move(x=LENGTH)
    part = part - cut + spring
    magnet_x = END_BAND / 2 if magnet_left else LENGTH - END_BAND / 2
    for fraction in MAGNET_POSITIONS:
        part -= cylinder(h=MAGNET_DEPTH + 0.1, r=MAGNET_DIAMETER / 2, fn=96).move(
            x=magnet_x, y=WIDTH * fraction, z=RAIL_HEIGHT - MAGNET_DEPTH
        )
    outline = (
        square(LENGTH - 4, WIDTH - 4)
        .offset(2, "round")
        .align(xmin=0, ymin=0)
        .extrude(RAIL_HEIGHT + 0.1)
    )
    return part & outline


def _outer_rim():
    """打印坐标下封左边及下边；上缘在对侧铰链组处退让。"""
    part = _box(-RIM_EXTENT, 0.1, 0, WIDTH, 0, FLOOR)
    part += _box(-RIM_EXTENT, LENGTH + RIM_EXTENT, -RIM_EXTENT, 0.1, 0, FLOOR)
    part += _box(-RIM_EXTENT, -RIM_GAP, -RIM_EXTENT, WIDTH, 0, RIM_HEIGHT)
    part += _box(-RIM_EXTENT, LENGTH + RIM_EXTENT, -RIM_EXTENT, -RIM_GAP, 0, RIM_HEIGHT)
    for start, end in ((0, PIN_SPAN), (HINGE_LENGTH - PIN_SPAN, HINGE_LENGTH)):
        part -= _box(
            -RIM_EXTENT - 0.1,
            0.1,
            HINGE_Y + start - AXIAL_GAP,
            HINGE_Y + end + AXIAL_GAP,
            2 * AXIS_HEIGHT - 0.2,
            RIM_HEIGHT + 0.1,
        )
    return part


def outer_panel(reverse=False):
    tray = _tray(magnet_left=True)
    # 铰链侧保持低导向边，避免翻开时刮到另一片外壳的跨层边框。
    tray -= _box(
        LENGTH - END_BAND - LIP_OVERLAP - 0.1,
        LENGTH + 0.1,
        -0.1,
        WIDTH + 0.1,
        OUTER_OPEN_EDGE_HEIGHT,
        RAIL_HEIGHT + 0.1,
    )
    tray += _spring().mirror(x=1).move(x=LENGTH)
    part = tray + _hinge(ends=False, right_edge=True) + _outer_rim()
    if reverse:
        part = part.mirror(y=1).move(y=WIDTH)
    return part.simplify(1e-6)


def middle_panel_half():
    return (
        _tray(magnet_left=False, back_stop=False) + _hinge(ends=True, right_edge=False)
    ).simplify(1e-6)


def folded_outer(angle=180, reverse=False):
    """正面外层从中间层左侧向上折；返回中间层坐标系的装配姿态。"""
    return (
        outer_panel(reverse)
        .move(x=-LENGTH - HINGE_OFFSET, z=-AXIS_HEIGHT)
        .rotate(y=angle)
        .move(x=-HINGE_OFFSET, z=AXIS_HEIGHT)
    )


outer_a = outer_panel()
outer_b = outer_panel(reverse=True).move(x=LENGTH + 15)
middle_half = middle_panel_half().move(x=2 * (LENGTH + 15))

show_closed = (
    middle_panel_half()
    + middle_panel_half().rotate(y=180).move(x=LENGTH)
    + folded_outer()
    + folded_outer(reverse=True).rotate(y=180).move(x=LENGTH)
).move(y=WIDTH + 20)

show_open = (
    middle_panel_half()
    + middle_panel_half().rotate(y=180).move(x=LENGTH)
    + folded_outer(45)
    + folded_outer(45, reverse=True).rotate(y=180).move(x=LENGTH)
).move(y=2 * WIDTH + 40)
