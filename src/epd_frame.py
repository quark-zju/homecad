"""Frame for e-ink display

For [Waveshare's 13.3 inch E6 color display](https://www.waveshare.com/13.3inch-e-paper-hat-plus-e.htm).

There are a bunch of E6 color displays in the market in 2025. However, they either have a worse form factory (large padding area around the picture, smaller display), or use a restricted software stack.

I use a Raspberry Pi Zero 2W, with [PiSugar 3](https://www.amazon.com/dp/B0FB3N1YSK) for scheduled power-on. ESP32-WROVER can also be a decent choice.

The waveshare's example dithering algorithm might produce suboptimal color accuracy. I [updated the script](https://gist.github.com/quark-zju/e488eb206ba66925dc23692170ba49f9) to produce more accurate colors.

The frame size exceeds the build plate I use. Initially, I made a one-piece frame that can print vertically. It requires lots of support and took 7h to print, and the `|Z` lines turned non-straight.

The current version uses multiple parts that fit the build plate to print horizontally, and supports rotation.
"""

import math
from functools import partial

from cqutils import W, connect_obj, import_part, sector, union_all
from magnet import magnet_2_10_20


def rotation_mounting_plate_10cm():
    # 4 medium-sized strips; modify as needed
    WIDTH = 63 - 0.2 - 0.3
    WIDTH1 = WIDTH / 4
    HEIGHT = 46

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

    R1 = 60 / 2
    border = 40

    def plate_female():
        m1 = magnet_2_10_20(hole_depth=0.4).rotate_axis("X", -90)
        thick = m1.measure("Y")

        b1 = W().box(WIDTH, thick, HEIGHT)
        b1 = b1.translate((0, 0, -15))
        u1 = u_shape(R1, thick)

        bu = (
            W()
            .box(R1 * 2 + border, thick * 2, R1 * 2 + border)
            .align(u1, ">Y")
            .edges("|Y and >Z")
            .fillet(border / 2)
        )
        obj = bu

        b2 = W().box(WIDTH1, thick * 2, 100).align(u1, ">Y", dz=-10)
        b2a = b2.align(b1, "<X", dx=WIDTH1 / 2)
        b2b = b2.align(b1, ">X", dx=-WIDTH1 / 2)
        b2c = b2a.union(b2b).cut(b1.align(b2, "<Y"))
        obj = obj.cut(b2c).union(b1)

        u2 = u_shape(R1 + 0.2, thick, chamfer=True).align(bu, "<Y")
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
        # shorter side install first
        m1 = magnet_2_10_20(hole_depth=0.4).rotate_axis(
            "X", 90
        )  # .rotate_axis("Z", 180)
        m1 = m1.rotate_axis("Y", 180)
        thick = m1.measure("Y")

        u1 = u_shape(R1, thick, chamfer=True, top_right=True)
        obj = u1

        reel_w = 3.3
        reel_w1 = 3.1
        reel_l = 14.4 + 1

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
            .box(35 + reel_l - 14, reel_w1, reel_w + 7)
            .align(u1, ":>X", dx=border / 2 - 22)
            .align(obj, "<Y")
            .faces(">X")
            .workplane(centerOption="CenterOfBoundBox")
            .hole(1.4)
        )
        m1x_dz = math.sqrt(2) * (100 - 20) / 2 - m_edge
        b_reelx = b_reel.align(u1, ":<Y -X -Z", dx=m1x_dz)
        b_wire_hole = (
            W().box(20, 2.2, 1.4).align(obj, "<Y :>X", dx=-6.5).faces(">Y").fillet(0.6)
        )
        for angle in [90, 45]:
            obj = obj.union(b2.rotate_axis("Y", angle))
            obj = obj.cut(b_reelx.rotate_axis("Y", angle))
        for angle in [90, 75, 60, 45]:
            obj = obj.cut(b_wire_hole.rotate_axis("Y", angle))
        u3 = u_shape(R1 + 2, 1.4, top_right=True).align(u2, "<Y")
        obj = obj.cut(u3.cut(u2))
        c1 = W().cylinder(obj.measure("Y"), 2).rotate_axis("X", 90).align(obj, "<Y")
        obj = obj.cut(c1)
        return obj

    return {
        "female": plate_female,
        "male": plate_male,
    }


MOUNTING_PLATE = rotation_mounting_plate_10cm()


# @cq_cache
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

    # orig_obj = render_one_piece()
    orig_obj = W().box(215, 14, 297)

    objs = []
    # objs += [orig_obj.translate((0, 30, 0))]
    connect = partial(connect_obj, 6.4, 18, 2.4, edge_outline=2.6)

    bottom_plate_height = (
        bottom_cable_height + front_border_bottom + surface_thickness * 2
    )

    # @cq_cache
    def get_bottom_obj():
        bar = (
            W()
            .box(display_width, whole_thickness, surface_thickness)
            .align(orig_obj, "<Z")
        )
        # fix: corner not high enough
        corner1 = (
            W().box(10, whole_thickness, bottom_cable_height + 3).align(bar, ":>Z <X")
        )
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
    left_conn_objs = []

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
        conn_top = conn.align(bar, ">Z")
        obj = obj.union(conn_top)
        if left:
            left_conn_objs.append(conn)
        for z in [0.25, 0.5, 0.75]:
            conn_next = conn.translate((0, 0, (whole_height - conn.measure("Z")) * z))
            obj = obj.union(conn_next)
            if left:
                left_conn_objs.append(conn_next)
        if left:
            left_conn_objs.append(conn_top)
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
    sides.export("sides")
    objs += [
        left.translate((-demo_sep, 0, 0)),
        right.translate((demo_sep, 0, 0)),
    ]

    # @cq_cache
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
    top_r.export("top-bar")
    bottom.export("bottom-bar")
    # top_bottom = bottom.union(
    #     top_r.align(bottom, "<Z").translate((0, bottom.measure("Y") + 10, 0))
    # )
    # top_bottom.export("top-bottom")

    def get_rotate90_obj():
        # r90 = import_part("command_strip_plate.py", "rotate90-male")
        r90 = MOUNTING_PLATE["male"]()
        r90_outer = MOUNTING_PLATE["female"]()
        thick = r90_outer.measure("Y") / 2
        conn = connect(kind=0).rotate_axis("Z", 270).rotate_axis("X", 180)
        conn2 = connect(kind=2).rotate_axis("Z", 270).rotate_axis("X", 180)
        bar = (
            W()
            .box(display_width, conn.measure("Y"), conn.measure("Z"))
            .align(left_conn_objs[2], "<Z")
        )
        r90 = r90.align(bar, ">Y", dy=-thick)
        obj = bar
        connect_left = conn.align(bar, "<X >Y >Z")
        connect_left_cut = conn2.align(bar, "<X >Y >Z")
        obj = obj.union(connect_left).cut(connect_left_cut)
        connect_right = conn.rotate_axis("Z", 180).align(bar, ">X >Y >Z")
        connect_right_cut = conn2.rotate_axis("Z", 180).align(bar, ">X >Y >Z")
        obj = obj.union(connect_right).cut(connect_right_cut)
        r = (
            (
                r90_outer.measure("X") ** 2
                + r90_outer.measure("Y") ** 2
                + r90_outer.measure("Z") ** 2
            )
            ** 0.5
            * 0.618
            * 1.1
        )
        cut_big_circle = (
            W("XZ")
            .cylinder(conn.measure("Y"), r)
            .align(r90, "<Y", dy=r90.measure("Y") - thick)
        )
        cut_magnet_holes = r90.surface_holes("<Y", len=50).translate((0, 20, 0))
        obj = obj.cut(cut_big_circle)
        obj = obj.cut(cut_magnet_holes)
        obj = obj.union(r90)
        # r90_extend = r90.surface_grow("<Y", length=r90.bbox().ymin - obj.bbox().ymin)
        # obj = obj.union(r90_extend) # hangs... bug in cadquery?
        return obj

    rotate90 = get_rotate90_obj()
    rotate90.rotate_axis("X", 90).export("middle-bar-with-rotate")
    objs += [rotate90]

    def get_support_bar(i=3):
        conn = connect(kind=0).rotate_axis("Z", 270)
        conn2 = connect(kind=2).rotate_axis("Z", 270)
        bar = (
            W()
            .box(display_width, conn.measure("Y"), conn.measure("Z"))
            .align(left_conn_objs[i], "<Z")
        )
        bar_cut = (
            W()
            .box(display_width - 20, conn.measure("Y") / 2, conn.measure("Z"))
            .align(bar, ">Y <Z")
        )
        obj = bar.cut(bar_cut)
        connect_left = conn.align(bar, "<X >Y >Z")
        connect_left_cut = conn2.align(bar, "<X >Y >Z")
        obj = obj.union(connect_left).cut(connect_left_cut)
        connect_right = conn.rotate_axis("Z", 180).align(bar, ">X >Y >Z")
        connect_right_cut = conn2.rotate_axis("Z", 180).align(bar, ">X >Y >Z")
        obj = obj.union(connect_right).cut(connect_right_cut)
        return obj

    bar1 = get_support_bar(1)
    bar2 = get_support_bar(3)
    bar2.export("middle-bar2", print_from_face=">Z")
    bar1c = bar1.solid_box(dx=-100, dy=-4.4)
    bar1 = bar1.cut(bar1c)
    bar1.export("middle-bar1", print_from_face=">Z")
    objs += [bar1, bar2]

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


render().show()
