"""Frame for display

For [Waveshare's 13.3 inch E6 color display](https://www.waveshare.com/13.3inch-e-paper-hat-plus-e.htm).

There are a bunch of E6 color displays in the market in 2025. However, they either have a worse form factory (large padding area around the picture, smaller display), or use a restricted software stack.

I use a Raspberry Pi Zero 2W, with [PiSugar 3](https://www.amazon.com/dp/B0FB3N1YSK) for scheduled power-on. ESP32-WROVER can also be a decent choice.

The waveshare's example dithering algorithm might produce suboptimal color accuracy. I [updated the script](https://gist.github.com/quark-zju/e488eb206ba66925dc23692170ba49f9) to produce more accurate colors.
"""

import math
from cqutils import *


def render():
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
    support2 = back_support_obj(True)
    support2 = align(support2, main_frame, "<Z <X :>Y", dy=20)
    objs += [support2]

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
obj.quick_export()
show_object(obj)
