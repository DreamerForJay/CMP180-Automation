"""Build and render a detailed exterior reference model of the R&S CMP180."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "cmp180_3d"
RENDER_DIR = ASSET_DIR / "renders"

# Blender 場景以公尺為單位；以下尺寸由 2 HU × 19 吋規格與照片比例估算。
CHASSIS_W = 0.465
CHASSIS_D = 0.555
BODY_H = 0.089
FOOT_H = 0.017
FRONT_Y = -CHASSIS_D / 2
REAR_Y = CHASSIS_D / 2


def material(name: str, color: tuple[float, float, float, float], metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def rounded_box(name, location, scale, mat, bevel=0.003, collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Edge softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    assign(obj, mat)
    if collection:
        for current in list(obj.users_collection):
            current.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def cylinder(name, location, radius, depth, mat, rotation=(math.pi / 2, 0, 0), vertices=48):
    # Blender 圓柱預設沿 Z 軸；前後面板接頭需旋轉到 Y 軸。
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    return assign(obj, mat)


def text_object(name, body, location, size, mat, align="LEFT", extrude=0.00012, facing_front=True):
    # 正面文字朝 -Y、背面文字朝 +Y，避免背板標籤鏡像顯示。
    rotation_x = math.pi / 2 if facing_front else -math.pi / 2
    bpy.ops.object.text_add(location=location, rotation=(rotation_x, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = 0.00004
    return assign(obj, mat)


def curve_handle(name, x, y, z_low, z_high, outward, mat):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.009
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(3)
    points = [
        (x, y + 0.020, z_low),
        (x + outward, y - 0.005, z_low),
        (x + outward, y - 0.005, z_high),
        (x, y + 0.020, z_high),
    ]
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    return assign(obj, mat)


def make_rf_connector(index, x, z, y, facing_front=True):
    sign = -1 if facing_front else 1
    base_y = y + sign * 0.004
    # 分層金屬環與金色中心可讓近距離視角保留接頭深度。
    cylinder(f"RF {index:02d} hex base", (x, base_y, z), 0.0115, 0.007, METAL_DARK, vertices=6)
    cylinder(f"RF {index:02d} body", (x, base_y + sign * 0.005, z), 0.0092, 0.010, METAL)
    cylinder(f"RF {index:02d} rim", (x, base_y + sign * 0.011, z), 0.0073, 0.004, METAL_BRIGHT)
    cylinder(f"RF {index:02d} dielectric", (x, base_y + sign * 0.0132, z), 0.0047, 0.0015, DARK)
    cylinder(f"RF {index:02d} contact", (x, base_y + sign * 0.0142, z), 0.0016, 0.0018, GOLD)


def make_front():
    rounded_box("Front white fascia", (0, FRONT_Y - 0.0055, 0.058), (0.468, 0.012, 0.073), OFF_WHITE, 0.002)
    rounded_box("Front blue RF field", (-0.047, FRONT_Y - 0.012, 0.052), (0.326, 0.0025, 0.054), BLUE, 0.001)

    xs = [-0.190 + i * 0.0415 for i in range(8)]
    zs = [0.069, 0.035]
    for row, z in enumerate(zs, start=1):
        for col, x in enumerate(xs, start=1):
            port = (row - 1) * 8 + col
            make_rf_connector(port, x, z, FRONT_Y - 0.014)
            text_object(
                f"RF label {row}.{col}", f"RF {row}.{col}", (x, FRONT_Y - 0.029, z - 0.015),
                0.0041, WHITE, align="CENTER", extrude=0.00005
            )

    text_object("Brand", "ROHDE & SCHWARZ", (-0.207, FRONT_Y - 0.0135, 0.089), 0.0065, BRAND_BLUE)
    text_object("Product name", "CMP180  ·  Radio Communication Tester", (-0.075, FRONT_Y - 0.0135, 0.089), 0.0051, CHARCOAL)
    text_object("Order number", "1201.0002K18", (0.119, FRONT_Y - 0.0135, 0.089), 0.0044, CHARCOAL)

    rounded_box("Display bezel", (0.163, FRONT_Y - 0.014, 0.063), (0.045, 0.006, 0.047), LIGHT_GREY, 0.0015)
    rounded_box("Display glass", (0.163, FRONT_Y - 0.018, 0.063), (0.036, 0.002, 0.038), SCREEN, 0.001)
    text_object("Display mark", "R&S", (0.163, FRONT_Y - 0.020, 0.063), 0.009, CHARCOAL, align="CENTER")

    cylinder("Sensor socket", (0.132, FRONT_Y - 0.017, 0.030), 0.007, 0.008, METAL_DARK)
    cylinder("Sensor center", (0.132, FRONT_Y - 0.022, 0.030), 0.0045, 0.002, DARK)
    text_object("Sensor label", "Sensor", (0.132, FRONT_Y - 0.025, 0.018), 0.0035, CHARCOAL, align="CENTER")

    for i, x in enumerate((0.163, 0.179, 0.195)):
        rounded_box(f"Front USB {i + 1}", (x, FRONT_Y - 0.018, 0.030), (0.007, 0.003, 0.014), DARK, 0.0007)
        if i == 0:
            rounded_box("Front USB blue insert", (x, FRONT_Y - 0.020, 0.030), (0.004, 0.001, 0.010), USB_BLUE, 0.0003)

    rounded_box("Power button", (0.216, FRONT_Y - 0.018, 0.026), (0.013, 0.003, 0.008), LIGHT_GREY, 0.001)
    rounded_box("Power LED", (0.216, FRONT_Y - 0.020, 0.027), (0.005, 0.001, 0.002), GREEN, 0.0004)


def make_rear():
    rounded_box("Rear panel", (0, REAR_Y + 0.004, 0.055), (0.455, 0.010, 0.076), REAR_BLACK, 0.0015)
    # 背板區塊稍微前後錯開，避免共面閃爍並保留模組分割線。
    rounded_box("Rear controller module", (-0.075, REAR_Y + 0.010, 0.061), (0.215, 0.003, 0.060), DARK, 0.0005)
    rounded_box("Rear power module", (0.145, REAR_Y + 0.010, 0.061), (0.155, 0.003, 0.060), DARK, 0.0005)

    for name, x, width in (("DisplayPort", -0.135, 0.019), ("HDMI", -0.097, 0.018), ("LAN", -0.055, 0.020)):
        rounded_box(name, (x, REAR_Y + 0.013, 0.070), (width, 0.003, 0.012), REAR_BLACK, 0.001)
    for i, x in enumerate((-0.022, -0.005)):
        rounded_box(f"Rear USB {i + 1}", (x, REAR_Y + 0.013, 0.070), (0.008, 0.003, 0.016), USB_BLUE, 0.0007)

    for i, x in enumerate((-0.132, -0.101, -0.070, -0.039), start=1):
        make_rf_connector(20 + i, x, 0.035, REAR_Y + 0.011, facing_front=False)

    rounded_box("IEC inlet", (0.170, REAR_Y + 0.014, 0.050), (0.032, 0.007, 0.035), BLACK, 0.002)
    rounded_box("Rear power switch", (0.170, REAR_Y + 0.019, 0.077), (0.024, 0.005, 0.016), CHARCOAL, 0.001)
    cylinder("Rear ground stud", (0.080, REAR_Y + 0.015, 0.028), 0.006, 0.007, METAL, rotation=(math.pi / 2, 0, 0))
    text_object("Rear labels", "DISPLAY     HDMI       LAN      USB", (-0.148, REAR_Y + 0.0155, 0.083), 0.0035, WHITE, facing_front=False)


def make_vents():
    for side in (-1, 1):
        x = side * (CHASSIS_W / 2 + 0.002)
        # 側邊百葉以薄片表現，控制面數同時保留照片中的密集通風節奏。
        for row, z in enumerate((0.031, 0.043, 0.055, 0.067, 0.079)):
            for col in range(24):
                y = -0.205 + col * 0.017
                rounded_box(f"Vent {'R' if side > 0 else 'L'} {row:02d}-{col:02d}", (x, y, z), (0.002, 0.010, 0.0045), VENT, 0.0006)


def make_chassis():
    rounded_box("Main chassis", (0, 0, 0.061), (CHASSIS_W, CHASSIS_D, BODY_H), ALUMINUM, 0.006)
    rounded_box("Top panel", (0, -0.010, 0.108), (0.445, 0.520, 0.006), TOP_GREY, 0.002)
    rounded_box("Front upper lip", (0, FRONT_Y - 0.002, 0.101), (0.465, 0.018, 0.010), OFF_WHITE, 0.002)

    for side in (-1, 1):
        x = side * (CHASSIS_W / 2 + 0.004)
        rounded_box(f"Side rail top {'R' if side > 0 else 'L'}", (x, 0.015, 0.097), (0.018, 0.505, 0.016), HANDLE_BLUE, 0.005)
        rounded_box(f"Side rail bottom {'R' if side > 0 else 'L'}", (x, 0.015, 0.023), (0.018, 0.505, 0.016), HANDLE_BLUE, 0.005)
        curve_handle(f"Front handle {'R' if side > 0 else 'L'}", x, FRONT_Y, 0.029, 0.092, side * 0.040, HANDLE_BLUE)

    for x in (-0.183, 0.183):
        for y in (-0.205, 0.205):
            rounded_box("Rubber foot", (x, y, FOOT_H / 2), (0.055, 0.055, FOOT_H), RUBBER, 0.007)


def make_floor_and_lighting():
    rounded_box("Studio floor", (0, 0, -0.006), (1.45, 1.45, 0.010), FLOOR, 0.002)
    world = bpy.context.scene.world
    world.color = (0.035, 0.035, 0.045)
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.025, 0.032, 0.045, 1)
    bg.inputs["Strength"].default_value = 0.25

    for name, loc, energy, size, color in (
        ("Key light", (-0.55, -0.55, 0.65), 230, 0.55, (0.80, 0.90, 1.0)),
        ("Fill light", (0.60, -0.15, 0.40), 120, 0.45, (0.65, 0.80, 1.0)),
        ("Rim light", (0.10, 0.65, 0.55), 260, 0.40, (0.25, 0.55, 1.0)),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = loc
        point_camera(obj, (0, 0, 0.055))


def point_camera(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera():
    data = bpy.data.cameras.new("Hero camera")
    camera = bpy.data.objects.new("Hero camera", data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.75, -1.05, 0.29)
    data.lens = 55
    point_camera(camera, (0, -0.015, 0.060))
    bpy.context.scene.camera = camera


def configure_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    # bpy 5.2 的模組版仍以 BLENDER_EEVEE 枚舉啟用 Eevee 渲染器。
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(RENDER_DIR / "cmp180-hero.png")
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.7


def render_view(camera, name, location, target=(0, 0, 0.058)):
    # 固定三個檢查視角可快速比對正面接頭、背板與整體輪廓。
    camera.location = location
    point_camera(camera, target)
    bpy.context.scene.render.filepath = str(RENDER_DIR / name)
    bpy.ops.render.render(write_still=True)


configure_scene()
ALUMINUM = material("Brushed aluminum", (0.38, 0.40, 0.43, 1), metallic=0.72, roughness=0.28)
TOP_GREY = material("Top silver", (0.53, 0.54, 0.57, 1), metallic=0.55, roughness=0.32)
OFF_WHITE = material("Warm white fascia", (0.82, 0.84, 0.85, 1), metallic=0.10, roughness=0.30)
BLUE = material("CMP panel blue", (0.16, 0.37, 0.56, 1), metallic=0.20, roughness=0.38)
HANDLE_BLUE = material("Handle blue", (0.18, 0.37, 0.55, 1), metallic=0.15, roughness=0.40)
BRAND_BLUE = material("Brand blue", (0.05, 0.42, 0.67, 1), metallic=0.05, roughness=0.35)
METAL = material("Connector metal", (0.48, 0.50, 0.52, 1), metallic=0.94, roughness=0.18)
METAL_BRIGHT = material("Connector bright metal", (0.72, 0.74, 0.77, 1), metallic=0.96, roughness=0.12)
METAL_DARK = material("Connector dark metal", (0.30, 0.31, 0.32, 1), metallic=0.90, roughness=0.24)
GOLD = material("RF contact gold", (0.72, 0.38, 0.05, 1), metallic=0.90, roughness=0.20)
DARK = material("Dark insert", (0.025, 0.030, 0.035, 1), metallic=0.15, roughness=0.30)
BLACK = material("Black", (0.008, 0.009, 0.012, 1), metallic=0.0, roughness=0.35)
CHARCOAL = material("Charcoal text", (0.055, 0.065, 0.075, 1), metallic=0.0, roughness=0.42)
WHITE = material("White print", (0.90, 0.93, 0.95, 1), metallic=0.0, roughness=0.35)
LIGHT_GREY = material("Light grey", (0.60, 0.64, 0.67, 1), metallic=0.30, roughness=0.30)
SCREEN = material("LCD glass", (0.34, 0.42, 0.45, 1), metallic=0.05, roughness=0.12)
REAR_BLACK = material("Rear black", (0.018, 0.020, 0.024, 1), metallic=0.30, roughness=0.40)
VENT = material("Vent dark", (0.012, 0.022, 0.032, 1), metallic=0.35, roughness=0.40)
USB_BLUE = material("USB blue", (0.01, 0.28, 0.55, 1), metallic=0.25, roughness=0.30)
GREEN = material("Status green", (0.05, 0.80, 0.22, 1), metallic=0.0, roughness=0.24)
RUBBER = material("Rubber feet", (0.035, 0.038, 0.042, 1), metallic=0.0, roughness=0.75)
FLOOR = material("Studio floor", (0.035, 0.045, 0.065, 1), metallic=0.10, roughness=0.42)

RENDER_DIR.mkdir(parents=True, exist_ok=True)
make_chassis()
make_vents()
make_front()
make_rear()
make_floor_and_lighting()
make_camera()

scene = bpy.context.scene
scene["asset_name"] = "R&S CMP180 exterior reference model"
scene["units"] = "metres"
scene["model_accuracy"] = "visual reference, not mechanical CAD"
scene["rf_ports"] = 16

# 先儲存完整可編輯場景，再渲染與匯出，確保失敗時仍保留可診斷的 .blend。
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_DIR / "cmp180.blend"))
camera = bpy.context.scene.camera
render_view(camera, "cmp180-hero.png", (0.75, -1.05, 0.29))
render_view(camera, "cmp180-front.png", (0, -1.10, 0.17))
render_view(camera, "cmp180-rear.png", (0, 1.10, 0.17))

# GLB 不含工作室地板與燈光，讓 Web 使用者可自行配置環境。
for obj in bpy.context.scene.objects:
    obj.select_set(obj.name not in {"Studio floor", "Hero camera", "Key light", "Fill light", "Rim light"})
bpy.ops.export_scene.gltf(
    filepath=str(ASSET_DIR / "cmp180.glb"),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
)
print(f"Saved {ASSET_DIR / 'cmp180.blend'}")
print(f"Rendered validation views in {RENDER_DIR}")
print(f"Exported {ASSET_DIR / 'cmp180.glb'}")
