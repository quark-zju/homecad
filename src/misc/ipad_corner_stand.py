"""iPad 裸机直立套角，左右各打印一件；纯 b4dcad，单位 mm。

正面由底边低挡唇和外侧窄挡唇组成 L 形包边，背面及外侧挡边较高。
front_lip 为底挡唇高度，side_lip 为正面侧挡唇宽度（0 可关闭）；
两者均须小于实测最窄黑边 bezel_width，并留 bezel_margin。
黑边从机身外沿量到显示区域；侧挡唇高度与背面 back_height 相同。
槽口容量取旧款 Pro 实测 6.57，默认预览 Mini 实测厚度 6.48；
黑边取实测 Pro 6（Mini 9），圆角仅为示意。
先打印 fit_test 手持试配，再确定正式槽宽；不要靠过盈夹紧屏幕。
fit_test 沿用正式模型的壁厚、底厚和挡唇，只缩短套角并裁掉大底座，
用于确认插拔松紧和黑边避让，不能用于验证支撑稳定性。
get_fit_tests 可一次打印窄 / 默认 / 宽三档，槽宽相差 0.2，
底座前缘分别有 1 / 2 / 3 个缺口；默认槽宽为 6.67 / 6.87 / 7.07。
用同样的材料、打印方向和切片设置，手持 iPad 试插，太紧时不要强压。
选中槽宽 W 后，设 clearance=(W-capacity)/2；只改 thickness 不改变槽宽。

thickness 为裸机厚度，clearance 为槽口单侧间隙；front_lip 从机身
底边向上量。左右套角不连接，横放、竖放均可，中央留空便于充电。
槽宽 = capacity + 2 * clearance，与 thickness 无关。用同一对脚适配薄机时，
在背面挡边内侧贴薄硬垫片，表面可覆一层薄胶带保护机身；避免厚软泡棉。
旧款 Pro 无需厚度垫片；Mini 仅差 0.09，可用薄胶带微调，不打印薄片。
默认输出 pro_11_shims / pro_13_shims，分别是 5.3 / 5.1 厚机身用的
一对硬垫片。每片厚度 = capacity - 机身厚度 - shim_tape，默认给
双面胶层留 0.1；装在背面挡边内侧，平放打印后用薄胶带固定。
改 thickness 及 preview_width / height 可预览其他设备，支脚尺寸不变。
rear_pad 为自动计算的垫片加胶层总厚度。沿背面挡边高度贴垫片，
逐层微调到能自然插拔、没有明显晃动；底面可贴薄防滑胶带。
圆角无需仿形：底部和侧面在机身圆角以外接触，grip_width 和
back_height 应大于机身圆角半径。底座平面朝下打印，无需支撑。
背面两条实心三角筋连接背板与底座；brace_size 为外露三角形的
高度及后伸长度，brace_width 为筋厚，brace_size=0 可关闭；试配件不加筋。
base_front / base_back 是从机身厚度中心到桌面支撑边的距离；
默认前伸 30、后伸 60，总深度 90，优先抵抗从屏幕前方施力造成的后倾。
大尺寸 iPad 可加大，抗倾倒和实际配合仍需实物验证。

    b4dcad preview src/misc/ipad_corner_stand.py
    b4dcad stl src/misc/ipad_corner_stand.py ./stl --object fit_test
    b4dcad stl src/misc/ipad_corner_stand.py ./stl --object get_fit_tests
    b4dcad stl src/misc/ipad_corner_stand.py ./stl

导出 left、right、fit_test 和两组薄款 Pro 垫片；show_assembly 为装配预览。
preview_width / height / radius 只用于示意及摆放右脚。
"""

from dataclasses import dataclass, fields, replace
import math

from b4dcad import Solid, cube, is_rendering, polygon, square


@dataclass(frozen=True)
class Parameters:
    thickness: float = 6.48
    capacity: float = 6.57
    shim_tape: float = 0.1
    clearance: float = 0.15
    bezel_width: float = 6.0
    bezel_margin: float = 1.0
    front_lip: float = 4.0
    side_lip: float = 4.0
    back_height: float = 32.0
    grip_width: float = 32.0
    wall: float = 2.4
    base_thickness: float = 3.2
    base_front: float = 30.0
    base_back: float = 60.0
    base_side: float = 5.0
    brace_size: float = 24.0
    brace_width: float = 3.2
    lead_in: float = 0.6
    preview_width: float = 134.8
    preview_height: float = 195.4
    preview_radius: float = 10.0

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{field.name} must be finite and nonnegative")
            if value == 0 and field.name not in (
                "shim_tape",
                "clearance",
                "lead_in",
                "side_lip",
                "brace_size",
            ):
                raise ValueError(f"{field.name} must be positive")
        if self.thickness > self.capacity:
            raise ValueError("Device thickness exceeds the universal slot capacity")
        if max(self.front_lip, self.side_lip) + self.bezel_margin > self.bezel_width:
            raise ValueError(
                "Front and side lips must stay inside the bezel with a margin"
            )
        if self.back_height < self.front_lip:
            raise ValueError("Back support must be at least as high as front lip")
        if self.lead_in >= min(self.wall, self.front_lip):
            raise ValueError("Lead-in must leave material in the wall and front lip")
        half_slot = self.capacity / 2 + self.clearance
        if min(self.base_front, self.base_back) <= half_slot + self.wall:
            raise ValueError("Base must extend beyond both retaining walls")
        if self.brace_size > 0:
            if self.brace_size + self.wall / 2 + self.lead_in > self.back_height:
                raise ValueError("Rear brace must stay below the back support lead-in")
            if half_slot + self.wall + self.brace_size > self.base_back:
                raise ValueError("Rear brace must fit on the existing base")
            if 2 * self.brace_width > self.grip_width:
                raise ValueError("Two rear braces must fit across the back support")
        if self.preview_radius >= min(self.grip_width, self.back_height):
            raise ValueError("Grip and side stop must reach beyond the device corner")
        if 2 * self.preview_radius >= min(self.preview_width, self.preview_height):
            raise ValueError("Preview corner radius is too large")
        if self.bezel_width >= self.preview_radius:
            raise ValueError("Preview bezel must be narrower than its corner radius")
        if self.preview_width <= 2 * (self.grip_width + self.base_side):
            raise ValueError("Preview device is too narrow for two independent feet")

    @property
    def rear_pad(self):
        return self.capacity - self.thickness


def make_foot(p=None, *, right=False):
    """左脚内侧挡面为 X=0，开口朝 +X；右脚关于 YZ 平面镜像。"""
    p = p or Parameters()
    s = p.capacity / 2 + p.clearance
    # 只有底座的竖向外角倒圆；槽底保持平面，以承托机身直边。
    width = p.grip_width + p.wall + 2 * p.base_side
    depth = p.base_front + p.base_back
    radius = min(2.0, p.base_side, width / 4, depth / 4)
    base = (
        square(width - 2 * radius, depth - 2 * radius)
        .offset(radius, "round")
        .extrude(p.base_thickness)
        .move(x=-p.wall - p.base_side + radius, y=-p.base_front + radius)
    )

    shell = cube(p.grip_width + p.wall, 2 * (s + p.wall), p.back_height).move(
        x=-p.wall, y=-s - p.wall, z=p.base_thickness
    )
    # YZ 截面的槽口：前挡边较低，前后顶部均朝槽外退让 45°。
    # 槽口向 +X 贯通，负 X 侧留下整块侧挡。
    slot = (
        polygon(
            [
                (-s, -1),
                (s, -1),
                (s, p.back_height - p.lead_in),
                (s + p.lead_in, p.back_height),
                (s + p.lead_in, p.back_height + 1),
                (-s - p.wall - 1, p.back_height + 1),
                (-s - p.wall - 1, p.front_lip),
                (-s - p.lead_in, p.front_lip),
                (-s, p.front_lip - p.lead_in),
            ]
        )
        .extrude(p.grip_width + 1)
        .rotate(x=90)
        .rotate(z=90)
        .move(z=p.base_thickness)
    )
    if p.side_lip > 0:
        # 保留正面靠外侧的一条窄挡唇；只包住黑边，不缩窄厚度槽。
        front_side = (
            polygon(
                [
                    (-s - p.wall - 1, -1),
                    (-s, -1),
                    (-s, p.back_height + 1),
                    (-s - p.wall - 1, p.back_height + 1),
                ]
            )
            .extrude(p.side_lip)
            .rotate(x=90)
            .rotate(z=90)
            .move(z=p.base_thickness)
        )
        slot = slot - front_side
    foot = base + (shell - slot)
    if p.brace_size > 0:
        rear = s + p.wall
        # 外露部分是实心直角三角筋；向背板内伸入半个壁厚，可靠并体。
        brace = (
            polygon(
                [
                    (rear - p.wall / 2, 0),
                    (rear + p.brace_size, 0),
                    (rear - p.wall / 2, p.brace_size + p.wall / 2),
                ]
            )
            .extrude(p.brace_width)
            .rotate(x=90)
            .rotate(z=90)
            .move(z=p.base_thickness)
        )
        foot = foot + brace + brace.move(x=p.grip_width - p.brace_width)
    return foot.mirror(x=1) if right else foot


def make_fit_test(p=None, *, slot_width=None, marks=0):
    """短套角试片，平底朝下；slot_width 为实际槽宽，缺口不接触机身。"""
    p = p or Parameters()
    if slot_width is not None:
        p = replace(p, clearance=(slot_width - p.capacity) / 2)
    length = min(p.grip_width, max(16, p.preview_radius + 4))
    height = min(p.back_height, max(16, p.preview_radius + 4))
    p = replace(p, grip_width=length, back_height=height, brace_size=0)
    if not isinstance(marks, int) or marks < 0 or 2 * marks > length:
        raise ValueError("Notch count must fit along the test piece")
    s = p.capacity / 2 + p.clearance
    # 裁剪只去掉大底座，挡唇及槽底仍直接使用正式模型的几何。
    clip = cube(length + p.wall + 2, 2 * (s + p.wall + 1), height + p.base_thickness)
    clip = clip.move(x=-p.wall - 1, y=-s - p.wall - 1)
    part = make_foot(p) & clip
    for i in range(marks):
        notch = cube(1, 0.8, p.base_thickness + 1).move(
            x=1 + 2 * i, y=-s - p.wall - 1.1, z=-0.5
        )
        part = part - notch
    return part


def get_fit_tests(p=None):
    """三档槽宽，前缘 1 / 2 / 3 个缺口对应窄 / 默认 / 宽。"""
    p = p or Parameters()
    nominal = p.capacity + 2 * p.clearance
    if nominal - 0.2 < p.capacity:
        raise ValueError("Three-width test requires at least 0.1 mm clearance per side")
    parts = Solid()
    x = 0.0
    for marks, delta in enumerate((-0.2, 0, 0.2), start=1):
        part = make_fit_test(p, slot_width=nominal + delta, marks=marks)
        part = part.align(xmin=x)
        parts = parts + part
        x += part.size().x + 4
    return parts


def make_shims(thickness, p=None):
    """一对背面硬垫片，平放打印；thickness 为设备厚度，含胶层适配。"""
    p = p or Parameters()
    shim = p.capacity - thickness - p.shim_tape
    if not math.isfinite(thickness) or thickness <= 0 or shim <= 0:
        raise ValueError("Device thickness must leave room for shim and tape")
    width = p.grip_width - 4
    height = p.back_height - max(4, p.lead_in * 2)
    if min(width, height) <= 0:
        raise ValueError("Grip and rear support must leave room for shims")
    pad = cube(width, height, shim)
    return pad + pad.move(x=width + 4)


def reference_pads(p):
    """背垫与胶层的装配包络，不导出。"""
    if p.rear_pad <= 0:
        return Solid()
    pad = cube(p.grip_width - 4, p.rear_pad, p.back_height - 4).move(
        x=2,
        y=p.capacity / 2 + p.clearance - p.rear_pad,
        z=p.base_thickness + 2,
    )
    return pad + pad.mirror(x=1).move(x=p.preview_width + 2 * p.clearance)


def reference_tablet(p):
    """圆角示意体；正面浅凹表示显示区域，不用于设备尺寸校验。"""
    r = p.preview_radius
    outline = (
        square(p.preview_width - 2 * r, p.preview_height - 2 * r)
        .offset(r, "round")
        .move(x=r, y=r)
    )
    body = outline.extrude(p.thickness)
    screen = outline.offset(-p.bezel_width).extrude(0.2).move(z=p.thickness - 0.1)
    return (
        (body - screen)
        .rotate(x=90)
        .move(x=p.clearance, y=(p.thickness - p.rear_pad) / 2, z=p.base_thickness)
    )


if is_rendering():
    settings = Parameters()
    left = make_foot(settings)
    right = make_foot(settings, right=True).move(
        x=settings.preview_width + 2 * settings.clearance
    )
    pro_11_shims = make_shims(5.3, settings).move(y=55)
    pro_13_shims = make_shims(5.1, settings).move(y=90)
    fit_test = make_fit_test(settings).move(y=-65)
    show_assembly = left + right + reference_tablet(settings) + reference_pads(settings)
