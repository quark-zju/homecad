import command_strip_plate_b4d
from b4dcad import cube

# Punch holes for 2 circle magnents
magnent_height = 26.5
magnent_inner_height = 24.2
magnent_width = 12 + 2


female_thick = 3.72 - 1 + 0.4
round = 1.2
_male, _female = command_strip_plate_b4d.flat_plate(
    width=command_strip_plate_b4d.WIDTH * 2 + magnent_inner_height + round * 2,
    thick=2,
    female_thick=female_thick, round=round
)

def get_part1():
    o1 = _male.rotate_axis('Y',180)
    o1_size = o1.size()
    b1 = cube(magnent_inner_height, o1_size.y * 0.8-1.4, 3.4).align_to(o1, ">Y >Z -X")
    b2 = cube(magnent_height, o1_size.y * 0.8, 3-1.6).align_to(o1, ">Y >Z -X")
    o2 = o1 - b1 - b2
    return o2

inner_height = 45

def get_part2():
    o1 = _female
    o1_size = o1.size()

    b1 = cube(inner_height, o1_size.y - 6 - 2.5, o1_size.z)
    b1 = b1.align_to(o1, "-X <Y <Z")
    o2 = o1 - b1

    o2_size = o2.size()
    b2 = cube(o2_size.x, o2_size.y, female_thick).align_to(o2, "<Z -X -Y")

    o3a = b2 & o2
    o3b = o2 - o3a
    # o3c =

    return o2


part1 = get_part1()
part2 = get_part2()
