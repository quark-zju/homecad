"""卡包角轴与磁铁适配试片，单位 mm，所有导出件按打印朝向放置。

裸回形针轴径 0.8、长约 16；切口磨平，先用 pin_gauge 的三个通孔试配。
pin_gauge 沿 +X 孔径依次 1.0/1.1/1.2，孔长与旋转臂轴套相同。
默认转动孔径 1.1；若需改变，修改 BEARING_DIAMETER 后重新生成。
打印 base 一件、rotor 两件、cap 一件，平底朝下，不用支撑。
先叠两臂、穿轴，再装顶盖；顶盖定位柱插入底座立柱孔，干装验证后
只在立柱顶面胶粘顶盖，不给轴套上胶。此为受立柱限位的摆动试片，非全周旋转。
每臂轴套高 6.4，用来测试长轴支承和晃动，不代表最终钱包单层厚度。
轴底到顶盖内顶留 16.2，可容纳 15.8–16.0 长的轴；每处轴向间隙 0.3。
cap 导出时孔朝上，装配时翻面；show_assembly 仅为装配预览。

magnet_gauge 沿 +X 三孔径依次 5.12/5.22/5.32，均为直径余量，非单边余量。
磁铁实测直径 5.02、高 2.58；孔深 2.8，底部有顶出孔，避免试配后取不出。
适配成功后最终磁铁采用胶粘固定，装前核对配对磁极；此处只测试孔位，不含磁吸闭合机构。
"""

from b4dcad import cube, cylinder

PIN_DIAMETER = 0.8
PIN_LENGTH = 16.0
BEARING_DIAMETER = 1.1
MAGNET_DIAMETER = 5.02
MAGNET_HEIGHT = 2.58

_BASE_FLOOR = 0.8
_BASE_TOP = 1.6
_ROTOR_HEIGHT = 6.4
_AXIAL_GAP = 0.3
_ROTOR_Z = _BASE_TOP + _AXIAL_GAP
_SECOND_Z = _ROTOR_Z + _ROTOR_HEIGHT + _AXIAL_GAP
_CAP_BOTTOM = _SECOND_Z + _ROTOR_HEIGHT + _AXIAL_GAP
_CAP_ROOF = _BASE_FLOOR + PIN_LENGTH + 0.2
_CAP_TOP = _CAP_ROOF + 1.2


def _bore(diameter, bottom, top):
    return cylinder(h=top - bottom, r=diameter / 2, fn=64).move(z=bottom)


def pivot_base():
    """立柱顶部孔与顶盖小柱定位；轴孔底部保留 0.8 塑料。"""
    part = cube(20, 12, 1.2).move(x=-10, y=-6)
    part += cylinder(h=_BASE_TOP, r=3, fn=64)
    part += cube(4, 8, _CAP_ROOF).move(x=-9, y=-4)
    part -= _bore(BEARING_DIAMETER, _BASE_FLOOR, _BASE_TOP + 0.1)
    part -= _bore(2.6, _CAP_ROOF - 1.3, _CAP_ROOF + 0.1).move(x=-7)
    return part


def pivot_rotor():
    """轴套与握持臂一体，握持臂平放在热床上。"""
    part = cylinder(h=_ROTOR_HEIGHT, r=3, fn=64)
    part += cube(20, 6, 1.2).move(y=-3)
    part += cylinder(h=1.2, r=3, fn=64).move(x=20)
    return part - _bore(BEARING_DIAMETER, -0.1, _ROTOR_HEIGHT + 0.1)


def pivot_cap():
    """返回装配姿态，导出前翻转，使轴孔和定位柱均朝上。"""
    part = cube(10, 8, 1.2).move(x=-10, y=-4, z=_CAP_ROOF)
    part += cylinder(h=_CAP_TOP - _CAP_BOTTOM, r=3, fn=64).move(z=_CAP_BOTTOM)
    part -= _bore(BEARING_DIAMETER, _CAP_BOTTOM - 0.1, _CAP_ROOF)
    # 与顶板重叠，避免仅共面连接产生独立壳体。
    part += cylinder(h=1.11, r=1.1, fn=48).move(x=-7, z=_CAP_ROOF - 1.1)
    return part


def pin_hole_gauge():
    part = cube(30, 10, _ROTOR_HEIGHT)
    for x, diameter in zip((5, 15, 25), (1.0, 1.1, 1.2)):
        part -= _bore(diameter, -0.1, _ROTOR_HEIGHT + 0.1).move(x=x, y=5)
    return part


def magnet_hole_gauge():
    floor = 0.8
    depth = MAGNET_HEIGHT + 0.22
    part = cube(30, 10, floor + depth)
    for x, allowance in zip((5, 15, 25), (0.1, 0.2, 0.3)):
        part -= _bore(MAGNET_DIAMETER + allowance, floor, floor + depth + 0.1).move(
            x=x, y=5
        )
        part -= _bore(2, -0.1, floor + 0.1).move(x=x, y=5)
    return part


base = pivot_base()
rotor = pivot_rotor().move(x=30)
cap = pivot_cap().rotate(x=180).align(zmin=0).move(x=75, y=4)
pin_gauge = pin_hole_gauge().move(x=-10, y=16)
magnet_gauge = magnet_hole_gauge().move(x=28, y=16)

show_assembly = (
    pivot_base()
    + pivot_rotor().rotate(z=-25).move(z=_ROTOR_Z)
    + pivot_rotor().rotate(z=35).move(z=_SECOND_Z)
    + pivot_cap()
).move(y=48)
