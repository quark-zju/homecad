from cqutils import *


def magnet2510(hole_depth=1, c1a=0.4, c1b=1.0, c2=0.6):
    """slot for magnet: 1.7mm x 9.8mm x 4.7mm"""
    m_w = 5.0
    m_h = 2.2
    m_t = 10.1
    obj = b = (
        W()
        .box(m_w, m_t, m_h)
        .edges("|X and <Z and <Y")
        .chamfer(c1a, c2)
        .edges("|X and <Z and >Y")
        .chamfer(c1b, c2)
    )
    if hole_depth:
        # b1 is to punch a "hole" to make it easier to remove the magnet later
        b1 = W().box(m_w, m_w, hole_depth).align(b, ":>Z")
        b1 = b1.translate((0, c1b - c1a, 0))
        obj = obj.union(b1)
    return obj


if __name__ == "__cq_main__":
    result = W()
    for i, c1b in enumerate([0.4, 0.6, 0.8, 1.0]):
        obj = magnet2510(c1b=c1b)
        bbox = obj.bbox()
        b2 = W().box(bbox.xlen + 3, bbox.ylen + 3, bbox.zlen)
        b2 = b2.cut(obj.align(b2, "<Z"))
        result = result.translate((-10, 0, 0)).union(b2)
    result.show().export()
