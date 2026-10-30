import bpy, sys, os, math, json
from mathutils import Vector
ROOT = "/home/claude/house/build2"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
which = argv[0]; samples = int(argv[1]); W, Hh = map(int, argv[2].split("x"))
outdir = argv[3] if len(argv) > 3 else os.path.join(ROOT, "renders")
os.makedirs(outdir, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "A105_lux.blend"))
sc = bpy.context.scene
S = 74.0
def X(px): return (px - 45) / S
def Y(py): return -(py - 160) / S

# panorama nodes (plan px, eye height) — shared with the web tour
NODES = json.load(open(os.path.join(ROOT, "nodes.json")))
VIEWS = {
    "hero_living": ((690, 470), 1.45, (860, 250), 1.15),
    "hero_dining": ((830, 545), 1.5, (540, 700), 1.1),
    "hero_master": ((330, 545), 1.45, (60, 410), 1.1),
    "hero_kitchen": ((1000, 738), 1.55, (1110, 590), 1.2),
    "v_living": ((1065, 515), 1.5, (700, 300), 1.2),
    "v_living2": ((700, 440), 1.45, (900, 230), 1.1),
    "v_sofa": ((690, 250), 1.4, (900, 360), 1.05),
    "v_dining": ((760, 560), 1.55, (520, 720), 1.05),
    "v_kitchen": ((905, 650), 1.55, (1137, 620), 1.25),
    "v_br2": ((1090, 420), 1.5, (1313, 280), 1.0),
    "v_br3": ((610, 430), 1.5, (378, 280), 1.05),
    "v_master": ((330, 560), 1.5, (55, 400), 1.05),
    "v_balcony": ((560, 120), 1.5, (900, 90), 1.0),
    "v_foyer": ((1300, 522), 1.6, (900, 522), 1.35),
}
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = W, Hh
sc.cycles.samples = samples
if which == "top":
    for o in sc.objects:
        if any(c.name in ("Ceiling",) for c in o.users_collection) or o.name.startswith(("Balcony_Soffit", "Ring", "Chand", "Backdrop", "ArcLamp", "Sheer", "Drape", "BR2_sheer", "BR3_sheer", "MB_sheer", "BR2_d", "BR3_d", "MB_drape", "Plant_living")) or "_wire" in o.name or "_globe" in o.name:
            o.hide_render = True
        if o.type == 'LIGHT' and not o.name.startswith("Sun"): o.hide_render = True
    sun = sc.objects["Sun"]; sun.rotation_euler = (math.radians(14), math.radians(6), math.radians(160)); sun.data.energy = 2.2
    cam_d.type = 'ORTHO'; cam_d.ortho_scale = 1400 / S
    cam.location = ((X(30) + X(1430)) / 2, (Y(60) + Y(870)) / 2, 20); cam.rotation_euler = (0, 0, 0)
    sc.render.resolution_y = int(W * 810 / 1400)
    sc.view_settings.exposure = -0.2
    sc.render.filepath = os.path.join(outdir, "plan.jpg"); sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
elif which in NODES:
    n = NODES[which]
    cam_d.type = 'PANO'
    try:
        cam_d.panorama_type = 'EQUIRECTANGULAR'
    except Exception:
        cam_d.cycles.panorama_type = 'EQUIRECTANGULAR'
    cam.location = (X(n["px"]), Y(n["py"]), n.get("z", 1.55))
    cam.rotation_euler = (math.radians(90), 0, math.radians(-90))   # centre of the image looks toward +X (east)
    sc.render.filepath = os.path.join(outdir, f"{which}.jpg")
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
else:
    (ex, ey), ez, (tx, ty), tz = VIEWS[which]
    cam_d.lens = 18 if which.startswith("hero") else 16; cam_d.sensor_width = 36
    cam.location = (X(ex), Y(ey), ez)
    d = Vector((X(tx), Y(ty), tz)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(outdir, f"{which}.jpg")
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
bpy.ops.render.render(write_still=True)
print("RENDERED", sc.render.filepath)
