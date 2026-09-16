"""Parametric inverted Cetaphil bottle stand, in mm; pure b4dcad.

See cetaphil_stand.md for scan provenance, fit adjustment and printing.

    b4dcad preview cetaphil_stand.py
"""

from dataclasses import dataclass
import math

from b4dcad import Solid, is_rendering, polygon

# Height from the inverted cap tip, full width, full depth. Smoothed scan
# envelopes, not a decimated scan. The latch depression is intentionally filled
# so the socket has no undercut and the bottle can lift straight out.
CAP_SECTIONS = (
    (4.0, 38.5, 23.5),
    (8.0, 51.5, 31.0),
    (12.0, 60.8, 36.4),
    (16.0, 67.5, 39.5),
    (20.0, 73.0, 42.0),
    (24.0, 77.2, 44.3),
    (28.0, 80.5, 45.7),
    (32.0, 82.8, 46.7),
    (36.0, 84.3, 47.2),
    (40.0, 84.8, 47.5),
)


@dataclass(frozen=True)
class Parameters:
    # Scale the scanned cap only; print clearance and wall remain in mm.
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    clearance: float = 0.8  # Per side, using a planar polygon offset.
    wall: float = 3.0
    tip_gap: float = 6.0  # Nominal; the cap settles slightly under gravity.
    cradle_start: float = 16.0  # Unscaled scan height; leave the tip free.
    cradle_end: float = 32.0
    base_width: float = 116.0
    base_depth: float = 90.0
    base_thickness: float = 3.2
    drain_height: float = 1.6  # Four triangular channels under the base.
    lead_in: float = 0.6  # Extra radial relief over the last 2 mm.
    exponent: float = 2.3  # Superellipse: 2 = ellipse, larger = squarer.
    segments: int = 128

    def __post_init__(self):
        positive = (
            self.width_scale,
            self.depth_scale,
            self.height_scale,
            self.wall,
            self.tip_gap,
            self.base_width,
            self.base_depth,
            self.base_thickness,
        )
        if not all(math.isfinite(v) and v > 0 for v in positive):
            raise ValueError(
                "Scales, wall, tip gap and base dimensions must be positive"
            )
        if not all(math.isfinite(v) and v >= 0 for v in (self.clearance, self.lead_in)):
            raise ValueError("Clearance and lead-in must be nonnegative")
        if not 0 < self.drain_height <= self.base_thickness - 1.0:
            raise ValueError("Drain channels need at least 1 mm of roof")
        if not 12 <= self.cradle_start < self.cradle_end <= 40:
            raise ValueError("Cradle must lie within scan heights 12..40 mm")
        if (self.cradle_end - self.cradle_start) * self.height_scale <= 3:
            raise ValueError("Cradle band must exceed 3 mm in height")
        if self.tip_gap + self.cradle_start * self.height_scale <= self.base_thickness:
            raise ValueError("Cradle must start above the base")
        if not 2 <= self.exponent <= 3 or self.segments < 48 or self.segments % 4:
            raise ValueError("Use exponent 2..3 and a multiple of four segments >=48")
        w, d = _dimensions(self.cradle_end)
        if self.base_width < w * self.width_scale + 2 * (
            self.clearance + self.wall + 5
        ) or self.base_depth < d * self.depth_scale + 2 * (
            self.clearance + self.wall + 5
        ):
            raise ValueError("Base must extend at least 5 mm beyond the cradle")


def _dimensions(height):
    for (z0, w0, d0), (z1, w1, d1) in zip(CAP_SECTIONS, CAP_SECTIONS[1:]):
        if z0 <= height <= z1:
            t = (height - z0) / (z1 - z0)
            return w0 + t * (w1 - w0), d0 + t * (d1 - d0)
    raise ValueError("Height outside measured cap sections")


def _oval(width, depth, exponent, segments):
    def power(v):
        return math.copysign(abs(v) ** (2 / exponent), v)

    return polygon(
        [
            (
                width / 2 * power(math.cos(2 * math.pi * i / segments)),
                depth / 2 * power(math.sin(2 * math.pi * i / segments)),
            )
            for i in range(segments)
        ]
    )


def _cap_section(height, p):
    w, d = _dimensions(height)
    return _oval(w * p.width_scale, d * p.depth_scale, p.exponent, p.segments)


def _loft(sections):
    """Join matching convex polygon sections without a CAD-kernel dependency."""
    result = Solid()
    for (z0, a), (z1, b) in zip(sections, sections[1:]):
        result += a.extrude_to(b, z1 - z0).move(z=z0)
    return result


def _cradle_sections(p):
    # Include the lead-in start even when it is between measured stations.
    lead_start = p.cradle_end - 2.0 / p.height_scale
    heights = sorted(
        {p.cradle_start, p.cradle_end, lead_start}
        | {z for z, _, _ in CAP_SECTIONS if p.cradle_start < z < p.cradle_end}
    )
    inner, outer = [], []
    for h in heights:
        z = p.tip_gap + h * p.height_scale
        socket = _cap_section(h, p).offset(p.clearance)
        relief = p.lead_in * max(0, (h - lead_start) / (p.cradle_end - lead_start))
        inner.append((z, socket.offset(relief)))
        # Keep full wall thickness even through the mouth's lead-in.
        outer.append((z, socket.offset(p.wall + relief)))
    return inner, outer


def make_stand(p=None):
    p = p or Parameters()
    inner, outer = _cradle_sections(p)
    # The lower throat is straight and completely open: the cap tip hangs free.
    shell = _loft([(0, outer[0][1])] + outer)
    flange = _oval(p.base_width, p.base_depth, 2, p.segments).extrude(p.base_thickness)
    cavity = _loft([(-1, inner[0][1])] + inner + [(inner[-1][0] + 1, inner[-1][1])])
    stand = shell + flange - cavity
    # V roofs are 45 degrees; unlike rectangular underside slots they need no
    # horizontal bridging. Rotating XY extrusion puts its run along X.
    h = p.drain_height
    length = max(p.base_width, p.base_depth) + 2
    drain = polygon([(-h, -1), (h, -1), (h, 0), (0, h), (-h, 0)]).extrude(length)
    drain = drain.rotate(x=90).rotate(z=90).move(x=-length / 2)
    return stand - drain - drain.rotate(z=90)


def make_fit_ring(p=None):
    """The entire contact band, without the pedestal; hold it around the cap."""
    p = p or Parameters()
    inner, outer = _cradle_sections(p)
    cavity = _loft(
        [(inner[0][0] - 1, inner[0][1])] + inner + [(inner[-1][0] + 1, inner[-1][1])]
    )
    return (_loft(outer) - cavity).move(z=-inner[0][0])


def reference_cap(p=None):
    """Smoothed crown only, for visual fit checks; not a printable bottle cap."""
    p = p or Parameters()
    sections = [(z * p.height_scale, _cap_section(z, p)) for z, _, _ in CAP_SECTIONS]
    # Close the unmeasured first 4 mm with a cone. A dedicated extrusion to an
    # apex avoids ambiguous vertex correspondence in a near-zero loft ring.
    tip = (
        sections[0][1]
        .extrude(sections[0][0], scale_top=(0, 0))
        .rotate(x=180)
        .move(z=sections[0][0])
    )
    return (_loft(sections) + tip).move(z=p.tip_gap)


if is_rendering():
    settings = Parameters()
    stand = make_stand(settings)
    fit_ring = make_fit_ring(settings).move(x=settings.base_width + 12)
    show_assembly = stand + fit_ring
    show_cap = reference_cap(settings)
