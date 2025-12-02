"""
Stand for pens

This is a stand for the [Panda Wiggle Gel Pens](https://www.hitchcockpaper.com/products/panda-wiggle-gel-pen). It holds the bamboo upright for a more realistic look.
"""

from cqutils import *


W = cq.Workplane()


def render():
    # matches pico plate
    R1 = 11.4 / 2
    R2 = 11.4 / 2
    H = 20.0
    thick = 4.0
    pad = 10
    inner_pad = 14
    b1_w = R1 * 2 * 2 + pad * 2 + inner_pad
    b1_h = R1 * 2 + pad * 2
    round_edge = thick
    b1 = W.box(b1_w, b1_h, H, centered=False).fillet(round_edge)
    c_cut = (
        W.cylinder(H, R1, centered=False)
        .center(R1 + R2 + inner_pad, 0)
        .cylinder(H, R2, centered=False)
    ).translate((pad, pad, 0))
    b2 = (
        W.box(b1_w + thick * 2, b1_h + thick * 2, thick, centered=False)
        .translate(
            (
                -thick,
                -thick,
            )
        )
        .edges("|Z")
        .fillet(round_edge)
    )
    # b3 = (
    #    W.box(b1_w + thick * 4, b1_h + thick * 4, thick, centered=False)
    #    .translate((-thick * 2, -thick * 2, -thick))
    #    .edges("|Z")
    #    .fillet(round_edge)
    # )
    return union_all([b1.cut(c_cut), b2])


render().export().show()
