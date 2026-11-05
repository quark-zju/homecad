"""尼龙外六角螺丝／螺母套筒，配精密螺丝刀六角柄，单位 mm。

HEAD_AF 是实测对边宽，CLEARANCE 是对边总增量（不是单侧间隙）。
先打印 fit_040 / fit_050 / fit_060，选能顺畅套入且晃动最小的间隙。
环高 3 / 3.4 / 3.8 mm 分别对应 0.40 / 0.50 / 0.60 mm 对边总增量。
drive_000 / drive_010 / drive_020 是公柄试配件，圆底座上 1 / 2 / 3 个
缺口分别对应柄对边减小 0 / 0.10 / 0.20 mm，选好后设置 DRIVE_REDUCTION。
中心 Ø4 mm 孔允许螺杆越过六角孔底继续伸入 3 mm；公柄及其根部保持实心。
套筒开口朝上、柄端朝下打印，加 brim；建议 0.16 mm 层高、5 圈墙、
100% 填充，无需支撑。公柄靠插入深度传递扭矩，无卡珠或锁定结构。
室温轻载可先用 PLA；仅供手拧，尚未验证实际扭矩。
"""

from math import cos, pi

from b4dcad import cylinder

HEAD_AF = 5.44
CLEARANCE = 0.50
SOCKET_DEPTH = 3.2
ENTRY_CHAMFER = 0.15
DRIVE_AF = 3.97
DRIVE_REDUCTION = 0.0
DRIVE_LENGTH = 10.0
SHOULDER_HEIGHT = 4.0
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


def _drive(af):
    tip = _hex(af - 0.6, 0.3, af)
    return tip + _hex(af, DRIVE_LENGTH - 0.3).move(z=0.3)


def make_socket(head_af=HEAD_AF, clearance=CLEARANCE, reduction=DRIVE_REDUCTION):
    """10 mm 长公六角柄、10 mm 对边外壳，默认总长 17.2 mm。"""
    af = DRIVE_AF - reduction
    shoulder = _hex(af, SHOULDER_HEIGHT, 10).move(z=DRIVE_LENGTH)
    body_z = DRIVE_LENGTH + SHOULDER_HEIGHT
    # 让位孔从渐扩肩部开始，避开薄弱的公柄及其根部。
    bore_bottom = DRIVE_LENGTH + 1.0
    top = bore_bottom + SCREW_CLEARANCE_LENGTH + SOCKET_DEPTH
    body = _hex(10, top - body_z).move(z=body_z)
    bore = cylinder(h=top - bore_bottom + 0.01, d=SCREW_CLEARANCE_DIAMETER).move(
        z=bore_bottom
    )
    return (
        _drive(af)
        + shoulder
        + body
        - _socket_cut(head_af + clearance, SOCKET_DEPTH).move(z=top)
        - bore
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
fit_040 = fit_ring(0.40, height=3).move(x=17, y=-11)
fit_050 = fit_ring(0.50, height=3.4).move(x=17)
fit_060 = fit_ring(0.60, height=3.8).move(x=17, y=11)
drive_000 = drive_sample(0, marks=1).move(x=28, y=-11)
drive_010 = drive_sample(0.10, marks=2).move(x=28)
drive_020 = drive_sample(0.20, marks=3).move(x=28, y=11)
