"""
Add border to make [a plastic sheet (25x20x1mm)](https://www.amazon.com/dp/B0CN1LJN11) a tray.
"""

from b4dcad import polygon

sheet_z = 0.95
sheet_x = 252
sheet_y = 201

thick = 2.6
edge_l = 5
corner_l = 2.6
border_h = 10

seam1 = 0.6
seam2 = 0.2


def get_part(l):
    p1 = (
        polygon(
            [
                (0, 0),
                (0, edge_l + thick),
                (thick, 0),
                (-seam2, -edge_l - seam1),
                (sheet_z + seam2 * 2, 0),
                (-seam2, edge_l + seam1),
                (thick, 0),
                (0, corner_l - edge_l),
                (corner_l, -corner_l),
                (border_h - corner_l, 0),
                (0, -thick),
            ],
            relative=True,
        )
        .extrude(l)
        .rotate(x=90, y=-90)
    )
    px, _py, pz = p1.size()
    p2 = polygon([(0, 0), (-px * 1.45, -px * 1.45), (-px * 1.45, 0)]).extrude(pz)
    p2b = p2.rotate(z=90).align_to(p1, "<Y >X")
    o1 = p1 - p2 - p2b
    return o1


def get_show_obj():
    p1 = get_part(sheet_x + thick * 2)
    p2 = get_part(sheet_y + thick * 2).rotate(z=90).align_to(p1, ":<X")
    p3 = p1.rotate(z=180).align_to(p2, ":<X >Y")
    p4 = p2.rotate(z=180).align_to(p3, ":>X <Y")
    obj = p1 + p2 + p3 + p4
    return obj


show_obj = get_show_obj()

part1 = get_part(sheet_x + thick * 2).rotate(y=90)
part2 = get_part(sheet_y + thick * 2).rotate(y=90)
