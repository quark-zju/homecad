"""
Snap-on two-plate mounting system for Command Refill Strips

** Plates to the left (thinner) **

The back plate (the thiner one) is meant to be attached to a wall using [3M Command Refill Strips](https://www.amazon.com/dp/B073XR4X72).

The front plate (the thicker one) can be attached to objects that need to be mounted.

The two plates snap together to hold the object in place. When removal is needed, the front plate can be detached easily, exposing the pull tab of the Command strip.

** Plates to the right (thicker) **

This is a variant to support rotation. It's useful to be embedded in a photo frame so it can rotate 90 degree. 2x5x10mm magnet holes are reserved to lock the designed rotation locations.
"""

from cqutils import *
from magnet import magnet2510
import math


# 4 medium-sized strips; modify as needed
WIDTH = 63 - 0.2 - 0.3
HEIGHT = 46
ROUND = 7
THICK = 2

SEAM = 0.16
SEAM_THICK = 0.06


def flat_plate(index=None, thick=THICK, extra_thick=THICK, round=ROUND, out=None):
    objs = []
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_plate(w, h, thick_d=0):
        return (
            W()
            .box(w, h, thick + thick_d)
            .faces(">Y")
            .edges("Z")
            .fillet(round)
            .edges(">Z")
            .filter(lambda edge: edge.Center().y > -5)
            .chamfer(d, d2)
        )

    w, h = WIDTH + d2 * 2, HEIGHT + d2 * 2
    if out is not None:
        out = out.update({"d2": d2, "d": d, "w": w, "h": h})

    plate = get_plate(w, h)
    plate.export("flat-male")
    if index == 0:
        return plate
    objs += [plate]

    edge = 4
    plate2 = W().box(WIDTH + edge * 2, HEIGHT + edge, thick + extra_thick)
    plate2 = align(plate2, plate, ">Z <Y")
    plate2 = plate2.cut(get_plate(w + SEAM * 2, h + SEAM, SEAM_THICK))
    plate2 = align(plate2, plate, "<Z")
    if index == 1:
        return plate2

    plate2.export("flat-female")
    objs += [plate2.align(plate, ">Z", dy=12)]
    obj = union_all(objs)
    return obj


CIRCLE_R = 20
CIRCLE_THICK = 2.8
CIRCLE_ROUND = 7


def circle_plate():
    d = CIRCLE_THICK - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_magnet_box():
        return magnet2510()

    def get_circle_male(
        r,
        thick_d=0,
        box_top_right=True,
        magnet_holes=True,
        cut_height=0,
    ):
        obj = circle = W().cylinder(CIRCLE_THICK + thick_d, r)
        if box_top_right:
            box = W().box(r, r, CIRCLE_THICK + thick_d).align(circle, ">X >Y")
            obj = circle.union(box)
        obj = obj.faces(">Z").chamfer(d, d2)
        if cut_height:
            box1c = (
                W()
                .box(r * 2, r + cut_height, CIRCLE_THICK + thick_d)
                .align(circle, "<X <Y", dy=r)
            )
            box1c = box1c.faces(">Z").edges("|Y").chamfer(d, d2)
            obj = obj.union(box1c)
        if magnet_holes:
            m1 = get_magnet_box().align(obj, ">Y <Z", dy=-d)
            m2 = m1.rotate_axis("Z", -90)
            m3 = m2.rotate_axis("Z", -90)
            m4 = m3.rotate_axis("Z", -90)
            obj = obj.cut(m1).cut(m2).cut(m3).cut(m4)
        return obj

    male = get_circle_male(CIRCLE_R)
    male.export("rotate90-male")
    # show_object(male)

    def get_circle_female():
        b_out = {}
        b = flat_plate(
            index=0, thick=CIRCLE_THICK * 2, round=CIRCLE_ROUND, out=b_out
        ).rotate_axis("Y", 180)
        obj = b
        c = get_circle_male(
            r=CIRCLE_R + SEAM,
            thick_d=SEAM_THICK,
            box_top_right=False,
            magnet_holes=False,
            cut_height=b_out["h"] / 2 - CIRCLE_R - SEAM_THICK,
        ).align(b, ">Y >Z")
        c_ref = get_circle_male(
            r=CIRCLE_R,
            box_top_right=False,
            magnet_holes=False,
        ).align(b, ">Z")
        obj = obj.cut(c)
        m1 = (
            get_magnet_box()
            .rotate_axis("Y", 180)
            .align(c_ref, ">Y", dy=-d)
            .align(obj, "<Z")
        )
        m2 = m1.rotate_axis("Z", -90)
        m3 = m2.rotate_axis("Z", -90)
        m4 = m3.rotate_axis("Z", -90)
        obj = obj.cut(m1).cut(m2).cut(m3).cut(m4)
        return obj

    female = get_circle_female().align(male, "<Z")
    female.export("rotate90-female")
    obj = female.union(male.align(female, ">Z").translate((0, 20, 0)))
    return obj


def render():
    flat = flat_plate()
    circle = circle_plate()
    obj = flat.union(circle.align(flat, ":>X <Z <Y").translate((5, 0, 0)))
    return obj


obj = render()
show_object(obj)
