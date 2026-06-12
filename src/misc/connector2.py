from b4dcad import cube, cylinder


def get_obj(r1=6.0, thick=5.0, hook_len=40.0, tall_len=150.0):
    c1 = cylinder(h=thick, r=r1)
    c2 = cylinder(h=thick, r=r1 + thick)
    b1 = cube(r1 + thick, (r1 + thick) * 2, thick).align_to(c2, ">X >Y")
    c3 = c2 - c1 - b1
    b2 = cube(hook_len, thick, thick).align_to(c3, ":>X <Y")
    b3 = cube(tall_len, thick, thick).align_to(c3, ":>X >Y")
    c4 = c3.rotate(z=180, x=90).align_to(b3, ":>X >Y <Z")
    b4 = b2.align_to(c4, ">Z >Y :<X")
    obj = c3 + b2 + b3 + c4 + b4
    return obj


obj = get_obj()
