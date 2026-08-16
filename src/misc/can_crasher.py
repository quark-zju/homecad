import math

from b4dcad import conic, cube, cylinder


def get_holder():
    """Alternative holder for https://www.thingiverse.com/thing:3474150"""
    d = 72
    h = 125
    thick = 6
    c1 = cylinder(h + thick, d + thick * 2)
    c2 = cylinder(h, d).align_to(c1, ">Z")
    c3 = cylinder(thick, d / 1.7).align_to(c1, "<Z")
    c4 = conic(h=thick * 2, d1=d + thick * 3, d2=d + thick * 2)

    slot = 20

    def warp(p):
        x, y, z = p
        if x > 0 and z > 0:
            z -= slot / 2
        elif x <= 0 and z <= 0:
            z += slot / 2
        return (x, y, z)

    b1 = (
        cube(x=20, y=d + thick * 2, z=h - thick * 3)
        .warp(warp)
        .align_to(c4, ":>Z -X -Y", dy=thick*2)
    )
    bs = b1
    for angle in range(0, 360, 60):
        bs = bs + b1.rotate(z=angle)

    o1 = c1 + c4 - c2 - c3 - bs
    obj = o1
    return obj


holder = get_holder()
