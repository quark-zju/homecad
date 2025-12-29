from cqutils import *


def finger_phone_holder(
    r1,  # ring
    r2,  # pinky
    phone_height,
    phone_thick,
    thick=2.4,
    bottom_thick=3,
    width=10,
    hook_height=4.6,
):
    eps = 1e-5
    fillet_width = (thick - 0.1) / 2

    def get_ring(r):
        ca = W().cylinder(width, r + thick)
        cb = W().cylinder(width, r)
        c = ca.cut(cb)
        return c

    def inner_ring_fillet(obj, rs=[r1, r2]):
        return (
            obj.edges("%CIRCLE")
            .filter(lambda e: any(abs(e.radius() - r) <= eps for r in rs))
            .fillet(fillet_width)
        )

    c1 = get_ring(r1)
    c2 = get_ring(r2).align(c1, ">X :<Y", dy=thick)
    cs = c1.union(c2)
    obj = cs
    b1_dy = r1 + thick
    b1_height = phone_height / 2 - r1 * 2  # skip a finger
    b1 = W().box(thick, b1_height - b1_dy, width)
    b1 = b1.align(c1, ">X >Y", dy=-b1_dy)
    b1 = b1.edges("|Z and <X and <Y").fillet(fillet_width)
    obj = obj.union(b1)
    obj = inner_ring_fillet(obj)
    b2 = W().box(phone_thick, bottom_thick, width).align(b1, "<Y :>X")
    b3 = W().box(thick, hook_height + thick, width).align(b2, ":>X <Y")
    b3 = b3.edges("|Z and >X").fillet(thick - 0.1)
    obj = obj.union(b2).union(b3)
    return obj


def render():
    return finger_phone_holder(r1=22 / 2, r2=20 / 2, phone_height=166, phone_thick=8.6)


render().show().export()
