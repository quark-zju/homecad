import math
import os
import cadquery as cq
from functools import reduce, wraps
import inspect

W = Workplane = cq.Workplane


def workplane_method(func):
    """Define method on Workplane object"""
    setattr(W, func.__name__, func)
    return func


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


# based on https://github.com/CadQuery/cadquery-plugins/blob/main/plugins/cq_cache/cq_cache.py
def cq_cache(function):
    """
    This function save the model created by the cached function as a BREP file and
    loads it if the cached function is called several time with the same arguments.

    Note that it is primarly made for caching function with simple types as argument.
    """
    import tempfile, marshal, hashlib, io
    from OCP.TopoDS import TopoDS_Shape

    TEMPDIR_PATH = tempfile.gettempdir()
    CACHE_DIR_NAME = "cq-cache"
    CACHE_DIR_PATH = os.path.join(TEMPDIR_PATH, CACHE_DIR_NAME)
    CQ_TYPES = {
        cq.Shape,
        cq.Solid,
        cq.Shell,
        cq.Compound,
        cq.Face,
        cq.Wire,
        cq.Edge,
        cq.Vertex,
        TopoDS_Shape,
        cq.Workplane,
    }

    os.makedirs(CACHE_DIR_PATH, exist_ok=True)

    def import_brep(f):
        # similar to cq.Shape.importBrep, but skips IsNull check
        from OCP.BRepTools import BRepTools
        from OCP.BRep import BRep_Builder

        s = TopoDS_Shape()
        builder = BRep_Builder()
        ret = BRepTools.Read_s(s, f, builder)
        if ret is False:
            raise ValueError("Could not import BREP")
        return s

    def build_file_path(f, *args, **kwargs):
        """File path for hashed (f, args, kwargs)"""
        # might raise for non-basic types
        v = marshal.dumps((f.__code__, f.__defaults__, f.__kwdefaults__, args, kwargs))
        file_name = hashlib.blake2s(v).hexdigest()
        file_path = os.path.join(CACHE_DIR_PATH, file_name)
        return file_path

    def return_right_wrapper(source, type_name):
        target = next(x for x in CQ_TYPES if x.__name__ == type_name)
        if target is cq.Workplane:
            shape = cq.Shape(source)
            shape = cq.Workplane(obj=shape)
            # This is a no-op, but it works around an issue that
            # obj1.union(obj2) when both objs are returned from the
            # below line, the first obj1 is ignored somehow.
            shape = cq.Workplane().union(shape)
        else:
            shape = target(source)
        return shape

    @wraps(function)
    def wrapper(*args, **kwargs):
        file_path = build_file_path(function, *args, **kwargs)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                v = marshal.load(f)
            shape = import_brep(io.BytesIO(v["brep"]))
            return return_right_wrapper(shape, v["type_name"])
        shape = function(*args, **kwargs)
        shape_type = type(shape)
        if shape_type not in CQ_TYPES:
            raise TypeError(f"cq_cache cannot wrap {shape_type} objects")
        try:
            shape_export = shape.val()
        except AttributeError:
            shape_export = shape
        buf = io.BytesIO()
        shape_export.exportBrep(buf)
        with open(file_path, "wb") as f:
            marshal.dump({"type_name": shape_type.__name__, "brep": buf.getvalue()}, f)
        return shape

    return wrapper


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
    If face is "-X", "-Y", or "-Z", align to the middle.
    """
    for face in faces.split():
        bbox1 = obj1.val().BoundingBox()
        bbox2 = obj2.val().BoundingBox()
        if face.startswith(":"):
            face1 = face2 = face[1:]
            if "<" in face1:
                face1 = face1.replace("<", ">")
            else:
                face1 = face1.replace(">", "<")
        elif face.startswith("-"):
            # select the middle
            face1 = face2 = "<" + face[1:]
            match face[1:]:
                case "X":
                    dx += (bbox2.xlen - bbox1.xlen) / 2
                case "Y":
                    dy += (bbox2.ylen - bbox1.ylen) / 2
                case "Z":
                    dz += (bbox2.zlen - bbox1.zlen) / 2
        else:
            face1 = face2 = face

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
_wanted_key = object()


class ImportDone(StopIteration):
    """`import_part` is done. No need to execute the rest of the code."""

    pass


@workplane_method
def export(obj, part=None, filename=None):
    """Export STL to /tmp, or as `import_part`"""
    if _capturing_stack:
        stack = _capturing_stack[-1]
        wanted = stack.get(_wanted_key)
        _capturing_stack[-1][part] = obj
        if wanted and part == wanted:
            raise ImportDone()
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
    captured = {_wanted_key: part}
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
    except ImportDone:
        pass
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
    assert length > 0
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


@workplane_method
def solid_box(obj, inverse=False):
    b = W().box(*obj.measure()).align(obj, "<X <Y <Z")
    if inverse:
        b = b.cut(obj)
    return b


@cq_cache
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
