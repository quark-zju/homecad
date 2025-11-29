"""Frame for e-ink display

For [Waveshare's 13.3 inch E6 color display](https://www.waveshare.com/13.3inch-e-paper-hat-plus-e.htm).

There are a bunch of E6 color displays in the market in 2025. However, they either have a worse form factory (large padding area around the picture, smaller display), or use a restricted software stack.

I use a Raspberry Pi Zero 2W, with [PiSugar 3](https://www.amazon.com/dp/B0FB3N1YSK) for scheduled power-on. ESP32-WROVER can also be a decent choice.

The waveshare's example dithering algorithm might produce suboptimal color accuracy. I [updated the script](https://gist.github.com/quark-zju/e488eb206ba66925dc23692170ba49f9) to produce more accurate colors.
"""

import math
from cqutils import *
from functools import partial


def render(demo_sep=10):
    display_width = 211
    display_height = 287
    front_border_width = 4
    front_border_top = 4
    front_border_bottom = 13
    surface_thickness = 2
    front_thickness = 1
    whole_thickness = 13 + front_thickness
    bottom_cable_height = 4

    orig_obj = render_one_piece()
    objs = []
    objs += [orig_obj.translate((0, 30, 0))]
    connect = partial(connect_obj, 6.4, 18, 2.4, edge=2.6)

    bottom_plate_height = (
        bottom_cable_height + front_border_bottom + surface_thickness * 2
    )

    def get_bottom_obj():
        bar = (
            W()
            .box(display_width, whole_thickness, surface_thickness)
            .align(orig_obj, "<Z")
        )
        corner1 = W().box(10, whole_thickness, bottom_cable_height).align(bar, ":>Z <X")
        corner2 = corner1.align(bar, ">X")
        obj = bar.union(corner1).union(corner2)
        connect_left = connect(kind=0).rotate_axis("Z", 270).align(bar, "<X >Y <Z")
        connect_left_cut = connect(kind=2).rotate_axis("Z", 270).align(bar, "<X >Y <Z")
        obj = obj.union(connect_left).cut(connect_left_cut)
        connect_right = connect(kind=0).rotate_axis("Z", 90).align(bar, ">X >Y <Z")
        connect_right_cut = connect(kind=2).rotate_axis("Z", 90).align(bar, ">X >Y <Z")
        obj = obj.union(connect_right).cut(connect_right_cut)
        plate = W().box(display_width, front_thickness, bottom_plate_height)
        obj = obj.union(plate.align(bar, "<Y <Z")).union(plate.align(bar, ">Y <Z"))
        cut_front = W().box(
            front_border_width, front_thickness + 0.2, bottom_plate_height
        )
        obj = obj.cut(cut_front.align(bar, "<Z <X <Y"))
        obj = obj.cut(cut_front.align(bar, "<Z >X <Y"))
        return obj

    bottom = get_bottom_obj()
    objs += [bottom]

    def get_side_obj(left=True):
        whole_height = display_height + bottom_cable_height + surface_thickness * 3

        def sign(left_dir):
            if left:
                return left_dir
            elif left_dir == "<":
                return ">"
            else:
                return "<"

        def angle(left_val):
            if left:
                return left_val
            else:
                return 360 - left_val

        bar = (
            W()
            .box(surface_thickness, whole_thickness, whole_height)
            .align(orig_obj, f"<Z {sign('<')}X")
        )
        obj = bar
        conn = (
            connect(kind=1)
            .rotate_axis("Z", angle(270))
            .align(bar, f"<Z :{sign('>')}X >Y")
        )
        obj = obj.union(conn)
        obj = obj.union(conn.align(bar, ">Z"))
        for z in [0.25, 0.5, 0.75]:
            obj = obj.union(
                conn.translate((0, 0, (whole_height - conn.measure("Z")) * z))
            )
        plate = (
            W()
            .box(front_border_width, front_thickness, whole_height)
            .align(bar, f"<Y :{sign('>')}X >Z")
        )
        obj = obj.union(plate)
        return obj

    left = get_side_obj()
    right = get_side_obj(False)
    left_r = left.rotate_axis("Y", -90).align(bottom, "<Z", dy=-20)
    right_r = right.rotate_axis("Y", 90).align(left_r, "<Z <X <Y", dy=-20)
    sides = left_r.union(right_r)
    sides.quick_export("sides")
    objs += [
        left.translate((-demo_sep, 0, 0)),
        right.translate((demo_sep, 0, 0)),
    ]

    def get_top_obj():
        bar = (
            W()
            .box(display_width, whole_thickness, surface_thickness)
            .align(orig_obj, "<Z")
        )
        obj = bar
        connect_left = connect(kind=0).rotate_axis("Z", 270).align(bar, "<X >Y >Z")
        connect_left_cut = connect(kind=2).rotate_axis("Z", 270).align(bar, "<X >Y >Z")
        obj = obj.union(connect_left).cut(connect_left_cut)
        connect_right = connect(kind=0).rotate_axis("Z", 90).align(bar, ">X >Y >Z")
        connect_right_cut = connect(kind=2).rotate_axis("Z", 90).align(bar, ">X >Y >Z")
        obj = obj.union(connect_right).cut(connect_right_cut)
        plate = (
            W()
            .box(
                display_width,
                front_thickness,
                front_border_top,
            )
            .align(bar, "<Y :<Z")
        )
        obj = obj.union(plate)
        cut_front = (
            W()
            .box(front_border_width, front_thickness + 0.2, obj.measure("Y"))
            .align(obj, "<Y <X >Z")
        )
        obj = obj.cut(cut_front)
        obj = obj.cut(cut_front.align(obj, ">X"))

        return obj

    top = get_top_obj().align(orig_obj, ">Z >Y")
    objs += [top.translate((0, 0, 0))]

    top_r = top.rotate_axis("X", 180)
    top_bottom = bottom.union(
        top_r.align(bottom, "<Z").translate((0, bottom.measure("Y") + 10, 0))
    )
    top_bottom.quick_export("top-bottom")

    return union_all(objs)


def render_one_piece():
    display_width = 211
    display_height = 287
    front_border_width = 4
    front_border_top = 4
    front_border_bottom = 13
    surface_thickness = 2
    front_thickness = 1
    whole_thickness = 13 + front_thickness
    bottom_cable_height = 4

    # main box
    box_outer = W().box(
        display_width + surface_thickness * 2,
        whole_thickness,
        display_height + surface_thickness * 2,
    )
    box_inner = W().box(
        display_width,
        whole_thickness - front_thickness,
        display_height,
    )
    box_inner = box_inner.align(box_outer, ">Y")
    box_surface_inner = W().box(
        display_width - front_border_width * 2,
        front_thickness,
        display_height - front_border_top - front_border_bottom,
    )
    box_surface_inner = box_surface_inner.align(box_outer, "<Y >Z").translate(
        (0, 0, -front_border_top - surface_thickness)
    )

    # bottom box for line wrapping
    box_bottom = W().box(
        display_width + surface_thickness * 2,
        whole_thickness,
        bottom_cable_height + surface_thickness,
    )
    box_bottom = box_bottom.align(box_outer, ":<Z")
    box_bottom_cut = W().box(
        display_width - 40,
        whole_thickness - front_thickness,
        bottom_cable_height + surface_thickness,
    )
    box_bottom_cut = align(box_bottom_cut, box_bottom, "<Z >Y", dz=surface_thickness)

    # so far...
    main_frame = (
        box_outer.cut(box_inner)
        .cut(box_surface_inner)
        .union(box_bottom)
        .cut(box_bottom_cut)
    )

    # bottom back
    box_bottom_back = W().box(
        display_width,
        front_thickness,
        bottom_cable_height + front_border_bottom,
    )

    box_bottom_back = align(box_bottom_back, main_frame, ">Y <Z", dz=surface_thickness)

    # middle back (mount to command strip)
    def back_before_cut(obj):
        belt = W().box(display_width, 10, 4)
        belt = align(belt, obj, ">Z <Y")
        belt2 = align(belt, obj, ">Z >Y")
        return obj.union(belt).union(belt2)

    back_support = back_support_obj(before_cut_process_obj=back_before_cut)
    back_support = rotate_axis(rotate_axis(back_support, "X", 90), "Z", 180)

    command_strip_thickness = 1
    back_support = align(back_support, main_frame, ">Y", dy=-command_strip_thickness)

    objs = [main_frame, box_bottom_back, back_support]

    # the other part of the support
    # support2 = back_support_obj(True)
    # support2 = align(support2, main_frame, "<Z <X :>Y", dy=20)
    # objs += [support2]

    return union_all(objs)


def back_support_obj(male=False, before_cut_process_obj=None):
    WIDTH = 63
    HEIGHT = 46
    THICK = 2

    d = THICK - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_plate(w, h):
        return (
            W()
            .box(WIDTH + d2 * 2, HEIGHT + d2, THICK)
            .edges(">Z")
            .filter(lambda edge: edge.Center().y > -5)
            .chamfer(d, d2)
        )

    w, h = WIDTH + d2 * 2, HEIGHT + d2 * 2
    plate = get_plate(w, h)
    if male:
        return plate

    edge = 4
    plate2 = W().box(WIDTH + edge * 2, HEIGHT + edge, THICK * 2)
    plate2 = align(plate2, plate, ">Z <Y")
    if before_cut_process_obj:
        plate2 = before_cut_process_obj(plate2)
    plate2 = plate2.cut(get_plate(w + 0.4, h + 0.4))
    plate2 = align(plate2, plate, "<Z")
    return plate2


obj = render()
show_object(obj)
