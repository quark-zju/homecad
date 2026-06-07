from b4dcad import cylinder


def get_obj(r1=70 / 2, r2=51.2 / 2, w1=17, n=20, slot_width=2, thick=1.2):
    c1 = cylinder(h=thick, r=r1)
    c2 = cylinder(h=thick, r=r2)
    obj = c1 - c2
    b0 = cylinder(h=w1, d=slot_width).align_to(c1, ">X")
    b1 = cylinder(h=w1, d=slot_width).align_to(c2, ":>X")
    b2 = b1.move(x=(r1 - r2 - slot_width) / 2.0).rotate(z=180.0 / n)
    for i in range(n):
        angle = 360.0 / n * i
        bi = b0.rotate(z=angle) + b1.rotate(z=angle) + b2.rotate(z=angle)
        obj += bi
    return obj


obj = get_obj()
