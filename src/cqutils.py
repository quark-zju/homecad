import cadquery as cq
from functools import reduce

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
        bbox1 = obj1.faces(face1).val().BoundingBox()
        bbox2 = obj2.faces(face2).val().BoundingBox()
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


@workplane_method
def quick_export(obj, part=None, filename=None):
    """Export STL to /tmp"""
    import os

    if filename is None:
        import inspect

        frame = inspect.stack()[1]
        filename = frame.filename
        if filename.endswith(">"):
            # ex. "<cq_editor-string>". Try to get the filename.
            filename = frame.frame.f_globals["__file__"]

    filename = os.path.basename(filename).rsplit(".", 1)[0]
    if part:
        filename += f"-{part}"
    out_dir = os.getenv("STL_OUT") or os.path.expanduser("~/stl")
    os.makedirs(out_dir, exist_ok=True)
    cq.exporters.export(obj, os.path.join(out_dir, f"{filename}.stl"))


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
def cut_inner_box(obj, face, thickness=1):
    return W(obj.val()).faces(face).shell(-thickness)
