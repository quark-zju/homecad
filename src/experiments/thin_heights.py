from b4dcad import cube

"""
Experiments about thin heights

legend:
- wanted: model definition
- got: measured (roughly)
- n layer(s), m mm: slicing output, slicing theorical height

layer height = 0.2mm; first layer = 0.2mm; precise Z height
- wanted 0.15 to 0.25, got ~0.3  (1 layer,  0.2mm)
- wanted 0.30 to 0.50, got ~0.55 (2 layers, 0.4mm)
- wanted 0.55 to 0.60, got ~0.7  (3 layers, 0.6mm)

layer height = 0.2mm; first layer = 0.32mm; precise Z height
- wanted 0.15, got nothing
- wanted 0.20 to 0.40, got ~0.45 (1 layer,  0.32mm)
- wanted 0.45 to 0.60, got ~0.60 (2 layers, 0.52mm)

layer height = 0.08mm; first layer = 0.2mm; precise Z height
- wanted 0.15 to 0.20, got ~0.35 (1 layer,  0.20mm)
- wanted 0.25 to 0.30, got ~0.42 (2 layers, 0.28mm)
- wanted 0.35        , got ~0.48 (3 layers, 0.36mm)
- wanted 0.40 to 0.45, got ~0.53 (4 layers, 0.42mm)
- wanted 0.50 to 0.55, got ~0.60 (5 layers, 0.50mm)
- wanted 0.60        , got ~0.66 (6 layers, 0.58mm)

Overall, +0.12mm
"""


def get_obj():
    o = None
    x = 6
    y = 16
    for i, h in enumerate([0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]):
        c = cube(x, y - i * 0.6, h)
        if o:
            c = c.align_to(o, ":<X")
        o = (o or c) + c
    return o


heights = get_obj()
