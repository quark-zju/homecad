import inspect
import math
import os
import typing
from functools import reduce, wraps

import cadquery as cq

Workplane = cq.Workplane


def workplane_method(func):
    """Define method on Workplane object"""
    # for compat, but not for typecheck
    setattr(cq.Workplane, func.__name__, func)
    return func


def union_all(objs):
    """Union all non-empty objects in order.

    Args:
        objs: Iterable of solids/workplanes; falsy items are ignored.
    """
    if not objs:
        return W()
    return reduce(lambda a, b: a.union(b), filter(None, objs))


# based on https://github.com/CadQuery/cadquery-plugins/blob/main/plugins/cq_cache/cq_cache.py
def cq_cache(function):
    """
    This function save the model created by the cached function as a BREP file and
    loads it if the cached function is called several time with the same arguments.

    Note that it is primarly made for caching function with simple types as argument.
    """
    import hashlib
    import io
    import marshal
    import tempfile

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
        from OCP.BRep import BRep_Builder
        from OCP.BRepTools import BRepTools

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
            cast = getattr(target, "cast") or target
            shape = cast(source)
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
        if shape_type is W:
            shape_type = cq.Workplane
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
def align(obj1, obj2=None, faces="", dx: float = 0, dy: float = 0, dz: float = 0):
    """Align obj1 to obj2 on faces (ex. ">X <Y").
    Return moved obj1.
    If face starts with :, then objects will align like:
        obj1|
            |obj2
    instead of:
        obj1|
        obj2|
    If face is "-X", "-Y", or "-Z", align to the middle.
    faces can also be a list like ["-X", ">Y"].

    Args:
        obj1: Object to move.
        obj2: Target object to align to.
        faces: Face selector string/list, like ">X <Y", ":>X", or "-Z".
        dx: Extra X translation after face alignment.
        dy: Extra Y translation after face alignment.
        dz: Extra Z translation after face alignment.
    """
    if obj2 is not None:
        if isinstance(faces, str):
            faces = faces.split()
        for face in faces:
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
                else:
                    raise ValueError(f"fix_bbox: {face=} must have '>' or '<'")
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
    """Rotate around a global axis.

    Args:
        obj: Object to rotate.
        axis: One of "X", "Y", "Z".
        degree: Rotation angle in degrees.
    """
    p1 = (0, 0, 0)
    p2 = (int(axis == "X"), int(axis == "Y"), int(axis == "Z"))
    return obj.rotate(p1, p2, degree)


@workplane_method
def repeat(obj, n, x=0, y=0, z=0):
    """Create repeated copies with a fixed translation step.

    Args:
        obj: Source object to copy.
        n: Number of copies.
        x: Step distance on X for each copy.
        y: Step distance on Y for each copy.
        z: Step distance on Z for each copy.
    """
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
def export(obj, part=None, filename=None, print_from_face="<Z"):
    """Export STL, or capture part during import_part execution.

    Args:
        obj: Object to export.
        part: Optional part name suffix in output filename.
        filename: Source script path; auto-detected when None.
        print_from_face: Face to place on print bed, one of <Z/>Z/<X/>X/<Y/>Y.
    """
    match print_from_face:
        case "<Z":
            pass
        case ">Z":
            obj = obj.rotate_axis("Y", 180)  # or "X"
        case ">X":
            obj = obj.rotate_axis("Y", 90)
        case "<X":
            obj = obj.rotate_axis("Y", -90)
        case ">Y":
            obj = obj.rotate_axis("X", -90)
        case "<Y":
            obj = obj.rotate_axis("X", 90)
        case _:
            raise ValueError(f"unknown {print_from_face=}")
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

    Args:
        filename: Relative script path under src.
        part: Named part passed to export(part=...); None means default export.
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
    """Cut a hex pattern from the thinnest face of a board-like object.

    Args:
        obj: Target solid.
        hex_radius: Radius of each hex cell.
        wall_thickness: Gap between cells.
        border: Solid margin kept around outer edge.
    """

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
    """Find holes on a surface and extend them by len.
    Useful to cut into other adjacent objects.

    Args:
        obj: Source solid containing hole boundaries.
        face: Face selector to read hole wires from.
        len: Extrusion length for hole solids.
    """
    sketches = []
    obj_face = obj.faces(face)

    # 用第一个 face 建立基准 plane
    f0 = obj_face.val()
    plane = cq.Workplane().newObject([f0]).workplane().plane

    for f in obj_face.vals():
        for w in f.innerWires():
            fw = cq.Face.makeFromWires(w)
            sketch = cq.Sketch(fw).finalize()
            sketches.append(sketch)
    wp = W(plane)
    return W(wp.placeSketch(*sketches).extrude(len).val())


@workplane_method
def surface_grow(obj, face=">Z", length=10, skip_parts=None):
    """Extend one selected face into a new solid.

    Args:
        obj: Source solid.
        face: Face selector; must resolve to exactly one face.
        length: Extrusion distance.
        skip_parts: set of indexes to skip, e.g. {0,1,2}
    """
    assert length > 0
    obj = W(obj.val())
    sel = obj.faces(face)

    if sel.size() == 0:
        raise ValueError("No face selected")

    objs = []

    vec = sel.workplane().plane.zDir * length
    for i, val in enumerate(sel.vals()):
        if skip_parts and i in skip_parts:
            continue
        solid = cq.Solid.extrudeLinear(val, vec)
        objs.append(W(solid))

    return union_all(objs)


@workplane_method
def bbox(obj):
    """Return CadQuery BoundingBox for quick size/position checks.

    Args:
        obj: Source object.
    """
    return obj.val().BoundingBox()


@workplane_method
def measure(obj, axis: str | float | None = None):
    """Measure object size by axis.

    axis can be "X", "Y", "Z", "X Y Z", or a numeric string.

    Args:
        obj: Source object.
        axis: Axis selector, axis list, or numeric literal.
    """
    bbox = obj.val().BoundingBox()
    if isinstance(axis, float):
        try:
            return float(axis)
        except ValueError:
            pass
    elif axis is None:
        return (bbox.xlen, bbox.ylen, bbox.zlen)
    elif isinstance(axis, str):
        match axis.upper():
            case "X":
                return bbox.xlen
            case "Y":
                return bbox.ylen
            case "Z":
                return bbox.zlen
            case _:
                return [measure(obj, a) for a in axis.split()]
    else:
        raise TypeError(f"unexpected {axis=}")


@workplane_method
def cut_inner_box(obj, face, thickness=1):
    """Shell from a selected face to make a hollow box-like body (shell: 抽壳).

    Args:
        obj: Source solid.
        face: Face selector where shell starts.
        thickness: Wall thickness.
    """
    return W(obj.val()).faces(face).shell(-thickness)


@workplane_method
def solid_box(obj, inverse=False, x=None, y=None, z=None, dx=0, dy=0, dz=0):
    """Build a box aligned to obj, with optional size delta and inverse cut.

    Args:
        obj: Reference object.
        inverse: If True, subtract obj from the generated box.
        x: Absolute X size override.
        y: Absolute Y size override.
        z: Absolute Z size override.
        dx: Extra X size added to x or measured x.
        dy: Extra Y size added to y or measured y.
        dz: Extra Z size added to z or measured z.
    """
    mx, my, mz = obj.measure()
    b = W().box((x or mx) + dx, (y or my) + dy, (z or mz) + dz).align(obj, "-X -Y -Z")
    if inverse:
        b = b.cut(obj)
    return b


def sector(radius=10, thick=2, angle=90):
    """Create a revolved sector ring from an XZ profile.

    Args:
        radius: Outer radius.
        thick: Radial thickness.
        angle: Sweep angle in degrees.
    """
    return (
        W("XZ")
        .moveTo(radius, 0)
        .lineTo(radius, thick)
        .lineTo(0, thick)
        .lineTo(0, 0)
        .close()
        .revolve(angle)
    )


@cq_cache
def connect_obj(
    width,
    height,
    thick,
    kind="male",
    edge_outline=2,
    seam_edge=0.16,
    seam_thick=0.06,
    placeholder=True,
):
    """Create cached male/female connector solids with print-friendly chamfers (倒角).

    Args:
        width: Inner connector width.
        height: Inner connector height.
        thick: Connector body thickness.
        kind: "male", "female", or "cut".
        edge_outline: Outer frame expansion.
        seam_edge: XY clearance for mating parts.
        seam_thick: Y thickness clearance for cut/female shape.
        placeholder: Add a tiny top marker for slicing/placement.
    """
    assert thick > 0.2
    d = thick - 0.2
    d2 = d * math.tan(math.radians(30))

    def get_obj(w, h, dthick: float = 0):
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
        return union_all([b_inner, placeholder and b_placeholder])

    b_outer = W().box(outer_width, thick + edge_outline, outer_height)
    b_inner_for_cut = get_obj(width + seam_edge * 2, height + seam_edge, seam_thick)
    if kind in {2, "cut"}:
        b_placeholder = (
            W()
            .box(outer_width, unprintable, unprintable)
            .align(b_inner_for_cut, "<Z >Y", dz=outer_height - unprintable)
        )
        return union_all([b_inner_for_cut, placeholder and b_placeholder])
    b_outer = b_outer.cut(b_inner_for_cut.align(b_outer, "<Z <Y"))
    return b_outer


@cq_cache
def hollow_box(size=10, thickness=0.0001):
    """Create a 6-face frame by intersecting three through-cut boxes (intersect: 求交).

    Args:
        size: Outer cube size.
        thickness: Wall thickness of the frame.
    """
    hole_size = size - (thickness * 2)
    b = W("XY").box(size, size, size)
    b1 = b.faces("Z").workplane().rect(hole_size, hole_size).cutThruAll()
    b2 = b.faces("X").workplane().rect(hole_size, hole_size).cutThruAll()
    b3 = b.faces("Y").workplane().rect(hole_size, hole_size).cutThruAll()
    b = b1.intersect(b2).intersect(b3)
    return b


def trapezoid(x, y, z, dx1=None, dx2=None, degree=30):
    """Extrude a vertical trapezoid profile.

    By default dx1/dx2 follow degree as printable side slope (slope: 斜度).

    Args:
        x: Top edge width.
        y: Trapezoid height in sketch plane.
        z: Extrusion depth.
        dx1: Left-side bottom expansion.
        dx2: Right-side bottom expansion; defaults to dx1.
        degree: Slope-derived expansion angle when dx is omitted.
    """
    if dx1 is None:
        # 取 30 度 (可打印梯度)
        dx1 = y * math.tan(math.radians(degree))
    elif dx2 is None and dx1 == 0:
        dx2 = y * math.tan(math.radians(degree))
    if dx2 is None:
        dx2 = dx1
    coordinates = [
        (-dx1 - x / 2, 0),
        (x / 2 + dx2, 0),
        (x / 2, y),
    ]
    if x > 0:
        coordinates.append((-x / 2, y))
    return W("XY").polyline(coordinates).close().extrude(z)


if typing.TYPE_CHECKING:

    class W(cq.Workplane):
        """Wrapper class of Workplane, to make pyright understand the @workplane_method patches"""

        # [[[cog
        # import ast
        # from pathlib import Path
        #
        # src = Path("cqutils.py").read_text()
        # mod = ast.parse(src)
        #
        # def _is_workplane_method(node):
        #     for dec in node.decorator_list:
        #         if isinstance(dec, ast.Name) and dec.id == "workplane_method":
        #             return True
        #     return False
        #
        # def _fmt_arg(arg, default=None):
        #     s = arg.arg
        #     if arg.annotation:
        #         s += f": {ast.unparse(arg.annotation)}"
        #     if default is not None:
        #         s += f"={ast.unparse(default)}"
        #     return s
        #
        # def _fmt_signature(fn):
        #     args = fn.args
        #     items = []
        #     call_items = []
        #
        #     pos = args.posonlyargs + args.args
        #     pos = pos[1:]  # skip obj/self arg
        #     defaults = [None] * (len(pos) - len(args.defaults)) + list(args.defaults)
        #     for i, arg in enumerate(pos):
        #         items.append(_fmt_arg(arg, defaults[i]))
        #         call_items.append(arg.arg)
        #
        #     if args.vararg:
        #         items.append("*" + _fmt_arg(args.vararg))
        #         call_items.append("*" + args.vararg.arg)
        #     elif args.kwonlyargs:
        #         items.append("*")
        #
        #     for i, arg in enumerate(args.kwonlyargs):
        #         items.append(_fmt_arg(arg, args.kw_defaults[i]))
        #         call_items.append(f"{arg.arg}={arg.arg}")
        #
        #     if args.kwarg:
        #         items.append("**" + _fmt_arg(args.kwarg))
        #         call_items.append("**" + args.kwarg.arg)
        #
        #     method_args = ", ".join(items)
        #     if method_args:
        #         method_args = ", " + method_args
        #     call_args = ", ".join(call_items)
        #     return method_args, call_args
        #
        # funcs = [
        #     node
        #     for node in mod.body
        #     if isinstance(node, ast.FunctionDef) and _is_workplane_method(node)
        # ]
        # indent = " " * 8
        # for fn in funcs:
        #     method_args, call_args = _fmt_signature(fn)
        #     cog.outl(f"{indent}def {fn.name}(self{method_args}):")
        #     cog.outl(f"{indent}    return {fn.name}(self{', ' if call_args else ''}{call_args})")
        #     cog.outl("")
        # ]]]
        def align(
            self, obj2=None, faces="", dx: float = 0, dy: float = 0, dz: float = 0
        ):
            return align(self, obj2, faces, dx, dy, dz)

        def rotate_axis(self, axis, degree):
            return rotate_axis(self, axis, degree)

        def repeat(self, n, x=0, y=0, z=0):
            return repeat(self, n, x, y, z)

        def export(self, part=None, filename=None, print_from_face="<Z"):
            return export(self, part, filename, print_from_face)

        def show(self):
            return show(self)

        def cut_hexagon(self, hex_radius=6, wall_thickness=1.4, border=1.4):
            return cut_hexagon(self, hex_radius, wall_thickness, border)

        def surface_holes(self, face=">Z", len=10):
            return surface_holes(self, face, len)

        def surface_grow(self, face=">Z", length=10, skip_parts=None):
            return surface_grow(self, face, length, skip_parts)

        def bbox(self):
            return bbox(self)

        def measure(self, axis: str | float | None = None):
            return measure(self, axis)

        def cut_inner_box(self, face, thickness=1):
            return cut_inner_box(self, face, thickness)

        def solid_box(self, inverse=False, x=None, y=None, z=None, dx=0, dy=0, dz=0):
            return solid_box(self, inverse, x, y, z, dx, dy, dz)

        # [[[end]]]

else:
    W = cq.Workplane
