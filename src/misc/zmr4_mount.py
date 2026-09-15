from b4dcad import  cube, cylinder

# 3M strip, medium
height_3m = 46
width_3m = 16

mounting_hole_distance = 84
mounting_hole_diameter = 4
mounting_hole_depth = 4.2
mounting_hole_thick = 2.2

thick = 1
padding = 6


def get_part1():
    b1 =  cube(width_3m * 2 + padding, height_3m, thick)
    b2 = cube(padding, mounting_hole_distance + mounting_hole_diameter, thick).align_to(b1, "-X -Y")
    c1 = cylinder(d=mounting_hole_diameter,h=mounting_hole_thick)
    c1a = c1.align_to(b2, ":>Z -X >Y")
    c1b = c1.align_to(b2, ":>Z -X <Y")
    o1 = b1 + b2 + c1a + c1b

    return o1


part1 = get_part1()
