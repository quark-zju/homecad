import command_strip_plate_b4d
from b4dcad import cube

# Punch holes for 2 circle magnents
magnent_x = 26.5
magnent_inner_x = 24.2
magnent_y = 12 + 2


female_thick = 3.72 - 1 + 0.4
round = 1.2
_male, _female = command_strip_plate_b4d.flat_plate(
    width=magnent_x + round * 2, thick=2, female_thick=0.4, round=round
)


def get_wall_part():
    o1 = _female
    # Extend on both sizes
    o1_size = o1.size()
    b1 = cube(command_strip_plate_b4d.WIDTH / 2, o1_size.y, o1_size.z)
    b1a = b1.align_to(o1, ":<X <Y <Z")
    b1b = b1.align_to(o1, ":>X <Y <Z")
    o2 = o1 + b1a + b1b
    return o2


inner_height = 45


def get_mount_part():
    o1 = _male
    o1_size = o1.size()

    b1 = cube((o1_size.x - 2) / 2, magnent_y, o1_size.z)
    b1a = b1.align_to(o1, "<X -Y <Z")
    b1b = b1.align_to(o1, ">X -Y <Z")
    o2 = o1 - b1a - b1b

    return o2


wall_part = get_wall_part()
mount_part = get_mount_part()
