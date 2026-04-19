"""
Bicolor Step Gradient Calibration

A stepped bicolor gradient model for calibrating the RGB response of layered 3D prints using photographed results.

**Printing settings**

Similar to HueForge, print at 100% infill with a layer height of 0.08mm and a base layer of 0.16mm.

At layer #5 (0.48mm), switch color.

**Motivation**

HueForge appears to assume a linear relationship between layer count and color blending in the linear space, which I have suspection.

In practice, light transmission through layered prints is non‑linear due to absorption and scattering.

This calibration model is intended to empirically measure how perceived color accumulates with increasing layer thickness, providing data for more physically accurate color‑to‑thickness mapping.

"""

from cqutils import *


def render(size=8, bottom_thick=0.40, layer_thick=0.08, n=4, pad=5):
    objs = []
    for x in range(n):
        for y in range(n):
            i = x * n + y + 1
            b = (
                W()
                .box(size, size, i * layer_thick + bottom_thick, centered=False)
                .align(dx=size * x, dy=size * y)
            )
            objs.append(b)
    b1 = union_all(objs)
    b2 = W().box(n * size + pad, n * size + pad, bottom_thick).align(b1, "<Z -X -Y")
    obj = b1.union(b2)
    return obj


render().show().export()
