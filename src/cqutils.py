import cadquery as cq
from functools import reduce


def union_all(objs):
    return reduce(lambda a, b: a.union(b), filter(None, objs))


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


def rotate_axis(obj, axis, degree):
    p1 = (0, 0, 0)
    p2 = (int(axis == "X"), int(axis == "Y"), int(axis == "Z"))
    return obj.rotate(p1, p2, degree)


def repeat(obj, n, x=0, y=0, z=0):
    h = n // 2
    obj = obj.translate((-x * h, -y * h, -z * h))
    objs = [obj]
    for i in range(n - 1):
        obj = obj.translate((x, y, z))
        objs.append(obj)
    return union_all(objs)


W = cq.Workplane
