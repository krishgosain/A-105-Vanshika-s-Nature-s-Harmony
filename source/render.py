import bpy, sys, os, json, math
from mathutils import Vector
ROOT = "/home/claude/house/build"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
which = argv[0] if argv else "top"
samples = int(argv[1]) if len(argv) > 1 else 32
res = argv[2] if len(argv) > 2 else "1280x720"
RW, RH = map(int, res.split("x"))

bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "A105_raw.blend"))
scene = bpy.context.scene
meta = json.load(open(os.path.join(ROOT, "layout.json")))
S, H = meta["scale_px_per_m"], meta["ceiling"]
def X(px): return (px - 45) / S
def Y(py): return -(py - 160) / S

# --- world: sky + sun
world = bpy.data.worlds.new("Sky"); scene.world = world; world.use_nodes = True
nt = world.node_tree; bg = nt.nodes["Background"]
sky = nt.nodes.new("ShaderNodeTexSky")
try: sky.sky_type = 'NISHITA'
except Exception: pass
try:
    sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(200)
except Exception: pass
nt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.35
sun_d = bpy.data.lights.new("Sun", "SUN"); sun_d.energy = 3.5; sun_d.angle = math.radians(2)
sun = bpy.data.objects.new("Sun", sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(200))

# --- interior lights (warm downlights + window fills)
for i, (x, y) in enumerate(meta["lights"]):
    ld = bpy.data.lights.new(f"DL{i}", "POINT"); ld.energy = 22; ld.color = (1.0, 0.86, 0.70); ld.shadow_soft_size = 0.08
    o = bpy.data.objects.new(f"DL{i}", ld); o.location = (x, y, H - 0.05); scene.collection.objects.link(o)
def area(name, x, y, z, sx, sy, rot, energy):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy; ld.energy = energy
    ld.color = (0.92, 0.96, 1.0)
    o = bpy.data.objects.new(name, ld); o.location = (x, y, z); o.rotation_euler = rot; scene.collection.objects.link(o)
# window portals (pointing into rooms)
R = math.radians
area("Fill_living", X(782), Y(166), 1.3, 2.4, 2.2, (R(-90), 0, 0), 260)
area("Fill_br3", X(505), Y(166), 1.3, 1.8, 2.2, (R(-90), 0, 0), 160)
area("Fill_br2", X(1185), Y(166), 1.3, 1.8, 2.2, (R(-90), 0, 0), 160)
area("Fill_dining", X(778), Y(748), 1.5, 1.8, 1.4, (R(90), 0, 0), 120)
area("Fill_master", X(50), Y(330), 1.5, 1.0, 1.2, (0, R(90), 0), 90)
area("Fill_mbal", X(125), Y(292), 1.3, 1.4, 2.2, (R(-90), 0, 0), 110)

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = samples
scene.cycles.use_denoising = True
try: scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = RW, RH
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [l for l in []] else 'None'
scene.view_settings.exposure = 0.0

def hide(prefixes=(), colls=()):
    for o in scene.objects:
        if any(o.name.startswith(p) for p in prefixes) or any(c.name in colls for c in o.users_collection):
            o.hide_render = True

cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); scene.collection.objects.link(cam); scene.camera = cam

def look(cam, loc, target):
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

out = os.path.join(ROOT, "renders"); os.makedirs(out, exist_ok=True)
if which == "top":
    hide(colls=("Ceiling",), prefixes=("AC_", "Curtain", "Sheer", "Drape", "BR2_curt", "BR3_curt", "MB_curt", "MB_blind", "Soffit", "Neighbour", "Tree", "DL", "Pendant"))
    for o in scene.objects:
        if o.type == 'LIGHT' and o.name.startswith(("DL", "Fill")): o.hide_render = True
    sun.rotation_euler = (math.radians(12), math.radians(6), math.radians(160)); sun_d.energy = 1.6
    bg.inputs[1].default_value = 0.25
    cam_d.type = 'ORTHO'
    cx, cy = (X(30) + X(1430)) / 2, (Y(60) + Y(870)) / 2
    cam_d.ortho_scale = (1430 - 30) / S * 1.0
    cam.location = (cx, cy, 20); cam.rotation_euler = (0, 0, 0)
    scene.render.resolution_x = RW; scene.render.resolution_y = int(RW * (870 - 60) / (1430 - 30))
    scene.render.filepath = os.path.join(out, "topdown.png")
else:
    cam_d.lens = 15 if which != "detail" else 20
    cam_d.sensor_width = 36
    views = {
        "save": ((1075, 515), 1.55, (700, 300), 1.2),
        # name: (eye px, eye_z, target px, target_z)
        "living": ((1075, 515), 1.55, (700, 300), 1.2),     # from the foyer, like the video's first interior shot
        "living2": ((700, 430), 1.5, (900, 200), 1.2),
        "dining": ((690, 520), 1.6, (520, 745), 1.15),
        "kitchen": ((905, 650), 1.6, (1137, 640), 1.2),
        "br2": ((1110, 400), 1.6, (1313, 270), 1.05),
        "br3": ((610, 440), 1.6, (378, 260), 1.1),
        "master": ((330, 545), 1.6, (55, 380), 1.1),
        "foyer": ((1300, 522), 1.6, (900, 522), 1.3),
    }
    (ex, ey), ez, (tx, ty), tz = views[which]
    look(cam, (X(ex), Y(ey), ez), (X(tx), Y(ty), tz))
    scene.render.filepath = os.path.join(out, f"{which}.png")
if which.startswith("save"):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "A105_Vanshikas_Type5.blend"))
    print("RENDERED saved blend"); sys.exit(0)
bpy.ops.render.render(write_still=True)
print("RENDERED", scene.render.filepath)
