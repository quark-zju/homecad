from cqutils import *


def get_obj(side=0):
    s = 2
    r = 21 / 2 + s
    thick = 6 + s
    c1 = W().cylinder(thick, r).rotate_axis("X", 90)
    h = 46
    b1h = r * 2
    b1 = W().box(r * 2, thick, b1h).align(c1, ">Y <Z", dz=r)
    b1c = W().box(r * 2 - s, thick - s, b1h).align(b1, f"{side and '<' or '>'}X <Y >Z")
    obj = c1.union(b1).faces("<Y").shell(-s).cut(b1c)
    b2 = W().box(r * 2 - s * 2, thick - s, h).align(b1, "<Z <Y")
    obj = obj.cut(b2)
    b3 = W().box(63 / 4, s, h - r).align(b1, ":<Z >Y")
    obj = obj.union(b3)
    # print(obj.measure())
    return obj


def render():
    o1 = get_obj(0)
    o2 = get_obj(1)
    obj = o1.union(o2.translate((o1.measure("X") + 6, 0, 0)))
    return obj


render().show().export()
