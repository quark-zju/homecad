import math
import os
import cadquery as cq
from functools import reduce
import inspect

W = cq.Workplane


def workplane_method(func):
    """Define method on Workplane object"""
    setattr(W, func.__name__, func)
    return func


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


@workplane_method
def align(obj1, obj2, faces, dx=0, dy=0, dz=0):
    """Align obj1 to obj2 on faces (ex. ">X <Y").
    Return moved obj1.
    If face starts with :, then objects will align like:
        obj1|
            |obj2
    instead of:
        obj1|
        obj2|
    """
    for face in faces.split():
        if face.startswith(":"):
            face1 = face2 = face[1:]
            if "<" in face1:
                face1 = face1.replace("<", ">")
            else:
                face1 = face1.replace(">", "<")
        else:
            face1 = face2 = face
        bbox1 = obj1.val().BoundingBox()
        bbox2 = obj2.val().BoundingBox()

        # Usually, faces(">Y") produces a "thin" (ymin = ymax) bounding box.
        # However, shapes like a cylinder does not have such "thin" faces.
        # So we need to handle them manually.
        def fix_bbox(bbox, face):
            if "<" in face:
                method = min
            elif ">" in face:
                method = max
            if "X" in face:
                bbox.xmin = bbox.xmax = method(bbox.xmin, bbox.xmax)
            elif "Y" in face:
                bbox.ymin = bbox.ymax = method(bbox.ymin, bbox.ymax)
            elif "Z" in face:
                bbox.zmin = bbox.zmax = method(bbox.zmin, bbox.zmax)

        fix_bbox(bbox1, face1)
        fix_bbox(bbox2, face2)

        cdx = cdy = cdz = 0
        if "X" in face:
            cdx = bbox2.xmin - bbox1.xmin
        elif "Y" in face:
            cdy = bbox2.ymin - bbox1.ymin
        else:
            cdz = bbox2.zmin - bbox1.zmin
        obj1 = obj1.translate((cdx, cdy, cdz))
    return obj1.translate((dx, dy, dz))


@workplane_method
def rotate_axis(obj, axis, degree):
    p1 = (0, 0, 0)
    p2 = (int(axis == "X"), int(axis == "Y"), int(axis == "Z"))
    return obj.rotate(p1, p2, degree)


@workplane_method
def repeat(obj, n, x=0, y=0, z=0):
    h = n // 2
    obj = obj.translate((-x * h, -y * h, -z * h))
    objs = [obj]
    for i in range(n - 1):
        obj = obj.translate((x, y, z))
        objs.append(obj)
    return union_all(objs)


_capturing_stack = []


@workplane_method
def export(obj, part=None, filename=None):
    """Export STL to /tmp, or as `import_part`"""
    if _capturing_stack:
        _capturing_stack[-1][part] = obj
        return

    if filename is None:
        frame = inspect.stack()[1]
        filename = frame.filename
        if filename.endswith(">"):
            # ex. "<cq_editor-string>". Try to get the filename.
            filename = frame.frame.f_globals["__file__"]

    filename = os.path.basename(filename).rsplit(".", 1)[0]
    filename = filename.replace("_", "-")
    if part:
        filename += f"-{part}"
    out_dir = os.getenv("STL_OUT") or os.path.expanduser("~/stl")
    os.makedirs(out_dir, exist_ok=True)
    cq.exporters.export(obj, os.path.join(out_dir, f"{filename}.stl"))
    return obj


@workplane_method
def show(obj):
    """Call show_object, and prevent further show_object calls"""
    frame = inspect.stack()[1]
    show_object = frame.frame.f_globals.get("show_object")
    if show_object:
        show_object(obj)
        frame.frame.f_globals["show_object"] = lambda _obj: None
    return obj


def import_part(filename, part=None):
    """Import a part exported by `export` from a script.
    The file is relative to this file's directory.
    """
    captured = {}
    _capturing_stack.append(captured)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        src_full_path = os.path.join(script_dir, filename)
        with open(src_full_path) as f:
            source = f.read()
        code = compile(source, filename, "exec")
        mod = type(os)("__import_part__")
        mod.__file__ = src_full_path
        mod.show_object = lambda _obj: None
        eval(code, mod.__dict__, mod.__dict__)
    finally:
        top = _capturing_stack.pop()
        assert top is captured

    obj = captured.get(part)
    if obj is None:
        parts = list(captured.keys())
        raise ValueError(f"{part=} is missing from {filename}, exported parts: {parts}")

    return obj


@workplane_method
def cut_hexagon(obj, hex_radius=6, wall_thickness=1.4, border=1.4):
    """Cut hexagon on a (thin) board"""

    dx = (3**0.5) * hex_radius + wall_thickness
    dy = 3.0 * hex_radius + (3**0.5) * wall_thickness

    bbox = obj.val().BoundingBox()
    face = sorted([(bbox.xlen, ">X"), (bbox.ylen, ">Y"), (bbox.zlen, ">Z")])[0][-1]
    match face:
        case ">Z":
            xlen, ylen = bbox.xlen, bbox.ylen
        case ">X":
            xlen, ylen = bbox.ylen, bbox.zlen
        case _:
            xlen, ylen = bbox.xlen, bbox.zlen

    ny = int(ylen / dy) + 2
    nx = int(xlen / dx) + 2
    sketch_a = cq.Sketch().rarray(dx, dy, nx, ny).regularPolygon(hex_radius, 6, angle=0)
    sketch_b = sketch_a.moved(cq.Location(cq.Vector(dx / 2, dy / 2, 0)))
    limit_area = cq.Sketch().rect(xlen - border * 2, ylen - border * 2)
    sketch_a = limit_area.face(sketch_a, mode="i")
    limit_area = cq.Sketch().rect(xlen - border * 2, ylen - border * 2)
    sketch_b = limit_area.face(sketch_b, mode="i")
    return obj.faces(face).workplane().placeSketch(sketch_a, sketch_b).cutThruAll()


@workplane_method
def surface_holes(obj, face=">Z", len=10):
    """Find holes in surface). Extend them by len.
    Useful to cut into other adjacent objects.
    """
    sketches = []
    obj_face = obj.faces(face)
    for f in obj_face.vals():
        for w in f.innerWires():
            fw = cq.Face.makeFromWires(w)
            sketch = cq.Sketch(fw).finalize()
            sketches.append(sketch)
    return obj_face.workplane().placeSketch(*sketches).extrude(len)


@workplane_method
def surface_grow(obj, face=">Z", length=10):
    """'extrude' (extend) the surface."""
    obj = W(obj.val())
    sel = obj.faces(face)
    if sel.size() != 1:
        raise ValueError("Selector must resolve to exactly one face")
    vec = sel.workplane().plane.zDir * length
    solid = cq.Solid.extrudeLinear(sel.val(), vec)
    return W(solid)


@workplane_method
def bbox(obj):
    return obj.val().BoundingBox()


@workplane_method
def measure(obj, axis=None):
    bbox = obj.val().BoundingBox()
    match axis and axis.upper():
        case "X":
            return bbox.xlen
        case "Y":
            return bbox.ylen
        case "Z":
            return bbox.zlen
        case _:
            return (bbox.xlen, bbox.ylen, bbox.zlen)


@workplane_method
def cut_inner_box(obj, face, thickness=1):
    return W(obj.val()).faces(face).shell(-thickness)


def connect_obj(
    width, height, thick, kind="male", edge_outline=2, seam_edge=0.16, seam_thick=0.06
):
    assert thick > 0.2
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_obj(w, h, dthick=0):
        return W().box(w, thick + dthick, h).edges("<Y").edges("|Z").chamfer(d, d2)

    b_inner = get_obj(width, height)
    outer_width = width + (edge_outline - d2 / 2) * 2
    outer_height = height + edge_outline
    unprintable = 0.01
    if kind in {1, "male"}:
        b_placeholder = (
            W()
            .box(outer_width, unprintable, unprintable)
            .align(b_inner, "<Z >Y", dz=outer_height - unprintable)
        )
        return b_inner.union(b_placeholder)

    b_outer = W().box(outer_width, thick + edge_outline, outer_height)
    b_inner_for_cut = get_obj(width + seam_edge * 2, height + seam_edge, seam_thick)
    if kind in {2, "cut"}:
        b_placeholder = (
            W()
            .box(outer_width, unprintable, unprintable)
            .align(b_inner_for_cut, "<Z >Y", dz=outer_height - unprintable)
        )
        return b_inner_for_cut.union(b_placeholder)
    b_outer = b_outer.cut(b_inner_for_cut.align(b_outer, "<Z <Y"))
    return b_outer
