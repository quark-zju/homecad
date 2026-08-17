import math

from b4dcad import conic, cube, cylinder


def get_holder():
    """Alternative holder for https://www.thingiverse.com/thing:3474150"""
    d = 70
    h = 125
    thick = 6
    c1 = conic(h=h + thick, d1=d + thick * 2, d2=d + thick * 4)
    c2 = conic(h=h, d1=d, d2=d + thick * 2).align_to(c1, ">Z")

    c1a = cylinder(h=h + thick, d=d + thick * 2)
    c2a = cylinder(h=h, d=d).align_to(c1, ">Z")

    c3 = cylinder(thick, d / 1.7).align_to(c1, "<Z")
    c4 = conic(h=thick * 3, d1=d + thick * 4, d2=d + thick * 2)

    slot = 23

    def warp(p):
        x, y, z = p
        if x > 0 and z > 0:
            z -= slot
        elif x <= 0 and z <= 0:
            z += slot
        return (x, y, z)

    b1 = (
        cube(x=slot, y=d + thick * 2, z=h - thick * 5)
        .warp(warp)
        .align_to(c4, ":>Z -X -Y", dy=thick * 2)
    )
    b1a = cube(x=slot, y=d + thick * 2, z=h+slot).warp(warp).align_to(c4, ":>Z -X -Y", dy=thick * 2)

    bs = b1
    bsa = b1a
    for angle in range(0, 360, 60):
        bs = bs + b1.rotate(z=angle)
        bsa = bsa + b1a.rotate(z=angle)

    o1 = c1 + c4 - c2 - bs
    o2 = c1a - c2a - bsa
    obj = o1 + o2 - c3
    return obj


holder = get_holder()
