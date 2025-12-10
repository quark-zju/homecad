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


def u_shape(r1, thick, chamfer=False, top_right=False):
    c1 = W().cylinder(thick, r1).rotate_axis("X", 90)
    obj = c1
    if top_right:
        b2 = W().box(r1, thick, r1).align(c1, ">Z >X")
    else:
        b2 = W().box(r1 * 2, thick, r1).align(c1, ">Z")
    obj = obj.union(b2)
    if chamfer:
        d = thick - 0.2
        d2 = d * math.tan(math.radians(30))
        obj = obj.faces("<Y").edges("not >Z").chamfer(d, d2)
    return obj


@cq_cache
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
    # print(f"{m1x_dz=} {bu.measure("Z")=} {m1.measure("Z")=}")
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


def plate_male():
    R1 = 70 / 2
    # shorter side install first
    m1 = magnet_2_10_20(hole_depth=0.4).rotate_axis("X", 90)  # .rotate_axis("Z", 180)
    thick = m1.measure("Y")

    u1 = u_shape(R1, thick, chamfer=True, top_right=True)
    obj = u1

    reel_w = 3.4
    reel_w1 = 3.2
    reel_l = 14.4 + 2

    u2 = u1.surface_grow("<Y", reel_w)
    obj = obj.union(u2)

    s1 = (
        sector(R1 + 20, reel_w1, 45 + 6)
        .rotate_axis("X", 90)
        .rotate_axis("Y", 90 + 3)
        .align(u2, "<Y")
    )
    obj = obj.union(s1)

    m_edge = 4
    m1e = m1.align(u1, "<Y >Z", dz=-m_edge)
    for angle in range(0, 360, 90):
        m1r = m1e.rotate_axis("Y", angle)
        obj = obj.cut(m1r)
        obj = obj.cut(m1r.surface_grow("<Y", u2.measure("Y")))

    b_reel = W().box(reel_l, reel_w, reel_w)  # to cut
    b2 = (
        W()
        .box(37 + reel_l - 14, reel_w1, reel_w + 7)
        .align(obj, "<Y :>X", dx=-10)
        .faces(">X")
        .workplane(centerOption="CenterOfBoundBox")
        .hole(2)
    )
    m1x_dz = math.sqrt(2) * (100 - 20) / 2 - m_edge
    b_reelx = b_reel.align(u1, ":<Y -X -Z", dx=m1x_dz)
    b_wire_hole = (
        W().box(20, 2.4, 2).align(obj, "<Y :>X", dx=-5).faces(">Y").fillet(0.99)
    )
    for angle in [90, 45]:
        obj = obj.union(b2.rotate_axis("Y", angle))
        obj = obj.cut(b_reelx.rotate_axis("Y", angle))
    for angle in [90, 75, 60, 45]:
        obj = obj.cut(b_wire_hole.rotate_axis("Y", angle))
    u3 = u_shape(R1 + 2, 1.4, top_right=True).align(u2, "<Y")
    obj = obj.cut(u3.cut(u2))
    return obj


def mag_test():
    m1 = magnet_2_10_20(hole_depth=0.4).rotate_axis("X", 180)
    x, y, z = m1.measure()
    b1 = W().box(x + 4, y + 4, z).align(m1, "<Z")
    obj = b1.cut(m1)
    return obj


def render():
    obj1 = plate_female()
    obj1.rotate_axis("X", 270).export("female")
    obj2 = plate_male()
    obj2.rotate_axis("X", 90).export("male")
    obj = obj1.union(obj2.translate((0, -2.5, 0)))
    return obj


render().show()
