"""Command Strip mounting plates for b4dcad.

Only the three rectangular pairs from command_strip_plate.py's preview.
Requires b4dcad and cadquery. From the repository root:

    b4dcad preview src/command_strip_plate_b4d.py
    b4dcad stl src/command_strip_plate_b4d.py ./stl

The six public parts export separately; show_assembly is preview-only.
"""

import math

import cadquery as cq
from b4dcad import cube, from_cq, is_rendering

WIDTH = 63 - 0.2 - 0.3
HEIGHT = 46
THICK = 2
SEAM = 0.16
SEAM_THICK = 0.06
TESSELLATION_TOLERANCE = 0.01


def flat_plate(n=4, width=None, height=HEIGHT, thick=THICK, extra_thick=THICK, round=7):
    """Return (male, female) in the original CQ model's coordinates.

    The +Y corners are rounded; the -Y end stays open for sliding the
    plates apart. Keep CQ's asymmetric chamfer so the mating surfaces
    match the original, including the curved portions of the bevel.
    """
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    if width is None:
        assert n > 0
        width = WIDTH * n / 4.0 + 10

    def get_plate(w, h, thick_d=0):
        plate = (
            cq.Workplane("XY")
            .box(w, h, thick + thick_d)
            .faces(">Y")
            .edges("Z")
            .fillet(round)
            .edges(">Z")
            .filter(lambda edge: edge.Center().y > -5)
            .chamfer(d, d2)
        )
        return from_cq(plate, tolerance=TESSELLATION_TOLERANCE)

    w, h = width + d2 * 2, height + d2 * 2
    male = get_plate(w, h)
    edge = 4
    female = cube(width + edge * 2, height + edge, thick + extra_thick, center=True)
    female = female.align_to(male, ">Z <Y")
    female -= get_plate(w + SEAM * 2, h + SEAM, SEAM_THICK)
    female = female.align_to(male, "<Z")
    return male, female


def _preview_pair(male, female):
    return (male + female.align_to(male, ">Z", dy=20)).rotate(y=180)


if is_rendering():
    flat1_male, flat1_female = flat_plate(n=1, round=5)
    flat2_male, flat2_female = flat_plate(n=2, round=5)
    flat4_male, flat4_female = flat_plate(n=4, round=5)

    _flat1 = _preview_pair(flat1_male, flat1_female)
    _flat2 = _preview_pair(flat2_male, flat2_female).align_to(_flat1, ":>X", dx=10)
    _flat4 = _preview_pair(flat4_male, flat4_female).align_to(_flat2, ":>X", dx=10)
    show_assembly = _flat1 + _flat2 + _flat4
