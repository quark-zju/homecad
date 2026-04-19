"""
Pocket closure strip

A pair of strips designed to hold embedded magnets and attach to the inside of a pocket opening.

The round holes and slots fit [5mm tag pins](https://www.amazon.com/10000-Stitch-Fasteners-Tagging-Include/dp/B0DJSSRRBG) for easy attachment.

The rectangle slots are for [60x10x3mm magnets](https://www.amazon.com/dp/B0CN6T35TJ). The magnetic connection helps keep pocket openings closed and prevents small items from falling out.
"""

from cqutils import *
from magnet import magnet31060


def mag_box(front=True):
    m = magnet31060(hole_depth=0.6).rotate_axis("Y", 180)
    if not front:
        x, y, z = m.measure()
        m = W().box(x, y, 3)
    m_bbox = m.bbox()
    y_pad = 8
    b = W().box(m_bbox.xlen + 5, m_bbox.ylen + y_pad * 2, m_bbox.zlen)
    obj = b.cut(m.align(b, "<Z"))
    r = 3 / 2
    c = W().cylinder(m_bbox.zlen, r)
    c1 = c.align(obj, "<Y", dy=(y_pad - r) / 2)
    c2 = c.align(obj, ">Y", dy=-(y_pad - r) / 2)
    sw = 1.4
    st = 1.6
    if front:
        slot = W().box(7, sw, st)  # .edges(">Z and |Y").chamfer(0.4, 1)
        s1 = slot.align(c1, ">Z <Y", dy=r - sw / 2)
        s2 = slot.align(c2, ">Z <Y", dy=r - sw / 2)
        obj = obj.cut(s1).cut(s2)
    obj = obj.cut(c1).cut(c2)
    return obj


def get_bar(front=True):
    obj = mag_box(front)
    # b = W().box(*m.measure())
    # b1 = b.faces(">Z or <Z").shell(-2)
    # b1 = b1.union(b.faces(">Z").shell(-1))
    # b2 = b1.align(m, ":>Y <Z")
    # t = W(
    #     obj=cq.Compound.makeText(
    #         front and "FRONT" or "BACK", 6, 1.4, font="Noto Sans", kind="bold"
    #     )
    # )
    # t = t.rotate_axis("Z", 90).align(b2, "<Z -Y")
    # obj = m.union(b2)  # .union(t)
    # obj = obj.union(m.rotate_axis("Z", 180).align(obj, ":>Y <Z"))
    # obj = obj.union(b.align(obj, ":>Y <Z"))
    # obj = obj.union(m.align(obj, ":>Y <Z"))
    b_outer = (
        W()
        .box(*obj.measure())
        .align(obj, "<Y")
        .edges("|Z")
        .fillet(4)
        .faces(">Z")
        .fillet(1.4)
    )
    obj = obj.intersect(b_outer)
    return obj


def render():
    front = get_bar(True).export("front")
    back = get_bar(False).export("back").align(front, "<Z")
    print(f"{front.measure()=} {back.measure()=}")
    return front.union(back.align(front, ":>X", dx=2))


render().export().show()
