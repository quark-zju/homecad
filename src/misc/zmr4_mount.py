"""Command-strip mount for the ZMR4 blind mounting slots.

+Y is the top of the switch; +Z points into its backplate. Insert both
eccentric heads, then slide the switch down about 1.2 mm to hang it. Lift
the switch by the same amount before pulling it off. This is a gravity
hook, not a snap lock.

The heads use the roughly 1.5 mm recess around the 7 x 4 mm slot openings.
The two strip lanes remain open above and below the central adhesive pad.
"""

from b4dcad import cube, cylinder

# 3M strip, medium
height_3m = 46
width_3m = 16

mounting_hole_distance = 84
mounting_hole_diameter = 4
mounting_hole_length = 7
mounting_hole_depth = 4.3
# Distance from the mount face to the underside of the retaining head.
# The measured lip is slightly thinner than this, leaving sliding clearance.
mounting_hole_thick = 2.2

neck_diameter = 2.6
head_diameter = 3.2
head_offset = 0.6  # Toward +Y; both hooks point in the same direction.
head_thick = 0.8  # Total insertion depth 3.0 mm; 1.3 mm clear of the bottom.
edge_clearance = 0.1

thick = 1.6
padding = 6
end_padding = 1

# From the insertion position (head centered on the slot's upper rounded
# end) to the hanging position. Nominally 1.2 mm, with 0.1 mm settling room.
slide_distance = (
    mounting_hole_diameter / 2 - neck_diameter / 2 - edge_clearance + head_offset
)
bottom_clearance = mounting_hole_depth - mounting_hole_thick - head_thick


def get_hook(slot):
    neck = cylinder(d=neck_diameter, h=mounting_hole_thick).align_to(
        slot, ":>Z -X >Y", dy=-edge_clearance
    )
    head = cylinder(d=head_diameter, h=head_thick).align_to(
        neck, ":>Z -X -Y", dy=head_offset
    )
    return neck + head


def get_part1():
    pad_width = width_3m * 2 + padding
    pad = cube(pad_width, height_3m, thick)
    # The spine occupies only the gap between the two 16 mm strip lanes:
    # no crossbars obstruct either pull tab or its straight pulling path.
    spine = cube(
        padding,
        mounting_hole_distance + mounting_hole_diameter + end_padding * 2,
        thick,
    ).align_to(pad, "-X -Y")

    # Alignment references only; these envelopes are not part of the print.
    top_slot = cube(mounting_hole_length, mounting_hole_diameter, thick).align_to(
        spine, "-X >Y <Z", dy=-end_padding
    )
    bottom_slot = cube(mounting_hole_diameter, mounting_hole_length, thick).align_to(
        top_slot, "-X -Y <Z", dy=-mounting_hole_distance
    )

    # Locate the necks from the UPPER edges, not the hole centers. The top
    # slot is horizontal (4 mm tall), the bottom vertical (7 mm tall), so
    # the neck centers are 82.5 mm apart although the hole centers are 84.
    return pad + spine + get_hook(top_slot) + get_hook(bottom_slot)


part1 = get_part1()
