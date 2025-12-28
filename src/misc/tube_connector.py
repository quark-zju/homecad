from cqutils import *
import magnet

r1_thick = 2


def pipe_connector(r1, r2=None, thick=0):
    r2 = r2 or r1
    o1 = W(cq.Solid.makeTorus(r2, r1))
    ra = max(r1, r2)
    b1 = W().box(ra * 2, ra * 2, ra * 2, centered=(False, False, True))
    o1 = o1.intersect(b1)
    if thick > 0:
        o2 = pipe_connector(r1 - thick, r2=r1, thick=0)
        o1 = o1.cut(o2)
    return o1


r1 = 85 / 2
inner_width = 90
inner_height = 100
outer_depth1 = 22
thick1 = 5
b1 = W().box(inner_width, thick1, inner_height)
b1h = (
    b1.edges("|Y")
    .fillet(3)
    .faces("<Y")
    .workplane()
    .rect(inner_width - 14, inner_height - 14)
    .vertices()
    .cboreHole(3, 7, 3)  # for tag pins
)
c1l = 35
r1_thick = 2
r1 = r1 + r1_thick
c1 = W("XZ").cylinder(c1l, r1).align(b1, ":<Y")
c1a = W("XZ").cylinder(c1l + thick1, r1 - r1_thick).align(b1, ">Y")
c1b = c1.cut(c1a)  # .faces(">Y or <Y").shell(-thick)

# NOTE: Use "pause" to insert magnets
m_thin = 0.6
m1 = (
    magnet.magnet_3_10_60(hole_depth=0, c1a=0.01, c1b=0.01, m_h=3.4, m_t=60.3)
    .rotate_axis("X", 90)
    .rotate_axis("Y", 90)
)
m1a = m1.align(b1, ">Y -X >Z", dy=-m_thin, dz=-1)
m1b = m1a.align(b1, "<Z", dz=1)
m2 = m1.rotate_axis("Y", 90)
m2a = m2.align(b1, ">X >Y -Z", dy=-m_thin, dx=-0.4)
m2b = m2a.align(b1, "<X", dx=0.4)
m1ac = m1a.solid_box(y=thick1).align(b1, ">Y", dz=-2)
m1bc = m1b.solid_box(y=thick1).align(b1, ">Y", dz=2)
m2ac = m2a.solid_box(y=thick1).align(b1, ">Y", dx=-2)
m2bc = m2b.solid_box(y=thick1).align(b1, ">Y", dx=2)


@cq_cache
def interna1_obj(fit_internal_depth=True):
    obj = b1h
    obj = obj.union(union_all([m1ac, m1bc, m2ac, m2bc])).cut(
        union_all([m1a, m1b, m2a, m2b])
    )

    obj = obj.cut(c1a)
    c1c = c1b
    if fit_internal_depth:
        internal_depth = 17
        c1c = c1c.cut(c1b.solid_box().translate((0, -(internal_depth - thick1), 0)))
    obj = obj.union(c1c)
    obj = obj.union(union_all([m1ac, m1bc, m2ac, m2bc])).cut(
        union_all([m1a, m1b, m2a, m2b])
    )
    return obj


@cq_cache
def external1_obj(r1=85 / 2, thick=4, pad=10):
    obj = b1h

    outer_frame_pad = 25 - 10.4
    ext_shrink = 20
    b1l = (
        W()
        .box(outer_frame_pad, thick1, inner_height - ext_shrink)
        .align(b1, ":<X <Y -Z")
    )
    b1b = (
        W()
        .box(inner_width - ext_shrink, thick1, outer_frame_pad)
        .align(b1, "<Y -X :<Z")
    )
    b1l1 = b1l.solid_box(y=2, x=2)
    b1l1 = b1l1.align(b1l, ">Y :<X")
    b1b1 = b1b.solid_box(y=2, z=2)
    b1b1 = b1b1.align(b1b, ">Y :<Z -X")
    obj = obj.union(b1l).union(b1b).union(b1l1).union(b1b1)

    putty_thick = 1
    b2l = (
        W()
        .box(thick, outer_depth1, inner_height - ext_shrink)
        .align(b1l, "<X <Z >Y", dx=putty_thick)
    )
    b2b = (
        W()
        .box(inner_width - ext_shrink, outer_depth1, thick)
        .align(b1b, "<X <Z >Y", dz=putty_thick)
    )
    b3l = W().box(*b2l.union(b1l).measure(f"X Y {thick}"))
    b3l1 = b3l.cut(b3l.edges("|Z and <X and >Y").chamfer(18, 12)).align(b2l, ":>X >Y")
    b3l1s = b3l1.repeat(3, z=25)
    b3b = W().box(*b2b.union(b1b).measure(f"{thick} Y Z"))
    b3b1 = b3b.cut(b3b.edges("|X and <Z and >Y").chamfer(12, 18)).align(b2b, ":>Z >Y")
    b3b1s = b3b1.repeat(3, x=25)
    obj = obj.union(b2l).union(b2b).union(b3l1s).union(b3b1s)

    obj = obj.cut(c1a)
    obj = obj.union(c1b)
    obj = obj.union(union_all([m1ac, m1bc, m2ac, m2bc])).cut(
        union_all([m1a, m1b, m2a, m2b])
    )
    return obj


@cq_cache
def external2_obj(r1=r1 + r1_thick + 0.3):
    r1 = r1 + r1_thick
    c1l = 25
    c1_thick = W("XZ").cylinder(c1l, r1 + 2)
    c1 = W("XZ").cylinder(c1l, r1)
    c1a = W("XZ").cylinder(c1l, r1 - r1_thick)
    c1b = c1.cut(c1a)  # .faces(">Y or <Y").shell(-thick)
    c1b_thick = c1_thick.cut(c1a)
    p1 = pipe_connector(r1=r1, thick=r1_thick * 1)
    p1 = p1.rotate_axis("Z", -90).rotate_axis("Y", -90)
    p1 = p1.align(c1b, ":<Y -X -Z", dy=-1e-4)  # dy is a workaround
    c1c = c1b.rotate_axis("X", 90).align(p1, ":<Z <Y", dz=-1e-4)
    obj = c1b_thick.union(p1).union(c1c)

    s1 = W().box(r1_thick, r1 * 2 - 0.4, c1l).align(c1c, ">Y <Z", dy=-0.2)
    obj = obj.union(s1)

    for d in [23, -23]:
        l2 = (r1**2 - d**2) ** 0.5
        s2 = W().box(r1_thick, l2 * 2 - 2, c1l).align(s1, "-Y >X >Z", dx=d)
        obj = obj.union(s2)
        # s3 = W().box(abs(d), r1_thick, c1l).align(s2, "<Y <Z").align(s1, "-X", dx=d / 2)
        # obj = obj.union(s3)

    return obj


def render():
    e1 = external1_obj().export("external1")
    e2 = external2_obj().export("external2")
    e2 = e2.align(e1, ":<Y", dy=-10)
    i1 = interna1_obj(fit_internal_depth=False).export("internal1")
    i1 = i1.rotate_axis("Z", 180).align(e1, ":>Y", dy=10)
    obj = e1.union(e2).union(i1)
    return obj


render().show().export()
