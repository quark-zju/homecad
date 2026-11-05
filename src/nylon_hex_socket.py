"""尼龙外六角螺丝的手拧套筒，尺寸单位 mm。

HEAD_AF 是实测对边宽，CLEARANCE 是对边总增量（不是单侧间隙）。
先打印 fit_010 / fit_020 / fit_030，选能顺畅套入且晃动最小的间隙。
套筒开口朝上打印，建议 0.16 mm 层高、5 圈墙、100% 填充，无需支撑。
室温轻载可先用 PLA；仅供手拧，尚未验证实际扭矩。
"""

from math import cos, pi

from b4dcad import cylinder

HEAD_AF = 5.0
HEAD_HEIGHT = 2.0
CLEARANCE = 0.20
SOCKET_DEPTH = HEAD_HEIGHT + 0.6
ENTRY_CHAMFER = 0.15


def _hex(af, height, top_af=None):
    radius = af / (2 * cos(pi / 6))
    top_radius = radius if top_af is None else top_af / (2 * cos(pi / 6))
    return cylinder(h=height, r=radius, r2=top_radius, fn=6)


def _socket_cut(af, depth):
    # 开口在 z=0，内部朝 -Z；只在入口最后 0.15 mm 放大。
    straight = _hex(af, depth + 0.01).move(z=-depth)
    entry = _hex(af, ENTRY_CHAMFER, af + 2 * ENTRY_CHAMFER).move(z=-ENTRY_CHAMFER)
    return straight + entry


def make_socket(head_af=HEAD_AF, clearance=CLEARANCE):
    """20 mm 指拧柄、12 mm 外径套筒；平底朝下、开口朝上。"""
    grip = cylinder(h=4, r=10, fn=12)
    shoulder = cylinder(h=4, r=10, r2=6, fn=12).move(z=4)
    nose = cylinder(h=8.01, r=6, fn=96).move(z=7.99)
    return (
        grip
        + shoulder
        + nose
        - _socket_cut(head_af + clearance, SOCKET_DEPTH).move(z=16)
    )


def fit_ring(clearance, head_af=HEAD_AF):
    """3 mm 高通孔试配环，入口与正式套筒相同。"""
    return cylinder(h=3, r=4.5, fn=96) - _socket_cut(head_af + clearance, 3.1).move(z=3)


socket = make_socket()
fit_010 = fit_ring(0.10).move(x=17, y=-11)
fit_020 = fit_ring(0.20).move(x=17)
fit_030 = fit_ring(0.30).move(x=17, y=11)
