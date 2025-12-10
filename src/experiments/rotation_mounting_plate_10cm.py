from cqutils import *
from magnet import magnet_2_10_20
import math


# 4 medium-sized strips; modify as needed
WIDTH = 63 - 0.2 - 0.3
WIDTH1 = WIDTH / 4
HEIGHT = 46
ROUND = 7
THICK = 2

SEAM = 0.16
SEAM_THICK = 0.06


def u_shape(r1, thick, chamfer=False):
    c1 = W().cylinder(thick, r1).rotate_axis("X", 90)
    obj = c1
    b2 = W().box(r1 * 2, thick, r1).align(c1, ">Z")
    obj = obj.union(b2)
    if chamfer:
        d = thick - 0.2
        d2 = d * math.tan(math.radians(30))
        obj = obj.faces("<Y").edges("not >Z").chamfer(d, d2)
    return obj


def plate_female():
    R1 = 70 / 2
    m1 = magnet_2_10_20(hole_depth=0.4).rotate_axis("X", -90)
    thick = m1.measure("Y")

    b1 = W().box(WIDTH, thick, HEIGHT)
    u1 = u_shape(R1, thick)

    border = 30
    bu = (
        W()
        .box(R1 * 2 + border, thick * 2, R1 * 2 + border)
        .align(u1, ">Y")
        .edges("|Y and >Z")
        .fillet(border / 2)
    )
    obj = bu

    b2 = W().box(WIDTH1, thick * 2, HEIGHT * 10).align(u1, ">Y")
    b2a = b2.align(b1, "<X", dx=WIDTH1 / 2)
    b2b = b2.align(b1, ">X", dx=-WIDTH1 / 2)
    obj = obj.cut(b2a).cut(b2b).union(b1)

    u2 = u_shape(R1 + 0.4, thick, chamfer=True).align(bu, "<Y")
    u2z = u2.surface_grow(">Z", bu.measure("Z"))
    obj = obj.cut(u2).cut(u2z)

    m_edge = 4
    m1e = m1.align(u1, "<Y >Z", dz=-m_edge)
    for angle in range(0, 360, 90):
        obj = obj.cut(m1e.rotate_axis("Y", angle))

    m1x_dz = math.sqrt(2) * (bu.measure("Z") - m1.measure("Z")) / 2 - m_edge
    m1x = (
        magnet_2_10_20(hole_depth=thick * 2)
        .rotate_axis("X", -90)
        .align(bu, "<Y -Z", dz=m1x_dz)
    )
    for angle in [135, 225]:
        obj = obj.cut(m1x.rotate_axis("Y", angle))

    c1 = W().cylinder(thick * 2, 2).rotate_axis("X", 90)
    obj = obj.cut(c1)

    return obj


def render():
    obj = plate_female()
    obj.rotate_axis("X", 270).export("female")
    return obj


render().show()
