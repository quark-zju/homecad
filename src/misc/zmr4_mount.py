import command_strip_plate_b4d
from b4dcad import cube

female_thick = 1
part1, _female = command_strip_plate_b4d.flat_plate(n=1, female_thick=female_thick, round=5)


def get_part2():
    o1 = _female  # Size(x=33.625, y=50.0, z=4.0)

    # Punch holes for 2 circle magnents
    h = 26 + 2
    w = 12 + 2
    b1 = cube(h, w, 3)
    b1 = b1.align_to(o1, "-X -Y <Z")
    o2 = o1 - b1

    return o2


part2 = get_part2()
