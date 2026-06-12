from b4dcad import polygon

sheet_z = 0.95
sheet_x = 252
sheet_y = 200

thick = 2
edge_l = 10
corner_l = 3
border_h = 10


def get_part(l):
    p1 = (
        polygon(
            [
                (0, 0),
                (0, edge_l + thick),
                (thick, 0),
                (0, -edge_l),
                (sheet_z, 0),
                (0, edge_l),
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
    p1 = get_part(sheet_x)
    p2 = get_part(sheet_y).rotate(z=90).align_to(p1, ":<X")
    p3 = p1.rotate(z=180).align_to(p2, ":<X >Y")
    p4 = p2.rotate(z=180).align_to(p3, ":>X <Y")
    obj = p1 + p2 + p3 + p4
    return obj


show_obj = get_show_obj()

part1 = get_part(sheet_x).rotate(y=90)
part2 = get_part(sheet_y).rotate(y=90)
