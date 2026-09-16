import command_strip_plate_b4d
from b4dcad import cube, cylinder

# Punch holes for 2 circle magnents
magnent_x = 26.5
magnent_inner_x = 24.2
magnent_y = 12 + 2


female_thick = 0.4
round = 5
_male, _female = command_strip_plate_b4d.flat_plate(
    width=magnent_x + round * 2 + 4, thick=2.8, female_thick=female_thick, round=round
)


def get_wall_part():
    o1 = _female
    # Extend on both sizes
    o1_size = o1.size()
    b1 = cube(command_strip_plate_b4d.WIDTH / 2, o1_size.y, o1_size.z)
    b1a = b1.align_to(o1, ":<X <Y <Z")
    b1b = b1.align_to(o1, ":>X <Y <Z")
    o2 = o1 + b1a + b1b

    b2 = cube(magnent_x + 2, 10, o1_size.z)
    b2 = b2.align_to(o1, "<Z >Y -X", dz=female_thick)
    o3 = o2 - b2

    return o3


inner_height = 45


def get_mount_part():
    o1 = _male
    o1_size = o1.size()
    # print('mount', o1_size)

    d = 12.5
    c1 = cylinder(d=d, h=o1_size.z)
    c1a = c1.align_to(o1, "-X :>Y >Z", dx=-7, dy=-3)
    c1b = c1.align_to(o1, "-X :>Y >Z", dx=7, dy=-3)

    o2 = o1 - c1a - c1b

    return o2


wall_part = get_wall_part()
mount_part = get_mount_part()
