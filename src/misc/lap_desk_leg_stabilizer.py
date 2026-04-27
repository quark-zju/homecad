from cqutils import W, trapezoid, union_all

# Stablizer for "Collapsible Lap Desk Brown - Threshold™"
# https://www.target.com/p/collapsible-lap-desk-brown-threshold-8482/-/A-83901213

bar_width = 20.2
bar_thick = 3.1

l1 = 45
l2 = 30  # length for the round corner
l3 = 12
pad = 2

rd = 8.7
# r + rd == sqrt(2) * r
r = 2.414 * rd


def render():
    b1 = W().box(bar_width + pad * 2.4, l1, pad)
    b2 = W().box(pad * 1.2, l1, bar_thick + pad)
    t1 = trapezoid(0, pad, l1, dx2=0).rotate_axis("X", 90).align(b2, ">Z >Y >X")
    b2c = b2.cut(t1)
    b2l = b2c.align(b1, "<X :>Z")
    b2r = b2c.rotate_axis("Z", 180).align(b1, ">X :>Z")
    o1 = union_all([b1, b2l, b2r])

    b3 = W().box(bar_width, l2, pad).align(b1, ":<Y")
    t2 = (
        trapezoid(0, l2 + l3, bar_width, dx2=0, degree=30)
        .rotate_axis("X", 90)
        .rotate_axis("Z", 90)
        .align(b3, "<X <Z :<Y")
        .edges("not >Y")
        .edges("not <Z")
        .fillet(1)
    )
    t2c1 = trapezoid(0, pad, l3 + pad * 2, dx2=0)
    t2cr = t2c1.align(t2, ">X >Y >Z")
    t2cl = t2cr.rotate_axis("Y", 180).align(t2, "<X >Y >Z")
    t2 = t2.cut(t2cr).cut(t2cl)

    b4 = W().box(bar_width + pad * 2, pad, l3)
    b4l = W().box(pad, bar_thick + pad, l3).align(b4, "<X :<Y")
    b4r = b4l.align(b4, ">X")
    t4 = trapezoid(0, pad, l3, dx2=0)
    t4r = t4.align(b4r, ":<X >Z <Y")
    t4l = t4.rotate_axis("Y", 180).align(b4l, ":>X >Z <Y")
    o4 = union_all([b4, b4l, b4r, t4r, t4l])

    o4.export("vertical-cap", print_from_face=">Y")
    o4 = o4.align(t2, ">Z >Y", dy=pad + bar_thick)

    c1 = (
        W()
        .cylinder(bar_width, r, angle=90)
        .rotate_axis("Y", 90)
        .rotate_axis("Z", 180)
        .align(b3, ":>Z <Y")
    )
    cv = c1.solid_box(inverse=True)
    o2 = union_all([o1, b3, t2, cv])
    o2.export("corner")

    b10 = W().box(bar_width + pad * 2.4, l1, t1.measure("Z")).align(b2l, "<X <Y >Z")
    o3 = b10.cut(o1).cut(o1.align(dx=-0.1))
    o3.export("cap")

    return union_all([o2, o3.align(dy=10), o4.align(dz=5)])


render().show()
