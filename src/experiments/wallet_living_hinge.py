"""折叠卡包的 living hinge 试片，单位 mm；平底朝下，无需支撑。

四件分别比较薄片厚度 0.4/0.6 与自由弯曲段长 10/14；Y 方向为铰链轴。
两端底板厚 1.2，凸台高 1.6，模拟每页两张卡的厚度，不用于实际装卡。
凸台朝内对折，检查能否合拢、回弹、发白和开裂；再测试反向折叠。
每种材料分别记录弯折次数和合拢保持后的变化，不预设耐久寿命。
建议固定 0.2 层高（含首层）、实心打印；薄片填充走线沿 X 跨越铰链。
0.4 薄片是有意的薄壁实验，切片预览须确认连续两层，避免筏层和自适应层高。
薄片下表面保持平整，上表面用 2 mm 长斜坡连接底板；不夹入铝箔。
"""

import math

from b4dcad import cube, polygon


def hinge_coupon(thickness=0.4, span=10.0, width=24.0):
    """两端为 22 mm 长的握持板，span 只计等厚薄片段，不含斜坡。"""
    if not all(math.isfinite(v) for v in (thickness, span, width)):
        raise ValueError("尺寸必须为有限数")
    if not 0 < thickness < 1.2 or span <= 0 or width <= 4:
        raise ValueError("薄片厚度须介于 0 和 1.2，弯曲段长须为正，宽须大于 4")
    paddle = 22.0
    floor = 1.2
    ramp = 2.0
    total = 2 * paddle + span
    part = (
        polygon(
            [
                (0, 0),
                (total, 0),
                (total, floor),
                (paddle + span + ramp, floor),
                (paddle + span, thickness),
                (paddle, thickness),
                (paddle - ramp, floor),
                (0, floor),
            ]
        )
        .extrude(width)
        .rotate(x=90)
        .move(y=width)
    )
    for x in (2.0, paddle + span + 4.0):
        part += cube(paddle - 6, width - 4, 1.61).move(x=x, y=2, z=floor - 0.01)
    return part


t04_span10 = hinge_coupon(0.4, 10)
t04_span14 = hinge_coupon(0.4, 14).move(x=66)
t06_span10 = hinge_coupon(0.6, 10).move(y=32)
t06_span14 = hinge_coupon(0.6, 14).move(x=66, y=32)
