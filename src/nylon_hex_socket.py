"""分体尼龙螺丝／螺母套筒和精密螺丝刀六角轴，单位 mm。

HEAD_AF 是实测对边宽，CLEARANCE 是对边总增量（不是单侧间隙）。
旧试配件的导出已注释；fit_040 / fit_050 / fit_060 用于螺丝／螺母端。
环高 3 / 3.4 / 3.8 mm 分别对应 0.40 / 0.50 / 0.60 mm 对边总增量。
drive_000 / drive_010 / drive_020 是公柄试配件，圆底座上 1 / 2 / 3 个
缺口分别对应柄对边减小 0 / 0.10 / 0.20 mm，选好后设置 DRIVE_REDUCTION。
中心 Ø4 mm 孔允许螺杆越过六角孔底继续伸入 3 mm，轴端止于让位孔下方。
六角孔底通过 1.5 mm 高斜面收进中心孔，消除内部平肩。
套筒为对边 8.4 mm 的直壳，前口朝上沿 Z 打印；背面六角孔深 7 mm。
独立实心轴对边 3.97 mm，总长 17 mm，其中 7 mm 插入套筒，10 mm 外露。
JOINT_CLEARANCE 单独控制背孔的对边总增量，默认 0.5 mm，需实际试配。
轴已摆为水平、一个侧面贴床；套筒和轴建议 0.16 mm 层高、5 圈墙、
100% 填充。show_assembly 仅供装配预览。连接无锁定结构，松配可少量粘接。
室温轻载可先用 PLA；水平轴的配合和抗扭性能尚待实物验证。
"""

from math import cos, pi

from b4dcad import cylinder

HEAD_AF = 5.44
CLEARANCE = 0.50
SOCKET_DEPTH = 3.2
SOCKET_TRANSITION_HEIGHT = 1.5
ENTRY_CHAMFER = 0.15
DRIVE_AF = 3.97
DRIVE_REDUCTION = 0.0
DRIVE_LENGTH = 10.0
BODY_AF = 8.4
JOINT_LENGTH = 7.0
JOINT_CLEARANCE = 0.50
SCREW_CLEARANCE_LENGTH = 3.0
SCREW_CLEARANCE_DIAMETER = 4.0


def _hex(af, height, top_af=None):
    radius = af / (2 * cos(pi / 6))
    top_radius = radius if top_af is None else top_af / (2 * cos(pi / 6))
    return cylinder(h=height, r=radius, r2=top_radius, fn=6)


def _socket_cut(af, depth):
    # 开口在 z=0，内部朝 -Z；只在入口最后 0.15 mm 放大。
    straight = _hex(af, depth + 0.01).move(z=-depth)
    entry = _hex(af, ENTRY_CHAMFER, af + 2 * ENTRY_CHAMFER).move(z=-ENTRY_CHAMFER)
    return straight + entry


def _drive(af, length=DRIVE_LENGTH):
    tip = _hex(af - 0.6, 0.3, af)
    return tip + _hex(af, length - 0.3).move(z=0.3)


def make_shaft(reduction=DRIVE_REDUCTION):
    """沿 Z 的等截面轴，螺丝刀端 z=0，套筒端为平端，止于背孔台阶。"""
    return _drive(DRIVE_AF - reduction, DRIVE_LENGTH + JOINT_LENGTH)


def make_socket(head_af=HEAD_AF, clearance=CLEARANCE, joint_clearance=JOINT_CLEARANCE):
    """直壳套筒；z=0 为轴插口，顶部为螺丝／螺母插口。

    检查装配、轴插入过程、螺丝刀插座以及螺母伸出的 M3 螺杆。

    >>> part = make_socket()
    >>> floor = JOINT_LENGTH + SCREW_CLEARANCE_LENGTH
    >>> nut = _hex(HEAD_AF, SOCKET_DEPTH - 0.02).move(z=floor + 0.01)
    >>> rod = cylinder(d=3, h=SCREW_CLEARANCE_LENGTH + SOCKET_DEPTH - 0.02, fn=96).move(z=JOINT_LENGTH + 0.01)
    >>> (part & (nut + rod)).is_empty()
    True
    >>> shaft = make_shaft().move(z=-DRIVE_LENGTH)
    >>> abs((part & shaft).manifold.volume()) < 1e-7
    True
    >>> all(abs((part & shaft.move(z=-distance)).manifold.volume()) < 1e-7 for distance in (0.1, 1, 3, 7))
    True
    >>> receiver = (cylinder(d=9, h=DRIVE_LENGTH) - _hex(DRIVE_AF + 0.05, DRIVE_LENGTH)).move(z=-DRIVE_LENGTH)
    >>> (shaft & receiver).is_empty()
    True
    >>> (shaft & rod).is_empty()
    True
    >>> (part & shaft.move(z=0.5)).manifold.volume() > 0
    True
    >>> (part & shaft.rotate(z=30)).manifold.volume() > 0
    True
    """
    bore_bottom = JOINT_LENGTH
    top = bore_bottom + SCREW_CLEARANCE_LENGTH + SOCKET_DEPTH
    body = _hex(BODY_AF, top)
    joint = _socket_cut(DRIVE_AF + joint_clearance, JOINT_LENGTH).rotate(x=180)
    bore = cylinder(h=top - bore_bottom + 0.01, d=SCREW_CLEARANCE_DIAMETER).move(
        z=bore_bottom
    )
    # 下端略缩小，完全落在圆孔的多边形网格内，不留下水平台阶。
    transition = _hex(
        (SCREW_CLEARANCE_DIAMETER - 0.04) * cos(pi / 6),
        SOCKET_TRANSITION_HEIGHT,
        head_af + clearance,
    ).move(z=top - SOCKET_DEPTH - SOCKET_TRANSITION_HEIGHT)
    return (
        body
        - joint
        - _socket_cut(head_af + clearance, SOCKET_DEPTH).move(z=top)
        - bore
        - transition
    )


def _mark(part, marks, radius, height):
    for i in range(marks):
        notch = (
            cylinder(h=height + 0.2, r=0.6, fn=32)
            .move(y=radius, z=-0.1)
            .rotate(z=(i - (marks - 1) / 2) * 25)
        )
        part -= notch
    return part


def fit_ring(clearance, head_af=HEAD_AF, *, height=3):
    """通孔试配环，用明显不同的高度辨认；入口倒角相同。"""
    return cylinder(h=height, r=5, fn=96) - _socket_cut(
        head_af + clearance, height + 0.1
    ).move(z=height)


def drive_sample(reduction, *, marks):
    """圆底座便于手持试配，柄形状与正式件相同。"""
    base = _mark(cylinder(h=2, r=4.5, fn=96), marks, 4.5, 2)
    return base + _drive(DRIVE_AF - reduction).move(z=2)


socket = make_socket()
shaft = make_shaft().rotate(x=90).rotate(z=90).align(xmin=0, ymin=10, zmin=0)
show_assembly = (socket + make_shaft().move(z=-DRIVE_LENGTH)).move(x=-16)

# fit_040 = fit_ring(0.40, height=3).move(x=17, y=-11)
# fit_050 = fit_ring(0.50, height=3.4).move(x=17)
# fit_060 = fit_ring(0.60, height=3.8).move(x=17, y=11)
# drive_000 = drive_sample(0, marks=1).move(x=28, y=-11)
# drive_010 = drive_sample(0.10, marks=2).move(x=28)
# drive_020 = drive_sample(0.20, marks=3).move(x=28, y=11)
