"""
Holder for rack edges and pico remote

Includes 2 parts that connect to each other:

- A holder that attach to the edges of [racks like this](https://www.amazon.com/dp/B09W2Y51TC/).
- A holder that attach to a [Pico remote](https://www.amazon.com/Lutron-3-Button-Wireless-Lighting-PJ2-3BRL-WH-L01R/dp/B00KLAXFQ0).
"""

from cqutils import *

W = Workplane()

# pico plate
bottom_width = 26.9
bottom_height = 36.6
bottom_thick = 0.8

top_height = 34
top_width = 24
top_thick = 1.95 - bottom_thick


def pico_remote_plate():
    """print_from: <Z"""
    min_height = min(top_height, bottom_height)
    b1 = W.box(bottom_width, min_height, bottom_thick).edges("|Z").fillet(0.8)
    b2 = W.box(top_width, min_height, top_thick)
    b2 = b2.align(b1, ":>Z >Y -X")
    return b1.union(b2)


trapezoid_z = 20


def _trapezoid(dx=0):
    return trapezoid(10 + dx, 2, trapezoid_z)


def pico_remote_plate_with_attacher():
    o1 = pico_remote_plate()
    t1 = _trapezoid(dx=0.4).rotate_axis("X", 90).align(o1, "<Z <Y")
    t1b = t1.solid_box(dx=2)
    t1v = t1b.cut(t1)
    o1v = o1.cut(t1b)
    o = union_all([o1v, t1v])
    o.export("pico", print_from_face="<Z")
    return o


def rack_edge_holder():
    # matches rack edge
    dh = 21.0  # rack edge height
    dt = 4.4  # rack edge thick
    pad = 2
    w = 16
    h = dt + pad * 2
    z = dh + pad * 2
    b1 = W.box(w, h, z)
    b1c = W.box(w, dt, dh).align(b1, "<Z")
    b1v = b1.cut(b1c)
    t1 = trapezoid(pad, pad, w, dx2=0).rotate_axis("Y", 90).rotate_axis("X", 90)
    t1a = t1.align(b1, ">Y :<Z <X")
    t1b = t1.rotate_axis("Z", 180).align(b1, "<Y :<Z <X")
    t1c = t1a.rotate_axis("Y", 180).align(t1a, ":<Z")
    t1d = t1b.rotate_axis("Y", 180).align(t1b, ":<Z")
    t2 = _trapezoid().align(b1, "-X >Z :<Y")
    o = union_all([b1v, t1a, t1b, t1c, t1d, t2])
    o.export("rack", print_from_face=">Z")
    return o


def render():
    o1 = rack_edge_holder()
    o2 = (
        pico_remote_plate_with_attacher()
        .rotate_axis("X", 90)
        .rotate_axis("Z", 180)
        .align(o1, ":>Z <Y", dz=1 - trapezoid_z)
    )
    return union_all([o1, o2])


render().show()
