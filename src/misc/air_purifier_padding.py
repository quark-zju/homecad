"""净化器可拆转角 padding：原十二块板不变，同一件打印两份用于左上、右下。

沿用箱体坐标：X 为宽、Z 为高、Y 为前后深度。顶部和右侧整面同时平移
X +5、Z +3.2；底部和左侧不动。左下、右上仍直接连接，另两角加转接件。
⅝″ 与 ½″ 相差 3.175 mm，补高取整为 3.2；原净高 496.2 变成 499.4，
对 19⅝″（498.475 mm）滤网的高度总余量为 0.925，并非原来的 1.2。
净宽为 501.2；较小滤网可用胶带和可拆垫片定位。

母槽只接住原公榫下部 3.2 mm，原榫的其余部分留在箱内；外侧延伸部
与原底板底面接壤、与偏移后的竖板外表面齐平。新公榫沿用 0.8 填胶倒角。
前后各 15 mm 滤网区清空台阶，不补局部限位条，由四周胶带封住。
打印件以外侧面朝下，最高 10 mm；按原方式侧滑装配，胶粘密封。
拆掉 padding 后原件可恢复原箱体；胶粘后的拆卸仍需清除胶层。
show_* 为装配/局部试片预览，不导出；corner_padding 打印两份。
"""

import math

from b4dcad import polygon, square, union

import air_purifier_box as box


def build_corner_padding(d, expansion=3.2, outward=5.0):
    """返回右下转接件的装配坐标实体，不改变原模型。

    expansion 是整框净高度增量，两件位于对角，不将其除以二。
    outward 是整框净宽度增量；至少错开一个板厚，避免新旧榫共用空间。
    """
    d.validate()
    if not math.isfinite(expansion) or not 0.5 <= expansion < d.thickness:
        raise ValueError("补高须至少 0.5 mm 且小于板厚，供部分母槽接合试验")
    if not math.isfinite(outward) or outward < d.thickness:
        raise ValueError("向外错位须至少为一个板厚，错开新旧燕尾")
    h, t = d.span, d.thickness
    # X/Z 截面：左阶贴住原底板顶面，右阶补平底面并延伸到新竖板外表面。
    profile = polygon(
        [
            (h, 0),
            (h + t, 0),
            (h + t, -t),
            (h + outward + t, -t),
            (h + outward + t, expansion),
            (h, expansion),
        ]
    )
    body = profile.extrude(d.depth).rotate(x=90).move(y=d.depth)
    socket = (
        box._tabs(
            d,
            thickness=t + 2 * d.joint_clearance,
            clearance=d.joint_clearance,
            depth=t,
        )
        .rotate(y=-90)
        .move(x=h + t + d.joint_clearance)
    )
    body -= socket
    # 复用原公榫，保留朝箱内的填胶倒角；原底板变换到装配坐标时下移了 t。
    body += box._corner_males(d)[0].move(x=outward, z=expansion - t)
    # 原榫只在中部 Y 区域。滤网两端不保留高于原板面的台阶，否则会挡住滤网角。
    for y in (0, d.depth - d.filter_capture):
        body -= square(outward, d.filter_capture).move(x=h, y=y).extrude(expansion)
    return body.as_original().simplify(1e-6)


def opposite_corner(part, d, expansion=3.2, outward=5.0):
    """右下件绕 Y 旋转半圈成为左上件，保持前后滤网端面不变。"""
    return part.rotate(y=180).move(x=d.span + outward, z=d.span + expansion)


def expanded_frame(parts, expansion=3.2, outward=5.0):
    """只刚性平移顶部、右侧，不缩放或重建任何已打印件。"""
    return {
        name: (
            part.move(x=outward, z=expansion)
            if name.startswith(("top_", "right_"))
            else part
        )
        for name, part in parts.items()
    }


dimensions = box.BoxDimensions()
expansion = 3.2
outward = 5.0
_padding = build_corner_padding(dimensions, expansion, outward)
_opposite = opposite_corner(_padding, dimensions, expansion, outward)
_frame = expanded_frame(box._assembled, expansion, outward)
_fans = expanded_frame(box._fans, expansion, outward)

# 外表面朝打印平台，连续的 5 mm 外壁先打印，再长出部分母槽所在的内阶。
corner_padding = _padding.rotate(y=90).align(xmin=0, ymin=0, zmin=0)
show_padding_pair = box._preview_group([_padding, _opposite])
show_frame = box._preview_group([*_frame.values(), _padding, _opposite])
show_with_fans = box._preview_group([show_frame, *_fans.values()])

# 前端局部显示一处燕尾及滤网让位；方便查看配合，未修改原板实体。
_crop = (
    square(26 + outward, dimensions.depth / 4 + 12)
    .extrude(24)
    .move(x=dimensions.span - 13, z=-dimensions.thickness)
)
_bottom = union(p for n, p in _frame.items() if n.startswith("bottom_")) & _crop
_right = union(p for n, p in _frame.items() if n.startswith("right_")) & _crop
show_corner_assembled = box._preview_group([_bottom, _padding & _crop, _right])
show_corner_exploded = box._preview_group(
    [_bottom, (_padding & _crop).move(x=15), _right.move(x=30)]
)

# 实心占位覆盖滤网插入的 15 mm 深度，供检查前后两个矩形净空。
_size = 19.625 * 25.4
_filter_x = (dimensions.span + outward - _size) / 2
_filter_z = (dimensions.span + expansion - _size) / 2
_filters = [
    square(_size, dimensions.filter_capture)
    .extrude(_size)
    .move(x=_filter_x, y=y, z=_filter_z)
    for y in (0, dimensions.depth - dimensions.filter_capture)
]
show_filter_fit = box._preview_group([show_frame, *_filters])
