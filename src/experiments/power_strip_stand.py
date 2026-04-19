from cqutils import *

W = Workplane()

# stand for j5create - 4-Outlet/3-USB-A/1-USB-C 500J Smart Matter Enabled Surge Protector Power Strip


def render():
    y = 30
    z = 100
    x = 100
    b1 = W.box(x, y + 6, z + 10)
    b2 = W.box(x, y, 10).align(b1, ">Z")

    h = 100
    t1 = (
        Workplane("YZ")
        .polyline(
            [
                (0, 0),  # 左下
                (y + 30, 0),  # 右下
                (y + 6, h),  # 右上
                (0, h),  # 左上
            ]
        )
        .close()
        .extrude(100)
    ).align(b1, "<Z <X <Y")

    o = b1.cut(b2).union(t1)
    return o


render().export().show()
