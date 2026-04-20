from cqutils import W, union_all

# Mount Noctua NF-A4x10 to back of a projector

nfa4_width = 40.2
nfa4_depth = 11
h = 123
pad = 2


def render():
    b1 = W().box(nfa4_width, nfa4_width, nfa4_depth)
    b2 = W().box(nfa4_width + pad * 2, nfa4_width + pad * 2, nfa4_depth)
    b3 = b2.cut(b1)
    b4 = W().box(pad, h, nfa4_depth).align(b3, "<X <Y")
    b5 = W().box(20, pad, nfa4_depth).align(b4, ">Y >X")
    obj = union_all([b3, b4, b5])
    return obj


render().show().export()
