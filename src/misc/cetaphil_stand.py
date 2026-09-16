"""Cetaphil 倒置支撑座，纯 b4dcad，单位 mm。

加深版：承托区从距盖顶 16 mm 延伸至 72 mm，包覆深度 56 mm；
底座 116 × 90 × 78 mm。内腔保留下方瓶盖通过所需的截面，不随瓶身
变薄而收口。它靠加长导向限制倾斜，不会紧箍整段瓶身。

先打印 fit_ring（完整导向套、无底座）验证能自然落座并轻松拔出，
再打印 stand。平底朝下；默认几何按 45° 悬垂设计。实际稳定性需实测。

    b4dcad preview src/misc/cetaphil_stand.py
    b4dcad stl src/misc/cetaphil_stand.py ./stl --object fit_ring
    b4dcad stl src/misc/cetaphil_stand.py ./stl --object stand

修改末尾 settings = Parameters(...)：
  clearance=0.5：上部单侧间隙，原版为 0.8；
  lower_relief=0.7：窄口额外单侧余量，在最下方 16 mm 内渐消。
    默认窄口总间隙 1.2，比原版放松 0.4；宽口不随之放大。
  cradle_end=72：覆盖终点，可在 32..72 内调整；cradle_start=16 保持不变；
  wall=3、base_width=116、base_depth=90：壁厚和底座占地；
  width_scale / depth_scale / height_scale：只调参考瓶形的比例。

show_assembly 预览两件打印件，show_cap 为盖子及部分瓶身的参考体。
参考体不导出；试配套在预览中放于底座旁，切片时可单独居中。
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
    (44.0, 85.2, 48.1),
    (48.0, 85.8, 47.5),
    (52.0, 86.2, 46.6),
    (56.0, 86.8, 45.8),
    (60.0, 87.4, 44.7),
    (64.0, 89.2, 43.7),
    (68.0, 89.8, 42.5),
    (72.0, 90.0, 41.3),
)


@dataclass(frozen=True)
class Parameters:
    # Scale the scanned cap only; print clearance and wall remain in mm.
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    clearance: float = 0.5  # Per side, using a planar polygon offset.
    lower_relief: float = 0.7  # Extra clearance only at the tight lower lip.
    relief_height: float = 16.0  # Physical height over which it fades to zero.
    wall: float = 3.0
    tip_gap: float = 6.0  # Nominal; the cap settles slightly under gravity.
    cradle_start: float = 16.0  # Unscaled scan height; leave the tip free.
    cradle_end: float = 72.0
    base_width: float = 116.0
    base_depth: float = 90.0
    base_thickness: float = 3.2
    drain_height: float = 1.6  # Four triangular channels under the base.
    lead_in: float = 0.35  # Extra radial relief over the last 2 mm.
    exponent: float = 2.3  # Superellipse: 2 = ellipse, larger = squarer.
    body_exponent: float = 3.2  # The bottle shoulder is squarer than the cap.
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
            self.relief_height,
        )
        if not all(math.isfinite(v) and v > 0 for v in positive):
            raise ValueError(
                "Scales, wall, tip gap and base dimensions must be positive"
            )
        if not all(
            math.isfinite(v) and v >= 0
            for v in (self.clearance, self.lower_relief, self.lead_in)
        ):
            raise ValueError("Clearance and relief must be nonnegative")
        if not 0 < self.drain_height <= self.base_thickness - 1.0:
            raise ValueError("Drain channels need at least 1 mm of roof")
        if not 12 <= self.cradle_start < self.cradle_end <= CAP_SECTIONS[-1][0]:
            raise ValueError("Cradle must lie within profile heights 12..72 mm")
        if (self.cradle_end - self.cradle_start) * self.height_scale <= 3:
            raise ValueError("Cradle band must exceed 3 mm in height")
        if self.tip_gap + self.cradle_start * self.height_scale <= self.base_thickness:
            raise ValueError("Cradle must start above the base")
        if not 2 <= self.exponent <= 3 or self.segments < 48 or self.segments % 4:
            raise ValueError("Use exponent 2..3 and a multiple of four segments >=48")
        if not self.exponent <= self.body_exponent <= 4:
            raise ValueError("Body exponent must be between cap exponent and 4")
        w, d = _insertion_dimensions(self.cradle_end)
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


def _insertion_dimensions(height):
    """Envelope every lower section that must pass through this height."""
    sections = [_dimensions(height)] + [
        (w, d) for z, w, d in CAP_SECTIONS if z < height
    ]
    return tuple(max(s[axis] for s in sections) for axis in (0, 1))


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


def _profile_exponent(height, p):
    # Preserve the tested cap, then blend into the squarer bottle shoulder.
    t = max(0, min(1, (height - 44) / (72 - 44)))
    return p.exponent + t * (p.body_exponent - p.exponent)


def _cap_section(height, p):
    w, d = _dimensions(height)
    return _oval(
        w * p.width_scale, d * p.depth_scale, _profile_exponent(height, p), p.segments
    )


def _loft(sections):
    """Join matching convex polygon sections without a CAD-kernel dependency."""
    result = Solid()
    for (z0, a), (z1, b) in zip(sections, sections[1:]):
        # Loft a unit height before scaling: float32 mesh heights such as 4.4
        # otherwise leave tiny gaps between adjacent sections after translation.
        result += a.extrude_to(b, 1).scale(z=z1 - z0).move(z=z0)
    return result


def _cradle_sections(p):
    # Include the lead-in start even when it is between measured stations.
    lead_start = p.cradle_end - 2.0 / p.height_scale
    heights = sorted(
        {p.cradle_start, p.cradle_end, lead_start}
        | {z for z, _, _ in CAP_SECTIONS if p.cradle_start < z < p.cradle_end}
        | {min(p.cradle_end, p.cradle_start + p.relief_height / p.height_scale)}
    )
    inner, outer = [], []
    for h in heights:
        z = p.tip_gap + h * p.height_scale
        w, d = _insertion_dimensions(h)
        bottom_relief = p.lower_relief * max(
            0, 1 - (h - p.cradle_start) * p.height_scale / p.relief_height
        )
        socket = _oval(
            w * p.width_scale, d * p.depth_scale, _profile_exponent(h, p), p.segments
        ).offset(p.clearance + bottom_relief)
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
    """The full-depth guide without the pedestal, for handheld fit testing."""
    p = p or Parameters()
    inner, outer = _cradle_sections(p)
    cavity = _loft(
        [(inner[0][0] - 1, inner[0][1])] + inner + [(inner[-1][0] + 1, inner[-1][1])]
    )
    return (_loft(outer) - cavity).move(z=-inner[0][0])


def reference_cap(p=None):
    """Smoothed cap and lower bottle body, for visual fit checks only."""
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
