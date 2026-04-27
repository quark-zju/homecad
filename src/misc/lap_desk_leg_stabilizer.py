from cqutils import W, trapezoid, union_all

# Stablizer for "Collapsible Lap Desk Brown - Threshold™"
# https://www.target.com/p/collapsible-lap-desk-brown-threshold-8482/-/A-83901213

bar_width = 20.2
bar_thick = 3.1

l1 = 45
l2 = 30  # length for the round corner
pad = 2


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
        trapezoid(0, l2 + 10, bar_width, dx2=0)
        .rotate_axis("X", 90)
        .rotate_axis("Z", 90)
        .align(b3, "<X <Z :<Y")
        .edges("not >Y")
        .edges("not <Z")
        .fillet(1)
    )

    o2 = union_all([o1, b3, t2])
    o2.export("corner")

    b10 = W().box(bar_width + pad * 2.4, l1, t1.measure("Z")).align(b2l, "<X <Y >Z")
    o3 = b10.cut(o1).cut(o1.align(dx=-0.1))
    o3.export("cap")

    return union_all([o2, o3.align(dy=10)])


render().show().export()


class K(W):
    pass


g = K()
b = g.box(1, 1, 1)
