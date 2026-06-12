from b4dcad import conic, cube, cylinder


def semicircular(r1, thick, thick_z=None, cut=True):
    thick_z = thick_z or thick
    c1 = cylinder(h=thick_z, r=r1)
    c2 = cylinder(h=thick_z, r=r1 + thick)
    obj = c2 - c1
    if cut:
        b1 = cube(r1 + thick, (r1 + thick) * 2, thick).align_to(c2, ">X >Y")
        obj -= b1
    return obj


def get_part1(
    r1=8.3 / 2,
    r2=9.8 / 2,
    thick=4.0,
    thick_z=2.0,
    c2_h=2.9,
    tall_len=200.0,
):
    c1 = semicircular(r1, thick, thick_z, cut=False)
    dx = r1 + thick - (((r1 + thick) ** 2 - (thick / 2) ** 2) ** 0.5)
    b3 = cube(tall_len, thick, thick_z).align_to(c1, ":>X -Y", dx=-dx * 1.1)
    c2 = cylinder(r=r2, h=c2_h + thick_z + 3).align_to(b3, "<Z -Y >X", dx=0.4)
    obj = c1 + b3 + c2
    return obj


def get_part2(r1=9.8 / 2, r2=16 / 2, h=2.5):
    c1 = conic(r1=r1, r2=r1 + 0.2, h=h)
    c2 = cylinder(r=r2, h=h)
    c3 = c2 - c1
    b1 = cube(r2 * 2, 1, 0.6).align_to(
        c3, ">Z -X -Y"
    )  # mark the top side (slightly loose)
    obj = c3 - b1
    return obj


part1 = get_part1()
part2 = get_part2()
