# Designed for wall mounting
# https://www.amazon.com/dp/B0CN1LJN11
# 6 Pack Clear Plexiglass Sheets 8×10×0.04In Thin PET Plexi Glass Sheets for Craft Projects Easy-Process Transparent Flexible Plastic Blanks Sheeting for Picture Frames

import command_strip_plate_b4d
from b4dcad import cube

_male, _female = command_strip_plate_b4d.flat_plate(n=2, round=5, female_thick=0.6, thick=1.2)


def get_frame_part():
    # thick:
    # | command_strip=1.24 | _female             |
    #                               | thin_plate |
    # |         frame=2.45          |
    command_strip_thick = 1.24
    female_size = _female.size()
    female_thick = female_size.z
    frame_thick = 2.45
    thin_plate_ideal_thick = command_strip_thick + female_thick - frame_thick
    assert thin_plate_ideal_thick < 0.6
    # extend plate size for strength
    extend_y = 4
    extend_x = 5
    b1 = cube(female_size.x, extend_y, female_size.z).align_to(_female, ":>Y <Z <X")
    o1 = _female + b1
    b2a = cube(extend_x, o1.size().y, female_size.z).align_to(o1, ":<X >Y >Z")
    b2b = b2a.align_to(o1, ":>X")
    o2 = o1 + b2a + b2b
    b3 = cube(o2.size().x, 20, thin_plate_ideal_thick).align_to(o2, ":>Y <Z <X")
    o3 = o2 + b3
    return o3


wall_part = _male
frame_part = get_frame_part()
