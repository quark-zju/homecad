"""Command Strip mounting plates for b4dcad.

Only the three rectangular pairs from command_strip_plate.py's preview.
Requires b4dcad and cadquery. From the repository root:

    b4dcad preview src/misc/command_strip_plate_b4d.py
    b4dcad stl src/misc/command_strip_plate_b4d.py ./stl

The six public parts export separately; show_assembly is preview-only.
Run geometry regression checks with:

    python -m doctest src/misc/command_strip_plate_b4d.py
"""

import math

import cadquery as cq
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer
from b4dcad import cube, from_cq, is_rendering

WIDTH = (63 - 0.2 - 0.3) / 4.0
HEIGHT = 46.0
THICK = 2.0
SEAM = 0.16
SEAM_THICK = 0.06
TESSELLATION_TOLERANCE = 0.01


def flat_plate(
    n=4, width=None, height=HEIGHT, thick=THICK, female_thick=THICK, round=5.0
):
    """Return (male, female) in the original CQ model's coordinates.

    The +Y corners are rounded; the -Y end stays open for sliding the
    plates apart. The bevel is 30 degrees from vertical on both parts,
    including the curved portions. Explicitly use the top face as the
    chamfer reference: CQ's automatic choice can swap unequal distances.

    Regression: unequal chamfer distances must not swap when dimensions change.
    Check the three straight sides and the tessellated rounded portions.

    >>> import numpy as np
    >>> def check_bevel(part, cavity=False):
    ...     assert not part.is_empty()
    ...     assert len(part.decompose()) == 1
    ...     mesh = part.manifold.to_mesh()
    ...     vertices = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
    ...     triangles = vertices[np.asarray(mesh.tri_verts)]
    ...     normals = np.cross(
    ...         triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
    ...     )
    ...     lengths = np.linalg.norm(normals, axis=1)
    ...     normals = normals[lengths > 1e-8] / lengths[lengths > 1e-8, None]
    ...     nz = np.abs(normals[:, 2])
    ...     bevels = normals[(nz > 0.01) & (nz < 0.99)]
    ...     assert len(bevels) > 0
    ...     # Include rounded portions: tessellating a conical bevel perturbs its
    ...     # normals slightly, but must never turn a 30-degree bevel into 60.
    ...     np.testing.assert_allclose(np.abs(bevels[:, 2]), 0.5, atol=0.04)
    ...     for axis, sign in ((0, -1), (0, 1), (1, 1)):
    ...         if cavity:
    ...             sign = -sign
    ...         straight = bevels[
    ...             (np.abs(bevels[:, 1 - axis]) < 1e-5) & (bevels[:, axis] * sign > 0.8)
    ...         ]
    ...         assert len(straight) > 0
    ...         np.testing.assert_allclose(np.abs(straight[:, 2]), 0.5, atol=1e-4)
    >>> male, female = flat_plate(width=46.5, thick=2.8, female_thick=0.4, round=5)
    >>> check_bevel(male)
    >>> check_bevel(female, cavity=True)
    >>> (male & female.align_to(male, ">Z")).is_empty()
    True
    >>> for thick in (0.8, 2.0, 2.8, 4.0):
    ...     male, female = flat_plate(thick=thick, female_thick=0.4)
    ...     check_bevel(male)
    ...     check_bevel(female, cavity=True)
    ...     assert (male & female.align_to(male, ">Z")).is_empty()
    """
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    if width is None:
        assert n > 0
        width = WIDTH * n + max(round, 1) * 2

    def get_plate(w, h, thick_d=0):
        plate = (
            cq.Workplane("XY")
            .box(w, h, thick + thick_d)
            .faces(">Y")
            .edges("Z")
            .fillet(round)
        )
        top = plate.faces(">Z")
        chamfer = BRepFilletAPI_MakeChamfer(plate.val().wrapped)
        for edge in top.edges().filter(lambda edge: edge.Center().y > -5).vals():
            # First distance is on the reference (top) face; second is vertical.
            chamfer.Add(d2, d, edge.wrapped, top.val().wrapped)
        plate = plate.newObject([cq.Solid(chamfer.Shape())])
        return from_cq(plate, tolerance=TESSELLATION_TOLERANCE)

    w, h = width + d2 * 2, height + d2 * 2
    male = get_plate(w, h)
    edge = 4
    female = cube(width + edge * 2, height + edge, thick + female_thick, center=True)
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
