from cqutils import *
from functools import partial


@cq_cache
def _magnet(
    m_w, m_h, m_t, hole_depth=1, c1a=0.4, c1b=1.0, c2=0.6, thick=None, round_hole=None
):
    obj = b = (
        W()
        .box(m_w, m_t, m_h)
        .edges("|X and <Z and <Y")
        .chamfer(c1a, c2)
        .edges("|X and <Z and >Y")
        .chamfer(c1b, c2)
    )
    if thick is not None:
        hole_depth = thick - m_h
        assert hole_depth > 0
    if hole_depth:
        # b1 is to punch a "hole" to make it easier to remove the magnet later
        if round_hole is None:
            b1 = W().box(m_w, m_w, hole_depth).align(b, ":>Z")
        else:
            if round_hole is True:
                r = m_w / 3
            else:
                r = round_hole / 2
            h1 = W().cylinder(hole_depth, r)
            b1 = h1.align(b, ":>Z")
        # asymmetrical - the shorter side should be installed first
        b1 = b1.translate((0, (int(c1b > c1a) - 0.5) * (m_t - m_w) / 4, 0))
        obj = obj.union(b1)
    return obj


magnet_2_5_10 = magnet2510 = partial(_magnet, m_w=5.0, m_h=2.2, m_t=10.1)
magnet2510.__doc__ = """slot for magnet: 10 x 5 x 2mm (useful for cut)"""

# actual: 1.7mm x 9.0mm x 19mm
# not yet verified
magnet_2_10_20 = magnet21020 = partial(
    _magnet, m_w=9.4, m_h=2.0, m_t=19.2, c1a=0.6, c1b=2.0, round_hole=True
)
magnet2510.__doc__ = """slot for magnet: 20 x 10 x 2mm (useful for cut)"""

magnet_3_10_60 = magnet31060 = partial(
    _magnet, m_w=9.9, m_h=3.1, m_t=59.3, c1b=3.0, c1a=0.8
)
magnet31060.__doc__ = """slot for magnet: 60 x 10 x 3mm (useful for cut)"""


if __name__ == "__cq_main__":
    result = W()
    for i, c1b in enumerate([0.4, 0.6, 0.8, 1.0]):
        obj = magnet2510(c1b=c1b)
        bbox = obj.bbox()
        b2 = W().box(bbox.xlen + 3, bbox.ylen + 3, bbox.zlen)
        b2 = b2.cut(obj.align(b2, "<Z"))
        result = result.translate((-10, 0, 0)).union(b2)
    result.show().export()
