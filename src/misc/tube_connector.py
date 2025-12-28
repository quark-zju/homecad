from cqutils import *
import magnet


@cq_cache
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


def render(r1=85 / 2, thick=4, pad=10):
    m1 = (
        magnet.magnet_3_10_60(hole_depth=0, c1a=0.01, c1b=0.01, m_h=3)
        .rotate_axis("X", 90)
        .rotate_axis("Y", 90)
    )
    inner_width = 90
    inner_height = 100
    outer_depth1 = 22
    thick1 = 4
    b1 = W().box(inner_width, thick1, inner_height)
    b1h = (
        b1.edges("|Y")
        .fillet(3)
        .faces("<Y")
        .workplane()
        .rect(inner_width - 12, inner_height - 12)
        .vertices()
        .cboreHole(3, 7, 1.4)  # for tag pins
    )
    obj = b1h
    m_thin = 0.4
    m1a = m1.align(b1, ">Y -X >Z", dy=-m_thin, dz=-0.8)
    m1b = m1a.align(b1, "<Z", dz=0.8)
    obj = obj.cut(m1a).cut(m1b)
    # NOTE: Use "pause" to insert magnets

    outer_frame_pad = 25
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
    obj = obj.union(b1l).union(b1b)

    putty_thick = 1
    b2 = (
        W()
        .box(thick, outer_depth1, inner_height - ext_shrink)
        .align(b1l, "<X <Z >Y", dx=putty_thick)
    )
    b3 = (
        W()
        .box(inner_width - ext_shrink, outer_depth1, thick)
        .align(b1b, "<X <Z >Y", dz=putty_thick)
    )
    b2u = W().box(*b2.union(b1l).measure(f"X Y {thick}"))
    b2u1 = b2u.cut(b2u.edges("|Z and <X and >Y").chamfer(16)).align(b2, ":>X >Y")
    b2u1s = b2u1.repeat(3, z=25)
    b3u = W().box(*b3.union(b1b).measure(f"{thick} Y Z"))
    b3u1 = b3u.cut(b3u.edges("|X and <Z and >Y").chamfer(16)).align(b3, ":>Z >Y")
    b3u1s = b3u1.repeat(3, x=25)
    obj = obj.union(b2).union(b3).union(b2u1s).union(b3u1s)

    c1l = 35
    r1_thick = 2
    r1 = r1 + r1_thick
    c1 = W("XZ").cylinder(c1l, r1).align(b1, ":<Y")
    c1a = W("XZ").cylinder(c1l + thick1, r1 - r1_thick).align(b1, ">Y")
    obj = obj.cut(c1a)
    c1b = c1.cut(c1a)  # .faces(">Y or <Y").shell(-thick)
    obj = obj.union(c1b)
    if False:
        p1 = pipe_connector(r1=r1, thick=r1_thick)
        p1 = p1.rotate_axis("Z", -90).rotate_axis("Y", -90)
        p1 = p1.align(c1b, ":<Y <X <Z", dy=-1e-4)  # dy is a workaround
        c1c = c1b.rotate_axis("X", 90).align(p1, ":<Z <Y", dz=-1e-4)
        c1d = c1c.align(c1c, ":<Z")
        obj = obj.union(c1b).union(p1).union(c1c).union(c1d)
        b3b = W().box(20, c1l + r1_thick, thick).align(b1b, "-X <Z :<Y", dz=putty_thick)
        obj = obj.union(b3b)

    m1ac = m1a.solid_box(y=m_thin).align(b1, ">Y", dz=-2)
    m1bc = m1b.solid_box(y=m_thin).align(b1, ">Y", dz=2)
    obj = obj.union(m1ac).union(m1bc)

    return obj


render().show().export()
