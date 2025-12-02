"""
Hair dryer holder

Similar to[mixicz's "Dyson supersonic hair dryer wall holder"](https://www.thingiverse.com/thing:2805650), but designed to attach to [the Command Strip mounting plate I designed](https://github.com/quark-zju/homecad/blob/master/src/command_strip_plate.py).

The size is measured to match a Laifen Swift. If you need a different size, just edit the variables.
"""

from cqutils import *


def render():
    r1 = 68 / 2
    r2 = 48 / 2
    w1 = r2 * 2 + 20 * 2
    plate = (
        import_part("command_strip_plate.py", "flat-female")
        .rotate_axis("X", 90)
        .rotate_axis("Z", 180)
    )
    g1 = plate.surface_grow("<Z", 20)
    g2 = plate.surface_grow(">Z", 6).edges("|Y and >Z").fillet(5)
    big_plate = plate.union(g1).union(g2)
    obj = big_plate
    py = plate.measure("Y")
    b1 = W().box(w1, r1 * 1.8, r1 + py).align(big_plate, "<Z >Y")
    b1 = b1.cut(big_plate.solid_box(inverse=True))
    pad_z = 10
    c1 = W().cylinder(w1, r1).rotate_axis("Y", 90).align(b1, "<Z >Y", dy=-py, dz=pad_z)
    b1r = b1.edges("Y and >Z").fillet(5)
    b1c = b1.cut(c1)
    c2 = W().cylinder(b1.measure("Z"), r2).align(b1, ">Y <Z", dy=r2 - r1)
    b1c = b1c.cut(c2)
    b2 = W().box(r2 * 2, r2 * 2, b1.measure("Z")).align(c2, ">Z >Y", dy=-r2)
    b1c = b1c.cut(b2)
    b1c = b1c.faces("<Y").fillet(5)
    b1c = b1c.intersect(b1r)
    obj = obj.union(b1c)
    return obj


render().show().export()
