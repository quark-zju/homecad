from cqutils import W, trapezoid, union_all

# Stablizer for "Collapsible Lap Desk Brown - Threshold™"
# https://www.target.com/p/collapsible-lap-desk-brown-threshold-8482/-/A-83901213

bar_width = 20.2
bar_thick = 3.1

l1 = 45  # bottom cover length
l2 = 30  # length for the round corner
l3 = 30  # top cover length
pad = 2

rd = 8.7
# r + rd == sqrt(2) * r
r = 2.414 * rd - 1


def render():
    b1 = W().box(bar_width + pad * 2.4, l1, pad)
    b2 = W().box(pad * 1.2, l1, bar_thick + pad)
    t1 = trapezoid(0, pad, l1, dx2=0).rotate_axis("X", 90).align(b2, ">Z >Y >X")
    b2c = b2.cut(t1)
    b2l = b2c.align(b1, "<X :>Z")
    b2r = b2c.rotate_axis("Z", 180).align(b1, ">X :>Z")
    o1 = union_all([b1, b2l, b2r])

    b2ls = b2.align(b1, "<X :>Z")
    b2rs = b2ls.align(b1, ">X :>Z")
    o1s = union_all([b1, b2ls, b2rs])

    b3 = W().box(bar_width + pad * 2.4, l2, pad).align(b1, ":<Y")
    t2h = r + pad + l3
    t2 = (
        trapezoid(0, t2h, bar_width + pad * 2.4, dx2=0, degree=30)
        .rotate_axis("X", 90)
        .rotate_axis("Z", 90)
        .align(b3, "-X <Z :<Y")
        .edges("not >Y")
        .edges("not <Z")
        .fillet(1)
    )
    # t2c1 = trapezoid(0, pad, l3 + pad * 2, dx2=0)
    # t2cr = t2c1.align(t2, ">X >Y >Z")
    # t2cl = t2cr.rotate_axis("Y", 180).align(t2, "<X >Y >Z")
    o1r = o1.rotate_axis("X", -90).align(t2, ">Z >Y", dy=pad + bar_thick)
    o1rs = o1s.rotate_axis("X", -90).align(t2, "<Z >Y", dy=pad + bar_thick)
    o1rs = o1rs.cut(o1rs.align(dz=r + pad))
    t2 = t2.union(o1r).union(o1rs)

    c1 = (
        W()
        .cylinder(bar_width + pad * 2.4, r, angle=90)
        .rotate_axis("Y", 90)
        .rotate_axis("Z", 180)
        .align(b3, ":>Z <Y")
    )
    cv = c1.solid_box(inverse=True)
    o2 = union_all([o1, b3, t2, cv])
    o2.export("corner")

    b10 = W().box(bar_width + pad * 2.4, l1, t1.measure("Z")).align(b2l, "<X <Y >Z")
    o3 = b10.cut(o1).cut(o1.align(dx=-0.1))
    o3.export("cap1")

    o4 = o3.rotate_axis("X", -90).align(o1r, ">Z >Y")
    o4 = o4.cut(o4.align(dz=-l3))
    o4.export("cap2", print_from_face="<Y")

    return union_all([o2, o3.align(dy=10), o4.align(dz=10)])


render().show()
