# Blender build script: Vanshika's Nature's Harmony, Flat A-105 (Type 5, 3BHK + Family)
# Geometry traced from the published Type-5 unit plan (74 px = 1 m), interiors from the walkthrough video.
import bpy, bmesh, math, json, os, sys
from mathutils import Vector, Matrix

ROOT = os.environ.get("HOUSE_ROOT", "/home/claude/house/build")
TEX = os.path.join(ROOT, "textures")
S = 74.0
H = 2.85          # clear ceiling height
DOOR_H = 2.10
SLIDE_H = 2.40

def X(px): return (px - 45) / S
def Y(py): return -(py - 160) / S
def M(pxlen): return pxlen / S

COLLIDERS = []   # 2D footprints (meters) for first-person collision: [x0,y0,x1,y1]

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
        COLL[name] = c
    return COLL[name]

# ---------------------------------------------------------------- materials
MATS = {}
def mat(name, color=(0.8, 0.8, 0.8), tex=None, tile=1.0, rough=0.6, metal=0.0,
        alpha=1.0, emit=None, emit_strength=0.0, transmission=0.0, coat=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if coat:
        bsdf.inputs["Coat Weight"].default_value = coat
    if tex:
        img = bpy.data.images.load(os.path.join(TEX, tex), check_existing=True)
        tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img
        tn.location = (-400, 200)
        nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
        m.use_backface_culling = False
    if transmission:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    m["tile"] = tile
    MATS[name] = m
    return m

def T(name):  # tile size lookup
    return MATS[name]["tile"] if name in MATS else 1.0

# palette
mat("paint_white", (0.86, 0.85, 0.82), rough=0.85, tile=1)
mat("paint_ext", (0.80, 0.80, 0.78), rough=0.9, tile=1)
mat("paint_taupe", (0.42, 0.36, 0.30), rough=0.85)
mat("paint_darkgrey", (0.20, 0.20, 0.21), rough=0.85)
mat("ceiling", (0.92, 0.92, 0.90), rough=0.9)
mat("floor_tile", tex="floor_tile.jpg", tile=1.6, rough=0.12, coat=0.6)
mat("wood_floor", tex="wood_floor.jpg", tile=1.2, rough=0.35)
mat("bath_tile", tex="bath_tile.jpg", tile=1.2, rough=0.4)
mat("bath_tile_light", tex="bath_tile_light.jpg", tile=1.2, rough=0.3)
mat("balcony_tile", tex="balcony_tile.jpg", tile=1.2, rough=0.7)
mat("granite", tex="granite_dark.jpg", tile=1.0, rough=0.2)
mat("corridor_tile", tex="corridor_tile.jpg", tile=1.2, rough=0.5)
mat("oak", tex="oak.jpg", tile=1.0, rough=0.5)
mat("walnut", tex="walnut.jpg", tile=1.0, rough=0.45)
mat("marble_white", tex="marble_white.jpg", tile=1.4, rough=0.15)
mat("marble_grey", tex="marble_grey.jpg", tile=1.6, rough=0.3)
mat("marble_table", tex="marble_table.jpg", tile=1.2, rough=0.12)
mat("tv_wallpaper", tex="tv_wallpaper.jpg", tile=0.7, rough=0.6, metal=0.2)
mat("br2_wallpaper", tex="br2_wallpaper.jpg", tile=1.5, rough=0.8)
mat("grey_wall", tex="grey_wall.jpg", tile=1.5, rough=0.85)
mat("panel_greywood", tex="panel_greywood.jpg", tile=1.0, rough=0.6)
mat("channel_dark", tex="channel_dark.jpg", tile=1.0, rough=0.9)
mat("channel_beige", tex="channel_beige.jpg", tile=1.0, rough=0.9)
mat("chevron", tex="chevron.jpg", tile=1.0, rough=0.9)
mat("fabric_sofa", tex="fabric_sofa.jpg", tile=0.5, rough=0.95)
mat("fabric_green", tex="fabric_green.jpg", tile=0.5, rough=0.8)
mat("fabric_bedgrey", tex="fabric_bedgrey.jpg", tile=0.5, rough=0.95)
mat("fabric_white", tex="fabric_white.jpg", tile=0.5, rough=0.95)
mat("fabric_teal", tex="fabric_teal.jpg", tile=0.5, rough=0.9)
mat("fabric_black", tex="fabric_black.jpg", tile=0.5, rough=0.95)
mat("slats", tex="slats.jpg", tile=1.0, rough=0.6)
mat("white_gloss", (0.90, 0.90, 0.89), rough=0.08, coat=0.5)
mat("white_matte", (0.88, 0.88, 0.86), rough=0.5)
mat("grey_cab", (0.42, 0.43, 0.44), rough=0.35)
mat("yellow_glass", (0.82, 0.62, 0.12), rough=0.3)
mat("black_gloss", (0.02, 0.02, 0.02), rough=0.08)
mat("black_matte", (0.04, 0.04, 0.045), rough=0.5)
mat("steel", (0.75, 0.75, 0.76), rough=0.25, metal=1.0)
mat("copper", (0.70, 0.40, 0.25), rough=0.3, metal=1.0)
mat("frame_white", (0.93, 0.93, 0.92), rough=0.4)
mat("frame_dark", (0.10, 0.07, 0.05), rough=0.4)
mat("glass", (0.85, 0.92, 0.95), rough=0.02, alpha=0.18)
mat("mirror", (0.72, 0.78, 0.80), rough=0.06, metal=0.0, coat=1.0)
mat("mirror_ring", (0.62, 0.60, 0.56), rough=0.4, metal=0.6)
mat("porcelain", (0.96, 0.96, 0.95), rough=0.1)
mat("sheer", (0.95, 0.94, 0.90), rough=0.9, alpha=0.55)
mat("curtain_grey", (0.30, 0.31, 0.33), rough=0.95)
mat("curtain_beige", (0.68, 0.62, 0.52), rough=0.95)
mat("curtain_pattern", tex="curtain_pattern.jpg", tile=0.6, rough=0.95)
mat("led", (1, 0.95, 0.85), emit=(1.0, 0.92, 0.80), emit_strength=12)
mat("led_cool", (1, 1, 1), emit=(0.95, 0.97, 1.0), emit_strength=8)
mat("sign_panel", (0.20, 0.12, 0.07), rough=0.5)
mat("plant", (0.12, 0.32, 0.12), rough=0.8)
mat("pot", (0.85, 0.85, 0.83), rough=0.4)
mat("lawn", (0.18, 0.32, 0.12), rough=0.95)
mat("ground", (0.35, 0.34, 0.32), rough=0.95)
mat("ac", (0.95, 0.95, 0.94), rough=0.3)
mat("screen", (0.01, 0.01, 0.012), rough=0.05)
mat("ceramic_vase", (0.45, 0.25, 0.18), rough=0.5)
for a in ["art_coral.png", "art_slats.png", "art_sticks.png", "art_frame_br3.png", "art_orange_l.png", "art_orange_r.png"]:
    mat(a.split(".")[0], tex=a, tile=1.0, rough=0.6)

# ---------------------------------------------------------------- mesh helpers
def _finish(obj, cname):
    coll(cname).objects.link(obj)
    return obj

def box_m(name, x0, y0, z0, x1, y1, z1, material, cname="Furniture", collide=False, uvmode="world", bevel=0.0):
    """Axis-aligned box in metres with world-scaled UVs (tiles at real size)."""
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1); z0, z1 = min(z0, z1), max(z0, z1)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for f in faces: bm.faces.new([vs[i] for i in f])
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    tile = T(material)
    for f in bm.faces:
        n = f.normal
        for l in f.loops:
            p = l.vert.co
            if uvmode == "unit":
                # fit 0..1 on the largest face (for art)
                if abs(n.z) > 0.5: u, v = (p.x - x0) / max(x1-x0,1e-6), (p.y - y0) / max(y1-y0,1e-6)
                elif abs(n.x) > 0.5: u, v = (p.y - y0) / max(y1-y0,1e-6), (p.z - z0) / max(z1-z0,1e-6)
                else: u, v = (p.x - x0) / max(x1-x0,1e-6), (p.z - z0) / max(z1-z0,1e-6)
                if (abs(n.x) > 0.5 and n.x < 0) or (abs(n.y) > 0.5 and n.y > 0): u = 1 - u
            else:
                if abs(n.z) > 0.5: u, v = p.x, p.y
                elif abs(n.x) > 0.5: u, v = p.y, p.z
                else: u, v = p.x, p.z
                u /= tile; v /= tile
            l[uv].uv = (u, v)
    bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(MATS[material])
    if bevel:
        md = obj.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 2
    if collide:
        COLLIDERS.append([round(x0,3), round(y0,3), round(x1,3), round(y1,3)])
    return _finish(obj, cname)

def box_px(name, px0, py0, px1, py1, z0, z1, material, cname="Walls", collide=True):
    return box_m(name, X(px0), Y(py0), z0, X(px1), Y(py1), z1, material, cname, collide)

def box_c(name, cx, cy, cz, sx, sy, sz, material, cname="Furniture", collide=False, rot=0.0, bevel=0.0, uvmode="world"):
    """Box by centre/size in metres, optional Z rotation (degrees). cz is the bottom."""
    o = box_m(name, -sx/2, -sy/2, 0, sx/2, sy/2, sz, material, cname, False, uvmode, bevel)
    o.location = (cx, cy, cz); o.rotation_euler[2] = math.radians(rot)
    if collide:
        c, s = abs(math.cos(math.radians(rot))), abs(math.sin(math.radians(rot)))
        hx, hy = (sx*c + sy*s)/2, (sx*s + sy*c)/2
        COLLIDERS.append([round(cx-hx,3), round(cy-hy,3), round(cx+hx,3), round(cy+hy,3)])
    return o

def cyl(name, cx, cy, cz, r, h, material, cname="Furniture", verts=24, rx=None, ry=None, rot_x=0.0, rot_y=0.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h/2))
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co
            l[uv].uv = (p.x / r * 0.5 + 0.5, p.y / r * 0.5 + 0.5) if abs(f.normal.z) > 0.5 else (math.atan2(p.y, p.x) / 6.283 + 0.5, p.z)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    o.location = (cx, cy, cz)
    o.scale = ((rx or r)/r, (ry or r)/r, 1)
    o.rotation_euler = (math.radians(rot_x), math.radians(rot_y), 0)
    return _finish(o, cname)

def art(name, cx, cy, cz, w, h, material, facing, depth=0.02, cname="Decor"):
    """Flat artwork; facing in {'N','S','E','W'} = direction the picture faces; cz is centre height."""
    if facing in "NS":
        o = box_m(name, cx - w/2, cy - depth/2, cz - h/2, cx + w/2, cy + depth/2, cz + h/2, material, cname, False, "unit")
    else:
        o = box_m(name, cx - depth/2, cy - w/2, cz - h/2, cx + depth/2, cy + w/2, cz + h/2, material, cname, False, "unit")
    # correct mirroring for the side that is visible
    if facing in ("S", "E"):
        for l in o.data.uv_layers[0].data: pass
    return o

def curtain(name, x0, y0, x1, y1, z0, z1, material, folds=10, amp=0.05, cname="Decor"):
    """Wavy curtain sheet between two plan points (metres)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    L = math.hypot(x1-x0, y1-y0); nx, ny = (x1-x0)/L, (y1-y0)/L; px, py = -ny, nx
    seg = folds * 6; rows = 2
    grid = []
    for j in range(rows):
        z = z0 + (z1 - z0) * j / (rows - 1)
        row = []
        for i in range(seg + 1):
            t = i / seg; w = math.sin(t * folds * 2 * math.pi) * amp
            row.append(bm.verts.new((x0 + nx*L*t + px*w, y0 + ny*L*t + py*w, z)))
        grid.append(row)
    uv = bm.loops.layers.uv.new("UVMap")
    for j in range(rows - 1):
        for i in range(seg):
            f = bm.faces.new([grid[j][i], grid[j][i+1], grid[j+1][i+1], grid[j+1][i]])
            for l, (u, v) in zip(f.loops, [(i/seg, 0), ((i+1)/seg, 0), ((i+1)/seg, 1), (i/seg, 1)]):
                l[uv].uv = (u * L, v * (z1 - z0))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    md = o.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.01
    return _finish(o, cname)

def plant(name, cx, cy, cz, h=0.9, r=0.25, pot_h=0.35, pot_r=0.17):
    cyl(name + "_pot", cx, cy, cz, pot_r, pot_h, "pot", "Decor", 16)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS["plant"])
    o.location = (cx, cy, cz + pot_h + h*0.45); o.scale = (1, 1, h / (2*r))
    _finish(o, "Decor")

# ---------------------------------------------------------------- walls with openings
def wall(name, px0, py0, px1, py1, openings=(), material="paint_white"):
    """Wall rectangle in plan px. openings: list of dicts {a,b (px along long axis), bot, top, kind, ...}."""
    horiz = (px1 - px0) >= (py1 - py0)
    lo, hi = (px0, px1) if horiz else (py0, py1)
    ops = sorted(openings, key=lambda o: o["a"])
    cur = lo; k = 0
    def seg(a, b, z0, z1, tag, collide):
        nonlocal k; k += 1
        if b - a <= 0.01 or z1 - z0 <= 0.001: return
        if horiz: box_px(f"{name}_{tag}{k}", a, py0, b, py1, z0, z1, material, "Walls", collide)
        else:     box_px(f"{name}_{tag}{k}", px0, a, px1, b, z0, z1, material, "Walls", collide)
    for o in ops:
        seg(cur, o["a"], 0, H, "w", True)
        if o["bot"] > 0: seg(o["a"], o["b"], 0, o["bot"], "sill", o["bot"] > 0.5)
        seg(o["a"], o["b"], o["top"], H, "lintel", False)
        add_fill(name, o, horiz, px0, py0, px1, py1)
        cur = o["b"]
    seg(cur, hi, 0, H, "w", True)

def add_fill(name, o, horiz, px0, py0, px1, py1):
    kind = o["kind"]
    a, b, bot, top = o["a"], o["b"], o["bot"], o["top"]
    # wall-centre line in metres
    if horiz:
        c = (Y(py0) + Y(py1)) / 2; th = abs(Y(py1) - Y(py0))
        A, B = X(a), X(b)
    else:
        c = (X(px0) + X(px1)) / 2; th = abs(X(px1) - X(px0))
        A, B = Y(a), Y(b)
    lo, hi = min(A, B), max(A, B)
    def frame_box(nm, u0, u1, z0, z1, mt, depth):
        if horiz: box_m(nm, u0, c - depth/2, z0, u1, c + depth/2, z1, mt, "Openings")
        else:     box_m(nm, c - depth/2, u0, z0, c + depth/2, u1, z1, mt, "Openings")
    f = 0.05
    if kind in ("window", "slider"):
        fm = "frame_white"
        frame_box(f"{name}_fr_t", lo, hi, top - f, top, fm, th * 0.6)
        frame_box(f"{name}_fr_b", lo, hi, bot, bot + f, fm, th * 0.6)
        frame_box(f"{name}_fr_l", lo, lo + f, bot, top, fm, th * 0.6)
        frame_box(f"{name}_fr_r", hi - f, hi, bot, top, fm, th * 0.6)
        if kind == "window":
            mid = (lo + hi) / 2
            frame_box(f"{name}_fr_m", mid - f/2, mid + f/2, bot, top, fm, th * 0.5)
            frame_box(f"{name}_glass", lo + f, hi - f, bot + f, top - f, "glass", 0.01)
        else:
            # sliding door: one glass panel closed, the other slid behind it (opening left walkable)
            mid = (lo + hi) / 2
            if horiz:
                box_m(f"{name}_panelA", lo + f, c - 0.035, bot + f, mid + 0.03, c - 0.015, top - f, "glass", "Openings")
                box_m(f"{name}_panelB", lo + f + 0.05, c + 0.015, bot + f, mid + 0.06, c + 0.035, top - f, "glass", "Openings")
                box_m(f"{name}_mullion", mid - 0.02 + 0.03, c - 0.04, bot, mid + 0.03 + 0.02, c + 0.04, top, fm, "Openings")
            else:
                box_m(f"{name}_panelA", c - 0.035, lo + f, bot + f, c - 0.015, mid + 0.03, top - f, "glass", "Openings")
                box_m(f"{name}_panelB", c + 0.015, lo + f + 0.05, bot + f, c + 0.035, mid + 0.06, top - f, "glass", "Openings")
            COLLIDERS.append(([lo, c - 0.05, mid + 0.06, c + 0.05] if horiz else [c - 0.05, lo, c + 0.05, mid + 0.06]))
    elif kind == "door":
        fm = o.get("frame", "frame_dark")
        depth = th + 0.03
        frame_box(f"{name}_dfr_t", lo - 0.05, hi + 0.05, top, top + 0.07, fm, depth)
        frame_box(f"{name}_dfr_l", lo - 0.05, lo, 0, top, fm, depth)
        frame_box(f"{name}_dfr_r", hi, hi + 0.05, 0, top, fm, depth)
        # open leaf: hinge at one end, swung ~95 deg to one side
        width = hi - lo - 0.01
        hinge_at_lo = o.get("hinge", "a") == "a"
        # in metres the 'a' end maps to A; find which of lo/hi that is
        hinge = A if hinge_at_lo else B
        side = o.get("swing", 1)       # +1 toward +py (plan) / +px
        # convert plan direction to world: +py -> -Y ; +px -> +X
        if horiz:
            dirv = Vector((0, -side, 0))
            hp = Vector((hinge, c, 0))
            along = Vector((1 if hinge == lo else -1, 0, 0))
        else:
            dirv = Vector((side, 0, 0))
            hp = Vector((c, hinge, 0))
            along = Vector((0, 1 if hinge == lo else -1, 0))
        ang = math.radians(95)
        leafdir = (along * math.cos(ang) + dirv * math.sin(ang)).normalized()
        leaf = box_c(f"{name}_leaf", 0, 0, 0, width, 0.04, top - 0.01, o.get("leaf", "walnut"), "Openings")
        leaf.location = hp + leafdir * (width / 2) + Vector((0, 0, 0.005))
        leaf.rotation_euler[2] = math.atan2(leafdir.y, leafdir.x)
        # handle
        hx = hp + leafdir * (width - 0.08)
        box_c(f"{name}_handle", hx.x, hx.y, 1.0, 0.14, 0.07, 0.02, "steel", "Openings", rot=math.degrees(math.atan2(leafdir.y, leafdir.x)))

def D(a, b, hinge="a", swing=1, **kw):
    d = dict(a=a, b=b, bot=0, top=DOOR_H, kind="door", hinge=hinge, swing=swing); d.update(kw); return d
def W(a, b, bot=0.9, top=2.1): return dict(a=a, b=b, bot=bot, top=top, kind="window")
def SL(a, b): return dict(a=a, b=b, bot=0, top=SLIDE_H, kind="slider")

# ---- master / west block
wall("MasterWest", 45, 160, 55, 752, [W(290, 368)])
wall("BalconyT1", 180, 160, 192, 292)
wall("MasterNorth", 55, 288, 365, 297, [SL(70, 180), D(238, 300, hinge="a", swing=-1, leaf="walnut")])
wall("T1North", 180, 160, 438, 172, [W(195, 240, 1.5, 2.1)])
wall("MasterEast", 365, 172, 378, 557, [D(492, 557, hinge="a", swing=-1)])
wall("MasterSouth", 45, 597, 313, 605)
wall("T3North", 313, 557, 450, 564, [D(378, 437, hinge="b", swing=1)])
wall("T3West", 313, 564, 325, 745, [W(687, 740, 1.6, 2.1)])
wall("T3East", 437, 564, 450, 752)
# ---- north block
wall("BR3South", 378, 462, 635, 470, [D(572, 632, hinge="b", swing=-1)])
wall("NorthMid", 438, 160, 935, 172, [SL(450, 572), SL(692, 872)])
wall("BR3Living", 635, 172, 649, 470)
wall("T2West", 922, 172, 935, 385)
wall("T2South", 935, 378, 1047, 385)
wall("T2North", 935, 160, 1047, 172, [W(960, 1010, 1.7, 2.1)])
wall("BR2West", 1047, 160, 1057, 452, [D(318, 376, hinge="a", swing=-1), D(388, 450, hinge="b", swing=1)])
wall("BR2North", 1057, 160, 1325, 172, [SL(1117, 1253)])
wall("BR2East", 1313, 172, 1325, 452)
wall("BR2South", 1047, 452, 1420, 462)
# ---- entry / kitchen / south
wall("MainDoorLine", 1137, 462, 1150, 562, [D(475, 557, hinge="a", swing=-1, leaf="walnut")])
wall("KitchenEast", 1137, 562, 1150, 850)
wall("KitchenNorth", 935, 562, 1137, 568)
box_px("Pillar", 905, 555, 935, 592, 0, H, "grey_cab", "Walls")
wall("KitchenSouth", 847, 745, 1137, 752, [D(1002, 1060, hinge="b", swing=1, leaf="walnut")])
wall("DiningSouth", 313, 745, 847, 752, [W(712, 845, 0.75, 2.2)])
wall("UtilityWest", 922, 752, 935, 850)
box_px("UtilityParapet", 935, 842, 1137, 850, 0, 1.0, "paint_white", "Walls")
wall("VestibuleSouth", 1150, 583, 1420, 597)
wall("VestibuleEnd", 1410, 462, 1420, 583)
# shaft / duct closures (keep the exterior tidy)
box_px("ShaftW", 248, 95, 262, 160, 0, H, "paint_ext", "Walls", False)
box_px("ShaftE", 365, 95, 378, 172, 0, H, "paint_ext", "Walls")
box_px("Shaft2W", 922, 95, 935, 160, 0, H, "paint_ext", "Walls", False)
box_px("Shaft2E", 1047, 95, 1057, 160, 0, H, "paint_ext", "Walls")

# ---------------------------------------------------------------- floors & ceiling
def floor(name, px0, py0, px1, py1, material, z=0.0, cname="Floors"):
    box_px(name, px0, py0, px1, py1, z - 0.05, z, material, cname, False)
floor("Floor_Main", 55, 172, 1137, 745, "floor_tile")
floor("Floor_BR2", 1137, 172, 1313, 452, "floor_tile")
floor("Floor_BR2b", 1057, 160, 1137, 172, "floor_tile")
box_px("Floor_Doorway", 1137, 475, 1150, 557, -0.05, 0.003, "granite", "Floors", False)
box_m("Floor_Master", X(55), Y(297), 0, X(365), Y(557), 0.004, "wood_floor", "Floors")
box_m("Floor_Master2", X(55), Y(557), 0, X(313), Y(597), 0.004, "wood_floor", "Floors")
for nm, r in {"T1": (192, 172, 365, 288), "T2": (935, 172, 1047, 378), "T3": (325, 564, 437, 745)}.items():
    box_m("Floor_" + nm, X(r[0]), Y(r[1]), 0, X(r[2]), Y(r[3]), 0.004, "bath_tile", "Floors")
floor("Floor_Utility", 935, 752, 1137, 842, "bath_tile", -0.02)
floor("Floor_Vestibule", 1150, 462, 1410, 583, "corridor_tile", 0.0)
box_m("Floor_Mat", X(1155), Y(480), 0, X(1185), Y(555), 0.006, "granite", "Floors")
floor("Balcony_Master", 55, 160, 180, 288, "balcony_tile", -0.03)
floor("Balcony_Living", 415, 75, 880, 160, "balcony_tile", -0.03)
floor("Balcony_BR2", 1057, 78, 1313, 160, "balcony_tile", -0.03)
floor("Slab_Below", 30, 60, 1430, 870, "paint_ext", -0.08, "Exterior")

# ceiling (flat) + band with LED strips
box_m("Ceiling", X(45), Y(160), H, X(1150), Y(752), H + 0.12, "ceiling", "Ceiling")
box_m("Ceiling_Vest", X(1150), Y(452), H, X(1420), Y(597), H + 0.12, "ceiling", "Ceiling")
for nm, r in {"Bal_L": (415, 75, 880, 160), "Bal_B2": (1057, 78, 1313, 160), "Bal_M": (55, 160, 180, 288)}.items():
    box_m("Soffit_" + nm, X(r[0]), Y(r[1]), H + 0.15, X(r[2]), Y(r[3]), H + 0.3, "paint_ext", "Ceiling")
# recessed band running from the foyer to the family area (seen in every hall shot)
band_y0, band_y1 = Y(482), Y(528)
box_m("CeilingBand", X(470), band_y1, H - 0.02, X(1137), band_y0, H, "slats", "Ceiling")
box_m("LED_band_N", X(470), band_y0 - 0.025, H - 0.025, X(1137), band_y0, H - 0.02, "led", "Ceiling")
box_m("LED_band_S", X(470), band_y1, H - 0.025, X(1137), band_y1 + 0.025, H - 0.02, "led", "Ceiling")

# railings
def railing(name, px0, py0, px1, py1, z=-0.03):
    box_px(name + "_glass", px0, py0, px1, py1, z, z + 1.0, "glass", "Exterior")
    box_m(name + "_rail", X(px0) - 0.01, Y(py0) + 0.02 if py0 == py1 else Y(py0), z + 1.0, X(px1) + 0.01, Y(py1) - 0.02 if py0 == py1 else Y(py1), z + 1.05, "steel", "Exterior")
railing("RailM_N", 55, 160, 180, 164)
railing("RailL_N", 415, 72, 880, 78); railing("RailL_W", 412, 75, 418, 160); railing("RailL_E", 877, 75, 883, 160)
railing("RailB_N", 1057, 75, 1313, 81); railing("RailB_E", 1310, 78, 1316, 160)
box_px("BalWall_LW", 378, 160, 415, 172, -0.03, 1.05, "paint_ext", "Exterior")
box_px("BalWall_LE", 880, 160, 922, 172, -0.03, 1.05, "paint_ext", "Exterior")

# ---------------------------------------------------------------- LIVING (TV wall west, sofa east, balcony north)
xl0, xl1, yl0, yl1 = X(649), X(922), Y(172), Y(462)
# TV feature wall on partition (faces east): bronze wallpaper + grey mirror strip
box_m("TVWall_paper", xl0, Y(400), 0, xl0 + 0.02, Y(190), H, "tv_wallpaper", "Decor")
box_m("TVWall_grey", xl0, Y(440), 0, xl0 + 0.03, Y(400), H, "mirror_ring", "Decor")
box_c("TV", xl0 + 0.05, Y(298), 0.95, 0.05, 1.45, 0.82, "screen", "Furniture")
box_c("TVConsole", xl0 + 0.22, Y(310), 0.22, 0.42, 2.6, 0.22, "white_gloss", "Furniture", collide=True)
box_c("TVConsoleTrim", xl0 + 0.22, Y(310), 0.20, 0.40, 2.6, 0.02, "grey_cab", "Furniture")
cyl("Vase", xl0 + 0.25, Y(410), 0.44, 0.08, 0.3, "ceramic_vase", "Decor")
box_c("Frame_tv", xl0 + 0.25, Y(225), 0.44, 0.04, 0.3, 0.24, "frame_dark", "Decor", rot=0)
# sofa against toilet-2 wall, facing west
sx = xl1 - 0.48
box_c("Sofa_base", sx, Y(325), 0.12, 0.92, 2.35, 0.32, "fabric_sofa", collide=True, bevel=0.03)
box_c("Sofa_back", xl1 - 0.12, Y(325), 0.12, 0.2, 2.35, 0.72, "fabric_sofa", bevel=0.04)
for i, yy in enumerate([-0.78, 0, 0.78]):
    box_c(f"Sofa_seat{i}", sx - 0.05, Y(325) + yy, 0.44, 0.7, 0.76, 0.14, "fabric_sofa", bevel=0.04)
    box_c(f"Sofa_cush{i}", xl1 - 0.3, Y(325) + yy, 0.5, 0.18, 0.72, 0.38, "fabric_sofa", bevel=0.05)
for s in (-1, 1):
    box_c(f"Sofa_arm{s}", sx, Y(325) + s * 1.24, 0.12, 0.92, 0.14, 0.52, "fabric_sofa", bevel=0.05)
art("Art_coral", xl1 - 0.02, Y(325), 1.75, 1.75, 0.85, "art_coral", "W")
# coffee table (oval white marble) + side table
cyl("CoffeeTable_top", X(790), Y(330), 0.38, 0.5, 0.04, "marble_table", rx=0.68, ry=0.42, verts=40)
cyl("CoffeeTable_base", X(790), Y(330), 0.0, 0.35, 0.38, "grey_cab", rx=0.5, ry=0.28, verts=32)
COLLIDERS.append([X(790) - 0.6, Y(330) - 0.35, X(790) + 0.6, Y(330) + 0.35])
cyl("SideTable", X(880), Y(440), 0.0, 0.25, 0.55, "marble_table", verts=24)
for i in range(6):
    box_c(f"Chess{i}", X(872) + (i % 3) * 0.06, Y(438) - (i // 3) * 0.08, 0.55, 0.035, 0.035, 0.07 + (i % 2) * 0.03, "black_matte" if i % 2 else "white_matte", "Decor")
# two dark-green armchairs
def armchair(n, cx, cy, rot):
    box_c(n + "_seat", cx, cy, 0.18, 0.78, 0.78, 0.26, "fabric_green", collide=True, rot=rot, bevel=0.03)
    off = Vector((0.33, 0, 0)); off.rotate(Matrix.Rotation(math.radians(rot), 3, 'Z'))
    box_c(n + "_back", cx + off.x, cy + off.y, 0.18, 0.14, 0.78, 0.62, "fabric_green", rot=rot, bevel=0.04)
    for s in (-1, 1):
        o2 = Vector((0.0, s * 0.35, 0)); o2.rotate(Matrix.Rotation(math.radians(rot), 3, 'Z'))
        box_c(n + f"_arm{s}", cx + o2.x, cy + o2.y, 0.18, 0.78, 0.1, 0.42, "fabric_green", rot=rot, bevel=0.04)
    for s in (-1, 1):
        for t in (-1, 1):
            o3 = Vector((0.3 * t, 0.3 * s, 0)); o3.rotate(Matrix.Rotation(math.radians(rot), 3, 'Z'))
            cyl(n + f"_leg{s}{t}", cx + o3.x, cy + o3.y, 0, 0.015, 0.18, "black_matte", verts=8)
armchair("Armchair_A", X(860), Y(215), 120)   # by the balcony glazing, facing the room
armchair("Armchair_B", X(735), Y(415), -60)   # near the TV, angled to the sofa
box_c("AC_living", X(780), Y(172) - 0.12, 2.42, 1.0, 0.22, 0.3, "ac", "Decor")
curtain("Sheer_L1", X(695), Y(176), X(740), Y(176), 0.02, 2.6, "sheer", folds=6, amp=0.04)
curtain("Sheer_L2", X(745), Y(178), X(868), Y(178), 0.02, 2.6, "sheer", folds=14, amp=0.035)
curtain("Drape_L", X(868), Y(180), X(886), Y(180), 0.02, 2.6, "curtain_beige", folds=3, amp=0.04)
box_m("CurtainRod_L", X(690), Y(181), 2.62, X(890), Y(176), 2.64, "steel", "Decor")

# ---------------------------------------------------------------- FOYER / VESTIBULE
art("Art_slats", X(1010), Y(568) + 0.012, 1.45, 0.42, 1.5, "art_slats", "N")
box_m("Foyer_panel", X(1080), Y(452) - 0.04, 0.0, X(1136), Y(452) - 0.0, H, "walnut", "Decor")
cyl("Foyer_mirror", X(1108), Y(452) - 0.05, 1.5, 0.28, 0.02, "mirror", "Decor", verts=40, rot_x=90)
box_c("Foyer_shelf", X(950), Y(575) - 0.18, 0, 0.3, 0.36, 2.4, "walnut", collide=True)
for i, z in enumerate([0.6, 1.1, 1.6]):
    cyl(f"Elephant{i}", X(950), Y(575) - 0.18, z, 0.06, 0.12, "white_matte", "Decor", verts=12)
# fins at the corridor edge
for i in range(3):
    box_c(f"Fin{i}", X(908) - i * 0.12, Y(600) - 0.08, 0, 0.05, 0.14, H, "walnut", collide=(i == 0))
# entrance vestibule: backlit name board "VANSHIKAS A-105"
box_m("Sign_board", X(1190), Y(462) - 0.05, 1.25, X(1235), Y(462) - 0.01, 1.85, "sign_panel", "Decor")
box_m("Sign_glow", X(1188), Y(462) - 0.012, 1.23, X(1237), Y(462) - 0.008, 1.87, "led", "Decor")
box_m("Sign_plank", X(1240), Y(462) - 0.03, 1.38, X(1300), Y(462) - 0.008, 1.62, "walnut", "Decor")
plant("Plant_vest", X(1165), Y(570), 0)
art("Art_vest", X(1300), Y(583) - 0.015, 1.5, 1.8, 0.7, "art_sticks", "N")

# ---------------------------------------------------------------- DINING (mirrors on south wall, crockery on west)
box_c("Dining_top", X(590), Y(648), 0.74, 1.85, 0.95, 0.04, "marble_table", collide=True)
box_c("Dining_base", X(590), Y(648), 0, 1.1, 0.25, 0.74, "walnut")
for i in range(3):
    for s in (-1, 1):
        cx = X(590) + (i - 1) * 0.6; cy = Y(648) + s * 0.68
        box_c(f"DChair{i}{s}_seat", cx, cy, 0.42, 0.46, 0.46, 0.06, "fabric_teal", bevel=0.01)
        box_c(f"DChair{i}{s}_back", cx, cy + s * 0.22, 0.48, 0.44, 0.04, 0.5, "fabric_teal", bevel=0.01)
        for t in (-1, 1):
            box_c(f"DChair{i}{s}_post{t}", cx + t * 0.23, cy + s * 0.24, 0.0, 0.03, 0.03, 1.0, "walnut")
        box_c(f"DChair{i}{s}_rail", cx, cy + s * 0.24, 0.97, 0.49, 0.03, 0.04, "walnut")
        for t in (-1, 1):
            box_c(f"DChair{i}{s}_leg{t}", cx + t * 0.2, cy - s * 0.18, 0, 0.03, 0.03, 0.42, "walnut")
# round mirror cluster
wy = Y(745) + 0.03
cyl("Mirror_big_ring", X(560), wy, 1.55, 0.42, 0.04, "mirror_ring", "Decor", verts=48, rot_x=90, rx=0.46, ry=0.40)
cyl("Mirror_big", X(560), wy + 0.01, 1.55, 0.34, 0.04, "mirror", "Decor", verts=48, rot_x=90, rx=0.37, ry=0.32)
cyl("Mirror_s_ring", X(625), wy, 1.95, 0.22, 0.04, "mirror_ring", "Decor", verts=32, rot_x=90)
cyl("Mirror_s", X(625), wy + 0.01, 1.95, 0.17, 0.04, "mirror", "Decor", verts=32, rot_x=90)
cyl("Mirror_m_ring", X(630), wy, 1.35, 0.27, 0.04, "mirror_ring", "Decor", verts=32, rot_x=90)
cyl("Mirror_m", X(630), wy + 0.01, 1.35, 0.21, 0.04, "mirror", "Decor", verts=32, rot_x=90)
# crockery: tall black-glass cabinet + low white unit with glass shelves & plants
cx0 = X(450) + 0.02
box_m("Crockery_tall", cx0, Y(640), 0, cx0 + 0.45, Y(600), 2.4, "black_gloss", "Furniture", collide=True)
box_m("Crockery_tall_glass", cx0 + 0.45, Y(637), 0.1, cx0 + 0.46, Y(603), 2.3, "mirror_ring", "Furniture")
box_m("Crockery_low", cx0, Y(742), 0, cx0 + 0.42, Y(642), 0.85, "white_gloss", "Furniture", collide=True)
box_m("Crockery_back", cx0, Y(742), 0.85, cx0 + 0.02, Y(642), 2.4, "panel_greywood", "Furniture")
for z in (1.3, 1.75):
    box_m(f"Crockery_shelf{z}", cx0, Y(742), z, cx0 + 0.3, Y(642), z + 0.012, "glass", "Furniture")
for i in range(5):
    plant(f"Herb{i}", cx0 + 0.2, Y(735) + i * 0.27, 0.85, h=0.18, r=0.07, pot_h=0.1, pot_r=0.06)
curtain("Curtain_dining_L", X(706), Y(740), X(740), Y(740), 0.05, 2.3, "curtain_pattern", folds=4, amp=0.04)
curtain("Curtain_dining_R", X(818), Y(740), X(852), Y(740), 0.05, 2.3, "curtain_pattern", folds=4, amp=0.04)
box_m("CurtainRod_D", X(700), Y(741), 2.32, X(858), Y(739), 2.34, "steel", "Decor")
# pendant over dining
cyl("Pendant_D", X(590), Y(648), 2.15, 0.18, 0.12, "black_matte", "Decor", verts=24)

# ---------------------------------------------------------------- KITCHEN (L-counter north + east, oven tower SW)
k_x0, k_x1, k_y0, k_y1 = X(935), X(1137), Y(568), Y(745)
box_m("K_counterN_base", k_x0 + 0.65, k_y0 - 0.6, 0.1, k_x1, k_y0, 0.86, "grey_cab", "Furniture", collide=True)
box_m("K_counterE_base", k_x1 - 0.6, k_y1 + 0.02, 0.1, k_x1, k_y0 - 0.6, 0.86, "grey_cab", "Furniture", collide=True)
box_m("K_topN", k_x0 + 0.65, k_y0 - 0.62, 0.86, k_x1, k_y0, 0.9, "marble_white", "Furniture")
box_m("K_topE", k_x1 - 0.62, k_y1 + 0.02, 0.86, k_x1, k_y0 - 0.62, 0.9, "marble_white", "Furniture")
box_m("K_plinth", k_x0 + 0.65, k_y0 - 0.55, 0, k_x1, k_y0, 0.1, "black_matte", "Furniture")
box_m("K_splashN", k_x0 + 0.65, k_y0 - 0.01, 0.9, k_x1, k_y0, 1.5, "marble_white", "Decor")
box_m("K_splashE", k_x1 - 0.01, k_y1 + 0.02, 0.9, k_x1, k_y0, 1.5, "marble_white", "Decor")
box_m("K_greyE", k_x1 - 0.012, k_y1 + 0.02, 1.5, k_x1 - 0.002, k_y0, H, "marble_grey", "Decor")
box_m("K_uppers", k_x0 + 0.65, k_y0 - 0.36, 1.5, k_x1 - 0.65, k_y0, 2.25, "yellow_glass", "Furniture")
for i in range(6):
    ux = k_x0 + 0.65 + i * ((k_x1 - 0.65) - (k_x0 + 0.65)) / 5
    box_m(f"K_upperframe{i}", ux - 0.015, k_y0 - 0.375, 1.5, ux + 0.015, k_y0 - 0.355, 2.25, "black_matte", "Furniture")
box_m("K_upperframe_b", k_x0 + 0.65, k_y0 - 0.375, 1.48, k_x1 - 0.65, k_y0 - 0.355, 1.51, "black_matte", "Furniture")
box_m("K_upperframe_t", k_x0 + 0.65, k_y0 - 0.375, 2.24, k_x1 - 0.65, k_y0 - 0.355, 2.27, "black_matte", "Furniture")
box_m("K_sink", k_x0 + 1.0, k_y0 - 0.5, 0.88, k_x0 + 1.55, k_y0 - 0.12, 0.905, "black_gloss", "Furniture")
cyl("K_tap", k_x0 + 1.27, k_y0 - 0.08, 0.9, 0.015, 0.32, "black_matte", verts=8)
box_m("K_hob", k_x1 - 0.55, Y(700), 0.9, k_x1 - 0.05, Y(665), 0.91, "black_gloss", "Furniture")
box_m("K_hood", k_x1 - 0.45, Y(700), 1.65, k_x1, Y(665), 2.1, "black_matte", "Furniture")
box_m("K_oven_tower", k_x0 + 0.02, k_y1 + 0.02, 0, k_x0 + 0.62, k_y1 + 0.62, 2.3, "grey_cab", "Furniture", collide=True)
box_m("K_oven", k_x0 + 0.62, k_y1 + 0.12, 0.9, k_x0 + 0.63, k_y1 + 0.52, 1.5, "black_gloss", "Furniture")
box_m("K_under_led", k_x0 + 0.65, k_y0 - 0.37, 1.47, k_x1 - 0.65, k_y0 - 0.33, 1.48, "led", "Decor")
# utility: washer + sink
box_m("U_washer", X(1080), Y(842) + 0.02, 0, X(1132), Y(800), 0.85, "white_matte", "Furniture", collide=True)
box_m("U_sink", X(1080), Y(800), 0.75, X(1132), Y(760), 0.85, "steel", "Furniture", collide=True)

# ---------------------------------------------------------------- BEDROOM (video BR1 = plan Bedroom 2, NE): oak + chevron headboard
b_x0, b_x1, b_y0, b_y1 = X(1057), X(1313), Y(172), Y(452)
bed_cy = Y(305)
box_m("BR2_backpanel", b_x1 - 0.03, Y(440), 0, b_x1, Y(185), 1.15, "oak", "Decor")
box_m("BR2_paper", b_x1 - 0.012, Y(450), 1.15, b_x1 - 0.002, Y(174), H, "br2_wallpaper", "Decor")
box_c("BR2_headboard", b_x1 - 0.06, bed_cy, 0.45, 0.06, 1.9, 0.75, "chevron", bevel=0.01)
box_c("BR2_bedbase", b_x1 - 1.1, bed_cy, 0.12, 2.05, 1.95, 0.28, "oak", collide=True)
box_c("BR2_mattress", b_x1 - 1.08, bed_cy, 0.4, 1.95, 1.85, 0.2, "fabric_bedgrey", bevel=0.04)
box_c("BR2_throw", b_x1 - 1.55, bed_cy, 0.45, 1.0, 1.95, 0.18, "fabric_bedgrey", bevel=0.05)
for s in (-1, 1):
    box_c(f"BR2_pillow{s}", b_x1 - 0.28, bed_cy + s * 0.45, 0.58, 0.35, 0.7, 0.14, "fabric_bedgrey", bevel=0.05)
    box_c(f"BR2_side{s}", b_x1 - 0.22, bed_cy + s * 1.25, 0.45, 0.42, 0.45, 0.08, "oak")
art("BR2_art", b_x1 - 0.03, bed_cy, 1.95, 1.6, 0.85, "art_sticks", "W")
box_m("BR2_wardrobe", X(1120), b_y1, 0, b_x1, b_y1 + 0.6, 2.6, "oak", "Furniture", collide=True)
box_m("BR2_wardrobe_loft", X(1120), b_y1, 2.6, b_x1, b_y1 + 0.6, H - 0.01, "oak", "Furniture")
for i in range(4):
    hx = X(1120) + (i + 0.5) * (b_x1 - X(1120)) / 4 + (0.05 if i % 2 == 0 else -0.05)
    box_m(f"BR2_handle{i}", hx - 0.01, b_y1 + 0.6, 0.7, hx + 0.01, b_y1 + 0.63, 1.5, "black_matte", "Furniture")
box_m("BR2_dresser", b_x0, Y(275), 0.72, b_x0 + 0.45, Y(190), 0.78, "oak", "Furniture")
box_m("BR2_dresser_box", b_x0, Y(275), 0.55, b_x0 + 0.45, Y(190), 0.72, "oak", "Furniture")
box_m("BR2_wallcab", b_x0, Y(275), 1.75, b_x0 + 0.35, Y(190), 2.15, "oak", "Furniture")
COLLIDERS.append([b_x0, Y(275), b_x0 + 0.45, Y(190)])
curtain("BR2_curtL", X(1100), Y(176), X(1125), Y(176), 0.02, 2.62, "curtain_grey", folds=4, amp=0.05)
curtain("BR2_curtR", X(1245), Y(176), X(1270), Y(176), 0.02, 2.62, "curtain_grey", folds=4, amp=0.05)
box_c("AC_br2", b_x0 + 0.13, Y(300), 2.42, 0.22, 0.95, 0.3, "ac", "Decor")

# ---------------------------------------------------------------- BEDROOM (video BR2 = plan Bedroom 3): dark channel headboard
c_x0, c_x1, c_y0, c_y1 = X(378), X(635), Y(172), Y(462)
bed3 = Y(300)
box_m("BR3_darkwall", c_x0, Y(455), 0, c_x0 + 0.015, Y(176), H, "paint_darkgrey", "Decor")
box_m("BR3_channel", c_x0, bed3 - 1.15, 0.5, c_x0 + 0.08, bed3 + 1.15, 1.45, "channel_dark", "Decor")
box_m("BR3_cream", c_x0, bed3 - 1.15, 1.45, c_x0 + 0.06, bed3 + 1.15, 2.55, "white_matte", "Decor")
box_m("BR3_cream_led", c_x0 + 0.06, bed3 - 1.15, 1.45, c_x0 + 0.065, bed3 + 1.15, 1.47, "led", "Decor")
art("BR3_art", c_x0 + 0.075, bed3, 2.0, 1.05, 0.6, "art_frame_br3", "E")
box_c("BR3_bedbase", c_x0 + 1.1, bed3, 0.05, 2.0, 1.7, 0.35, "grey_cab", collide=True)
box_c("BR3_mattress", c_x0 + 1.12, bed3, 0.4, 1.95, 1.62, 0.2, "fabric_white", bevel=0.04)
box_c("BR3_throw", c_x0 + 1.55, bed3, 0.45, 0.9, 1.7, 0.18, "fabric_sofa", bevel=0.05)
for s in (-1, 1):
    box_c(f"BR3_pillow{s}", c_x0 + 0.3, bed3 + s * 0.4, 0.6, 0.35, 0.62, 0.14, "fabric_white", bevel=0.05)
    box_c(f"BR3_side{s}", c_x0 + 0.2, bed3 + s * 1.05, 0.45, 0.38, 0.4, 0.06, "oak")
box_m("BR3_wardrobe", c_x0, c_y1, 0, X(565), c_y1 + 0.62, H - 0.01, "white_gloss", "Furniture", collide=True)
box_m("BR3_wardrobe_band", c_x0, c_y1 + 0.62, 1.95, X(565), c_y1 + 0.625, 2.1, "grey_cab", "Furniture")
box_m("BR3_desk", c_x1 - 0.5, Y(300), 0.72, c_x1, Y(190), 0.76, "white_matte", "Furniture")
box_m("BR3_shelf", c_x1 - 0.3, Y(300), 1.6, c_x1, Y(190), 1.63, "oak", "Furniture")
curtain("BR3_curtL", X(452), Y(176), X(480), Y(176), 0.02, 2.62, "curtain_grey", folds=4, amp=0.05)
curtain("BR3_curtR", X(545), Y(176), X(572), Y(176), 0.02, 2.62, "curtain_grey", folds=4, amp=0.05)

# ---------------------------------------------------------------- MASTER (wood floor, beige channel headboard, orange prints)
m_x0, m_x1, m_y0, m_y1 = X(55), X(365), Y(297), Y(597)
mb = Y(425)
box_m("MB_panel", m_x0, mb - 1.2, 0, m_x0 + 0.03, mb + 1.2, 2.55, "panel_greywood", "Decor")
box_m("MB_grey", m_x0, m_y1 + 0.02, 0, m_x0 + 0.012, m_y0, H, "grey_wall", "Decor")
box_m("MB_slatsTop", m_x0, mb - 1.2, 2.55, m_x0 + 0.05, mb + 1.2, H - 0.01, "slats", "Decor")
box_m("MB_headboard", m_x0 + 0.03, mb - 1.0, 0.45, m_x0 + 0.12, mb + 1.0, 1.15, "channel_beige", "Furniture")
box_c("MB_bedbase", m_x0 + 1.15, mb, 0.08, 2.1, 1.95, 0.22, "oak", collide=True)
box_c("MB_mattress", m_x0 + 1.15, mb, 0.3, 2.0, 1.85, 0.24, "fabric_white", bevel=0.04)
box_c("MB_throw", m_x0 + 1.75, mb, 0.4, 0.8, 1.95, 0.16, "fabric_black", bevel=0.05)
for s in (-1, 1):
    box_c(f"MB_side{s}", m_x0 + 0.22, mb + s * 1.2, 0.5, 0.4, 0.38, 0.05, "oak")
art("MB_art_l", m_x0 + 0.045, mb + 0.32, 1.85, 0.52, 0.85, "art_orange_l", "E")
art("MB_art_r", m_x0 + 0.045, mb - 0.32, 1.85, 0.48, 0.85, "art_orange_r", "E")
box_m("MB_wardrobe", m_x0, m_y1, 0, X(313), m_y1 + 0.62, H - 0.01, "white_gloss", "Furniture", collide=True)
for i, xx in enumerate([0.9, 1.0, 2.6, 2.7]):
    box_m(f"MB_wstrip{i}", m_x0 + xx, m_y1 + 0.62, 0, m_x0 + xx + 0.1, m_y1 + 0.625, H - 0.01, "fabric_black", "Furniture")
for i, xx in enumerate([1.08, 2.52]):
    box_m(f"MB_whandle{i}", m_x0 + xx, m_y1 + 0.625, 0.8, m_x0 + xx + 0.03, m_y1 + 0.65, 1.6, "copper", "Furniture")
box_m("MB_desk", m_x1 - 0.5, Y(420), 0.72, m_x1, Y(320), 0.76, "white_matte", "Furniture")
box_m("MB_desk_box", m_x1 - 0.5, Y(420), 0.6, m_x1, Y(320), 0.72, "white_matte", "Furniture")
box_m("MB_cove", m_x1 - 0.02, Y(330), 0.8, m_x1 - 0.01, Y(325), 2.6, "led", "Decor")
COLLIDERS.append([m_x1 - 0.5, Y(420), m_x1, Y(320)])
curtain("MB_blind", m_x0 + 0.02, Y(296), m_x0 + 0.02, Y(360), 1.6, 2.1, "white_matte", folds=3, amp=0.02)
curtain("MB_curt_bal", X(160), Y(292), X(182), Y(292), 0.02, 2.62, "curtain_beige", folds=3, amp=0.05)
box_c("AC_mb", m_x1 - 0.12, Y(480), 2.42, 0.22, 0.95, 0.3, "ac", "Decor")

# ---------------------------------------------------------------- BATHROOMS
def bathroom(n, px0, py0, px1, py1, wc_side, vanity_side):
    x0, x1, y0, y1 = X(px0), X(px1), Y(py0), Y(py1)  # y0 > y1
    t = 0.008
    box_m(n + "_tileN", x0, y0 - t, 0, x1, y0, 2.4, "bath_tile", "Decor")
    box_m(n + "_tileS", x0, y1, 0, x1, y1 + t, 2.4, "bath_tile_light", "Decor")
    box_m(n + "_tileW", x0, y1, 0, x0 + t, y0, 2.4, "bath_tile_light", "Decor")
    box_m(n + "_tileE", x1 - t, y1, 0, x1, y0, 2.4, "bath_tile", "Decor")
    # wall-hung WC + concealed cistern panel
    if wc_side == "N": cx, cy, r = (x0 + x1) / 2 - 0.3, y0 - 0.32, 90
    elif wc_side == "W": cx, cy, r = x0 + 0.32, (y0 + y1) / 2, 0
    else: cx, cy, r = x1 - 0.32, (y0 + y1) / 2 + 0.2, 0
    box_c(n + "_wc", cx, cy, 0.3, 0.55, 0.38, 0.12, "porcelain", rot=r, bevel=0.06)
    box_c(n + "_wcbowl", cx, cy, 0.18, 0.45, 0.32, 0.14, "porcelain", rot=r, bevel=0.08)
    # vanity: wood cabinet + white basin
    if vanity_side == "S": vx, vy, vr = (x0 + x1) / 2 + 0.3, y1 + 0.25, 0
    elif vanity_side == "E": vx, vy, vr = x1 - 0.25, y1 + 0.45, 90
    else: vx, vy, vr = x0 + 0.25, y0 - 0.45, 90
    box_c(n + "_vanity", vx, vy, 0.45, 0.8, 0.46, 0.4, "walnut", rot=vr, collide=True)
    box_c(n + "_basin", vx, vy, 0.85, 0.8, 0.48, 0.06, "porcelain", rot=vr, bevel=0.01)
    plant_free = None
bathroom("T1", 192, 172, 365, 288, "N", "W")
bathroom("T2", 935, 172, 1047, 378, "W", "S")
bathroom("T3", 325, 564, 437, 745, "E", "S")
box_m("T3_glass", X(330), Y(660), 0, X(437), Y(658), 2.1, "glass", "Decor")
box_m("T2_glass", X(940), Y(250), 0, X(1047), Y(248), 2.1, "glass", "Decor")

# ---------------------------------------------------------------- ceiling downlights (emissive discs)
DOWNLIGHTS = [
    (790, 260), (790, 400), (700, 330), (880, 330),          # living
    (590, 600), (590, 700), (750, 650), (850, 650),          # dining/family
    (1040, 510), (1100, 510),                                # foyer
    (1036, 620), (1036, 700),                                # kitchen
    (1185, 260), (1185, 380), (1100, 320),                   # BR2
    (505, 260), (505, 390),                                  # BR3
    (210, 380), (210, 520), (310, 450),                      # master
    (278, 230), (990, 275), (380, 655),                      # toilets
    (1280, 520), (420, 515),
]
for i, (px, py) in enumerate(DOWNLIGHTS):
    cyl(f"Downlight{i}", X(px), Y(py), H - 0.012, 0.045, 0.01, "led", "Ceiling", verts=16)

# ---------------------------------------------------------------- exterior surroundings (building shell + greenery)
box_m("Ground", -20, -25, -3.1, 35, 20, -3.05, "lawn", "Exterior")
box_m("Facade_below", X(45), Y(752), -3.05, X(1325), Y(160), -0.2, "paint_ext", "Exterior")
for i, (gx, gy) in enumerate([(-3, 6), (8, 6.5), (16, 6.5), (-4, -4), (21, 2), (2, 7)]):
    cyl(f"TreeTrunk{i}", gx, gy, -3.05, 0.15, 3.0, "walnut", "Exterior", verts=8)
    me = bpy.data.meshes.new(f"Tree{i}"); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.8); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(f"Tree{i}", me); o.data.materials.append(MATS["plant"]); o.location = (gx, gy, 1.4); o.scale = (1, 1, 1.3)
    coll("Exterior").objects.link(o)
# neighbour tower suggestion to the east and west (stays out of the way)
box_m("Neighbour_E", 25, -14, -3.05, 34, 4, 30, "paint_ext", "Exterior")

# ---------------------------------------------------------------- write collision + metadata
spawn = {"x": X(1250), "y": Y(522), "z": 0, "yaw_deg": 180}
meta = {"scale_px_per_m": S, "ceiling": H, "spawn": spawn,
        "colliders": [[round(v, 3) for v in c] for c in COLLIDERS],
        "rooms": {
            "Living": [X(649), Y(462), X(922), Y(172)], "Family & Dining": [X(450), Y(745), X(922), Y(470)],
            "Foyer": [X(935), Y(562), X(1137), Y(462)], "Kitchen": [X(935), Y(745), X(1137), Y(568)],
            "Utility": [X(935), Y(842), X(1137), Y(752)], "Bedroom 2": [X(1057), Y(452), X(1313), Y(172)],
            "Bedroom 3": [X(378), Y(462), X(635), Y(172)], "Master Bedroom": [X(55), Y(597), X(365), Y(297)],
            "Toilet 1": [X(192), Y(288), X(365), Y(172)], "Toilet 2": [X(935), Y(378), X(1047), Y(172)],
            "Toilet 3": [X(325), Y(745), X(437), Y(564)], "Entrance": [X(1150), Y(583), X(1410), Y(462)],
            "Balcony": [X(415), Y(160), X(880), Y(75)], "Bedroom 2 Balcony": [X(1057), Y(160), X(1313), Y(78)],
            "Master Balcony": [X(55), Y(288), X(180), Y(160)]},
        "lights": [[round(X(px), 3), round(Y(py), 3)] for px, py in DOWNLIGHTS]}
with open(os.path.join(ROOT, "layout.json"), "w") as f:
    json.dump(meta, f)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "A105_raw.blend"))
print("BUILD OK", len(bpy.data.objects), "objects", len(COLLIDERS), "colliders")
