from b4dcad import cube

import command_strip_plate_b4d as s

_male, _female = s.flat_plate(n=4, shape='circle')

def get_wall_part():
    # 2 strips: 极限
    # 4 strips: 安全一点
    return _female


def get_mount_part():
    # 300LSE, 2.2kg, 12mm 胶带, 大约需要（极限）6.2mm
    # 30–40 cm 保守
    o1 = _male
    s1 = _female.size()
    o2 = cube(x=199, y=14*2, z=_male.size().z).align_to(o1, '<Z -X <Y', dy=s1.y+3)
    o3 = o1 + o2
    return o3

def get_bottom_part():
    mirror_thickness = 3.2
    width = s.WIDTH * 2
    b1 = cube(width, s.HEIGHT, _female.size().z)
    b2 = cube(width, 5, mirror_thickness + 1).align_to(b1, "-X <Y :>Z")
    o1 = b1 + b2
    return o1

wall_part = get_wall_part()
mount_part = get_mount_part()
bottom_part = get_bottom_part()
