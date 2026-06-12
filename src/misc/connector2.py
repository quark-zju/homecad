from b4dcad import conic, cube, cylinder


def semicircular(r1, thick):
    c1 = cylinder(h=thick, r=r1)
    c2 = cylinder(h=thick, r=r1 + thick)
    b1 = cube(r1 + thick, (r1 + thick) * 2, thick).align_to(c2, ">X >Y")
    return c2 - c1 - b1


def get_obj(r1=6.1 / 2, r2=9.8 / 2, thick=5.0, hook_len=40.0, tall_len=210.0):
    c1 = semicircular(r1, thick)
    b2 = cube(hook_len, thick, thick).align_to(c1, ":>X <Y")
    b3 = cube(tall_len, thick, thick).align_to(c1, ":>X >Y")
    c2 = conic(r1=thick / 2, r2=r2, h=2.9 + 1).align_to(b3, ":>Z -Y >X")
    obj = c1 + b2 + b3 + c2
    return obj


obj = get_obj()
