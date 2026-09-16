"""Regression checks for the straight command-strip plate pair."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1] / "src" / "misc"))
import command_strip_plate_b4d as plates  # noqa: E402


class CommandStripPlateGeometryTest(unittest.TestCase):
    def assert_bevel_angle(self, part, cavity=False):
        self.assertFalse(part.is_empty())
        self.assertEqual(len(part.decompose()), 1)
        mesh = part.manifold.to_mesh()
        vertices = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
        triangles = vertices[np.asarray(mesh.tri_verts)]
        normals = np.cross(
            triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
        )
        lengths = np.linalg.norm(normals, axis=1)
        normals = normals[lengths > 1e-8] / lengths[lengths > 1e-8, None]
        nz = np.abs(normals[:, 2])
        bevels = normals[(nz > 0.01) & (nz < 0.99)]
        self.assertGreater(len(bevels), 0)
        # Include rounded portions: tessellating a conical bevel perturbs its
        # normals slightly, but must never turn a 30-degree bevel into 60.
        np.testing.assert_allclose(np.abs(bevels[:, 2]), 0.5, atol=0.04)
        for axis, sign in ((0, -1), (0, 1), (1, 1)):
            if cavity:
                sign = -sign
            straight = bevels[
                (np.abs(bevels[:, 1 - axis]) < 1e-5) & (bevels[:, axis] * sign > 0.8)
            ]
            self.assertGreater(len(straight), 0)
            np.testing.assert_allclose(np.abs(straight[:, 2]), 0.5, atol=1e-4)

    def test_user_example_has_matching_bevels_and_clear_assembly(self):
        thick = 2.8
        male, female = plates.flat_plate(
            width=26.5 + 5 * 2 + 10,
            thick=thick,
            female_thick=0.4,
            round=5,
        )
        self.assert_bevel_angle(male)
        self.assert_bevel_angle(female, cavity=True)

        assembled_female = female.align_to(male, ">Z")
        intersection = male & assembled_female
        self.assertTrue(intersection.is_empty())

    def test_defaults_and_thicknesses_keep_both_surfaces_equal(self):
        for thick in (0.8, 2.0, 2.8, 4.0):
            with self.subTest(thick=thick):
                male, female = plates.flat_plate(thick=thick, female_thick=0.4)
                self.assert_bevel_angle(male)
                self.assert_bevel_angle(female, cavity=True)
                self.assertTrue((male & female.align_to(male, ">Z")).is_empty())


if __name__ == "__main__":
    unittest.main()
