# Realism pass for A-105, run inside build_v2.py (shares its globals).
# Ceiling fans and split ACs in every living space, the three bathrooms fitted out to the plan
# (wall-hung WC with health faucet, vessel basin on a floating vanity, walk-in shower behind glass),
# kitchen fridge, utility sink, dining place settings, fruit bowl, switch plates, and the balcony sit-out
# with a steaming cup of coffee.
import bmesh

mat("ac_white", (0.90, 0.90, 0.88), rough=0.35, coat=0.1)
mat("ac_grille", (0.55, 0.55, 0.54), rough=0.5)
mat("fan_black", (0.03, 0.03, 0.032), rough=0.4, metal=0.3)
mat("terry_white", (0.90, 0.88, 0.84), normal="wool_n.png", nstr=0.6, tile=0.3, rough=1.0, sheen=0.4)
mat("terry_sand", (0.68, 0.60, 0.50), normal="wool_n.png", nstr=0.6, tile=0.3, rough=1.0, sheen=0.4)
mat("coffee", (0.045, 0.022, 0.010), rough=0.05, coat=0.6)
mat("switch_glass", (0.02, 0.02, 0.022), rough=0.05, coat=0.8)
mat("steel", (0.80, 0.80, 0.82), rough=0.22, metal=1.0)
mat("fruit_orange", (0.80, 0.33, 0.04), rough=0.4, coat=0.2)
mat("fruit_green", (0.36, 0.55, 0.09), rough=0.35, coat=0.3)
mat("fruit_red", (0.55, 0.05, 0.04), rough=0.3, coat=0.4)
mat("shower_floor", (0.30, 0.29, 0.28), tex="stone_grey.jpg", tile=0.6, rough=0.4)
# steam: a soft volume whose wisps thin out as they rise
steam = bpy.data.materials.new("steam"); steam.use_nodes = True; snt = steam.node_tree
for nd in list(snt.nodes):
    if nd.type == 'BSDF_PRINCIPLED': snt.nodes.remove(nd)
vol = snt.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Color"].default_value = (0.95, 0.95, 0.95, 1)
tcs = snt.nodes.new("ShaderNodeTexCoord"); sep = snt.nodes.new("ShaderNodeSeparateXYZ")
snt.links.new(tcs.outputs["Generated"], sep.inputs[0])
nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 55.0; nz.inputs["Detail"].default_value = 3.0
mp = snt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 0.35)
snt.links.new(tcs.outputs["Object"], mp.inputs["Vector"]); snt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
cr = snt.nodes.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.42; cr.inputs["From Max"].default_value = 0.62
snt.links.new(nz.outputs["Fac"], cr.inputs["Value"])
fade = snt.nodes.new("ShaderNodeMath"); fade.operation = 'SUBTRACT'; fade.inputs[0].default_value = 1.0
snt.links.new(sep.outputs["Z"], fade.inputs[1])
fade2 = snt.nodes.new("ShaderNodeMath"); fade2.operation = 'POWER'; fade2.inputs[1].default_value = 1.6
snt.links.new(fade.outputs[0], fade2.inputs[0])
dm = snt.nodes.new("ShaderNodeMath"); dm.operation = 'MULTIPLY'
snt.links.new(cr.outputs["Result"], dm.inputs[0]); snt.links.new(fade2.outputs[0], dm.inputs[1])
dm2 = snt.nodes.new("ShaderNodeMath"); dm2.operation = 'MULTIPLY'; dm2.inputs[1].default_value = 28.0
snt.links.new(dm.outputs[0], dm2.inputs[0]); snt.links.new(dm2.outputs[0], vol.inputs["Density"])
snt.links.new(vol.outputs[0], snt.nodes["Material Output"].inputs["Volume"])
MATS["steam"] = steam; steam["tile"] = 1.0

FACE_ROT = {"E": 0, "N": 90, "W": 180, "S": -90}

FIN = 0.011     # bathroom walls carry a 1 cm stone/marble finish layer
def group(name, x, y, z=0.0, face="E", cname="Furniture", inset=0.0):
    """An empty on a wall: local +X points into the room, local Y runs along the wall."""
    a_ = math.radians(FACE_ROT[face]); x += math.cos(a_) * inset; y += math.sin(a_) * inset
    e = bpy.data.objects.new(name, None); e.location = (x, y, z); e.rotation_euler = (0, 0, math.radians(FACE_ROT[face]))
    coll(cname).objects.link(e); return e

def adopt(parent, objs):
    for o in objs:
        o.parent = parent

def lathe(name, prof, material, cname="Decor", seg=48, sx=1.0, sy=1.0):
    """Surface of revolution from a (radius, height) profile; elliptical with sx/sy."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    rings = []
    for (r, z) in prof:
        if r < 1e-6: rings.append([bm.verts.new((0, 0, z))])
        else: rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg) * sx, r * math.sin(2 * math.pi * i / seg) * sy, z)) for i in range(seg)])
    for k, (a, b) in enumerate(zip(rings[:-1], rings[1:])):
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1 and len(b) == 1: break
            if len(a) == 1: vs = [a[0], b[j], b[i]]
            elif len(b) == 1: vs = [a[i], a[j], b[0]]
            else: vs = [a[i], a[j], b[j], b[i]]
            try: f = bm.faces.new(vs)
            except ValueError: continue
            for l in f.loops:
                p = l.vert.co; l[uvl].uv = (math.atan2(p.y, p.x) / 6.283 + 0.5, k / len(prof))
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    coll(cname).objects.link(o); return o

def world_rect(cx, cy, hx, hy, face):
    """Axis-aligned collider for a fixture centred hx out from a wall, half-width hy along it."""
    if face in ("E", "W"):
        s = 1 if face == "E" else -1
        return [min(cx, cx + s * 2 * hx), cy - hy, max(cx, cx + s * 2 * hx), cy + hy]
    s = 1 if face == "N" else -1
    return [cx - hy, min(cy, cy + s * 2 * hx), cx + hy, max(cy, cy + s * 2 * hx)]

# ---------------------------------------------------------------- ceiling fans (blades turn in the walk)
def fan(n, px, py, R=0.6):
    x, y = X(px), Y(py)
    cyl(n + "_canopy", x, y, H - 0.07, 0.075, 0.07, "fan_black", "Decor", 32)
    cyl(n + "_rod", x, y, H - 0.40, 0.012, 0.34, "fan_black", "Decor", 12)
    g = bpy.data.objects.new("FanRot_" + n, None); g.location = (x, y, H - 0.47); coll("Fans").objects.link(g)
    parts = [cyl(n + "_motor", 0, 0, -0.05, 0.13, 0.10, "fan_black", "Fans", 40),
             cyl(n + "_trim", 0, 0, -0.012, 0.135, 0.012, "brass_brushed", "Fans", 40),
             cyl(n + "_cap", 0, 0, -0.075, 0.075, 0.025, "brass_brushed", "Fans", 32)]
    for k in range(3):
        a = k * 2 * math.pi / 3
        bl = box(f"{n}_blade{k}", 0.16, -0.065, -0.006, R, 0.065, 0.006, "walnut", "Fans", bevel=0.004, seg=2)
        bl.rotation_euler = (math.radians(9), 0, a)
        br = box(f"{n}_iron{k}", 0.10, -0.022, -0.02, 0.24, 0.022, -0.004, "fan_black", "Fans")
        br.rotation_euler = (0, 0, a)
        parts += [bl, br]
    adopt(g, parts)

fan("FanLiving", 776, 425)
fan("FanDining", 740, 650)
fan("FanBR2", 1185, 315)
fan("FanBR3", 507, 315)
fan("FanMaster", 205, 435)

# ---------------------------------------------------------------- split air conditioners
def ac(n, x, y, face, w=0.96):
    g = group(n, x, y, 0, face, "Furniture")
    parts = [box(n + "_body", 0.0, -w / 2, 2.25, 0.21, w / 2, 2.55, "ac_white", "Furniture", bevel=0.025, seg=3),
             box(n + "_face", 0.205, -w / 2 + 0.02, 2.34, 0.214, w / 2 - 0.02, 2.53, "ac_white", "Furniture", bevel=0.004),
             box(n + "_vent", 0.12, -w / 2 + 0.06, 2.248, 0.20, w / 2 - 0.06, 2.252, "ac_grille", "Furniture"),
             box(n + "_flap", 0.17, -w / 2 + 0.06, 2.27, 0.225, w / 2 - 0.06, 2.285, "ac_grille", "Furniture", bevel=0.003),
             box(n + "_led", 0.214, w / 2 - 0.16, 2.47, 0.216, w / 2 - 0.10, 2.49, "led_soft", "Furniture")]
    adopt(g, parts)

ac("AC_Living", X(922), Y(212), "W")
ac("AC_Dining", X(890), Y(745), "N")
ac("AC_BR2", X(1057), Y(235), "E")
ac("AC_BR3", X(635), Y(380), "W")
ac("AC_Master", X(365), Y(445), "W")

# ---------------------------------------------------------------- bathrooms, laid out as on the plan
def wc(n, x, y, face, tp_side=-1):
    g = group(n, x, y, 0, face, "Furniture", FIN)
    parts = [lathe(n + "_bowl", [(0.11, 0.0), (0.165, 0.05), (0.18, 0.13), (0.182, 0.20), (0.178, 0.215), (0.15, 0.215), (0.13, 0.15), (0.07, 0.11), (0.0, 0.10)], "porcelain", "Furniture", 48, 1.42, 1.0),
             lathe(n + "_seat", [(0.0, 0.0), (0.17, 0.0), (0.182, 0.012), (0.176, 0.03), (0.0, 0.036)], "porcelain", "Furniture", 48, 1.42, 1.0),
             box(n + "_back", 0.0, -0.16, 0.20, 0.12, 0.16, 0.44, "porcelain", "Furniture", bevel=0.03),
             box(n + "_flush", 0.0, -0.12, 0.98, 0.01, 0.12, 1.14, "switch_glass", "Decor"),
             box(n + "_flushA", 0.010, -0.10, 1.00, 0.014, -0.006, 1.12, "brass_brushed", "Decor"),
             box(n + "_flushB", 0.010, 0.006, 1.00, 0.014, 0.10, 1.12, "brass_brushed", "Decor"),
             # health faucet beside the WC
             box(n + "_hfhold", 0.0, 0.33, 0.70, 0.04, 0.37, 0.76, "chrome", "Decor"),
             cyl(n + "_hfhead", 0.05, 0.35, 0.62, 0.016, 0.16, "chrome", "Decor", 16),
             tube(n + "_hfhose", [(0.0, 0.40, 0.45), (0.05, 0.42, 0.30), (0.06, 0.38, 0.45), (0.05, 0.35, 0.62)], 0.006, "chrome", "Decor", 8),
             ]
    if tp_side:
        ty_ = 0.40 if tp_side < 0 else 0.47
        parts += [box(n + "_tp", 0.0, tp_side * ty_ - 0.01, 0.68, 0.06, tp_side * ty_ + 0.01, 0.70, "chrome", "Decor"),
                  cyl(n + "_tproll", 0.06, tp_side * ty_ - 0.05, 0.64, 0.055, 0.10, "terry_white", "Decor", 24, rot=(-90, 0, 0))]
    parts[0].location = (0.30, 0, 0.19); parts[1].location = (0.30, 0, 0.405)
    adopt(g, parts)
    COLLIDERS.append(world_rect(x, y, 0.29, 0.2, face))

def vanity(n, x, y, face, length=0.9, ring_side=1):
    g = group(n, x, y, 0, face, "Furniture", FIN)
    L = length / 2
    parts = [box(n + "_cab", 0.0, -L, 0.42, 0.50, L, 0.82, "walnut", "Furniture", bevel=0.01),
             box(n + "_groove", 0.495, -L + 0.02, 0.70, 0.505, L - 0.02, 0.72, "brass_brushed", "Furniture"),
             box(n + "_top", 0.0, -L - 0.01, 0.82, 0.52, L + 0.01, 0.85, "marble_counter", "Furniture", bevel=0.004),
             box(n + "_glow", 0.03, -L + 0.03, 0.415, 0.47, L - 0.03, 0.42, "led_soft", "Furniture"),
             lathe(n + "_basin", [(0.12, 0.0), (0.185, 0.03), (0.20, 0.10), (0.20, 0.13), (0.187, 0.13), (0.175, 0.06), (0.10, 0.025), (0.0, 0.02)], "porcelain", "Furniture", 56),
             cyl(n + "_drain", 0.27, 0.06, 0.871, 0.022, 0.002, "brass", "Decor", 16),
             cyl(n + "_mixer", 0.07, 0.06, 0.85, 0.017, 0.29, "brass", "Decor", 16),
             tube(n + "_spout", [(0.07, 0.06, 1.13), (0.13, 0.06, 1.165), (0.205, 0.06, 1.13)], 0.011, "brass", "Decor", 12),
             box(n + "_lever", 0.05, 0.06 - 0.008, 1.02, 0.115, 0.06 + 0.008, 1.035, "brass", "Decor"),
             cyl(n + "_soap", 0.14, -L + 0.14, 0.85, 0.035, 0.15, "ceramic_black", "Decor", 20),
             cyl(n + "_pump", 0.14, -L + 0.14, 1.0, 0.009, 0.04, "brass", "Decor", 10),
             cyl(n + "_dish", 0.16, -L + 0.26, 0.85, 0.055, 0.012, "travertine", "Decor", 24),
             # backlit round mirror above the basin
             torus(n + "_mglow", 0.014, 0.06, 1.62, 0.31, 0.012, "led_soft", "Decor", rot=(0, 90, 0)),
             cyl(n + "_mrim", 0.002, 0.06, 1.62, 0.33, 0.02, "brass", "Decor", 64, rot=(0, 90, 0)),
             cyl(n + "_mir", 0.006, 0.06, 1.62, 0.31, 0.02, "mirror", "Decor", 64, rot=(0, 90, 0)),
             # hand towel on a ring beside the vanity
             torus(n + "_ring", 0.03, ring_side * (L + 0.14), 1.05, 0.09, 0.008, "brass", "Decor", rot=(0, 90, 0)),
             box(n + "_htowel", 0.015, ring_side * (L + 0.06), 0.70, 0.05, ring_side * (L + 0.22), 1.0, "terry_sand", "Decor", bevel=0.012, seg=3)]
    parts[4].location = (0.27, 0.06, 0.85)
    adopt(g, parts)
    COLLIDERS.append(world_rect(x, y, 0.26, L, face))

def shower(n, zone, glass, head, mixer_wall, mixer_at, rail_at, exhaust):
    """zone (px0,py0,px1,py1): shower floor; glass ((pxa,pya),(pxb,pyb)) fixed panel;
    head (px,py): rain head under the ceiling; mixer_wall: 'N','S','E','W' wall that carries the mixer,
    mixer_at / rail_at: plan coords along that wall; exhaust (px,py,face)."""
    px0, py0, px1, py1 = zone
    box(n + "_floor", X(px0) + FIN, Y(py1) + FIN, 0.006, X(px1) - FIN, Y(py0) - FIN, 0.010, "shower_floor", "Floors")
    # linear drain along the back of the zone
    if mixer_wall in ("N", "S"):
        yy = Y(py0) - 0.08 if mixer_wall == "N" else Y(py1) + 0.08
        box(n + "_drain", X(px0) + 0.1, yy - 0.03, 0.010, X(px1) - 0.1, yy + 0.03, 0.013, "steel", "Decor")
    else:
        xx = X(px0) + 0.08 if mixer_wall == "W" else X(px1) - 0.08
        box(n + "_drain", xx - 0.03, Y(py1) + 0.1, 0.006, xx + 0.03, Y(py0) - 0.1, 0.013, "steel", "Decor")
    (xa, ya), (xb, yb) = (X(glass[0][0]), Y(glass[0][1])), (X(glass[1][0]), Y(glass[1][1]))
    if abs(xa - xb) > abs(ya - yb):   # panel runs along x
        box(n + "_glass", min(xa, xb), ya - 0.005, 0.01, max(xa, xb), ya + 0.005, 2.05, "glass", "Decor")
        box(n + "_chan", min(xa, xb), ya - 0.012, 0.0, max(xa, xb), ya + 0.012, 0.03, "black_metal", "Decor")
        box(n + "_bar", min(xa, xb), ya - 0.01, 2.04, max(xa, xb), ya + 0.01, 2.07, "black_metal", "Decor")
        box(n + "_edge", max(xa, xb) - 0.015, ya - 0.012, 0.0, max(xa, xb), ya + 0.012, 2.07, "black_metal", "Decor")
    else:
        box(n + "_glass", xa - 0.005, min(ya, yb), 0.01, xa + 0.005, max(ya, yb), 2.05, "glass", "Decor")
        box(n + "_chan", xa - 0.012, min(ya, yb), 0.0, xa + 0.012, max(ya, yb), 0.03, "black_metal", "Decor")
        box(n + "_bar", xa - 0.01, min(ya, yb), 2.04, xa + 0.01, max(ya, yb), 2.07, "black_metal", "Decor")
        box(n + "_edge", xa - 0.012, min(ya, yb), 0.0, xa + 0.012, min(ya, yb) + 0.015, 2.07, "black_metal", "Decor")
    hx, hy = X(head[0]), Y(head[1])
    box(n + "_rain", hx - 0.15, hy - 0.15, H - 0.33, hx + 0.15, hy + 0.15, H - 0.315, "black_metal", "Decor", bevel=0.004)
    box(n + "_rainface", hx - 0.14, hy - 0.14, H - 0.332, hx + 0.14, hy + 0.14, H - 0.33, "chrome", "Decor")
    cyl(n + "_rainrod", hx, hy, H - 0.315, 0.01, 0.315, "black_metal", "Decor", 12)
    # thermostatic mixer and hand shower on the wall
    if mixer_wall in ("E", "W"):
        wx = X(px1) - FIN if mixer_wall == "E" else X(px0) + FIN; s = -1 if mixer_wall == "E" else 1
        my, ry = Y(mixer_at), Y(rail_at)
        cyl(n + "_mixplate", wx - (0.012 if s < 0 else 0), my, 1.05, 0.075, 0.012, "black_metal", "Decor", 40, rot=(0, 90, 0))
        box(n + "_mixlever", wx + s * 0.012, my - 0.008, 1.05, wx + s * 0.06, my + 0.008, 1.065, "brass", "Decor")
        cyl(n + "_rail", wx + s * 0.04, ry, 0.95, 0.012, 0.8, "black_metal", "Decor", 12)
        cyl(n + "_hand", wx + s * 0.06, ry, 1.45, 0.028, 0.22, "black_metal", "Decor", 16, rot=(0, 18 * s, 0))
        tube(n + "_hose", [(wx + s * 0.02, ry + 0.05, 0.9), (wx + s * 0.08, ry + 0.08, 0.55), (wx + s * 0.07, ry + 0.02, 1.0), (wx + s * 0.06, ry, 1.34)], 0.006, "black_metal", "Decor", 8)
        box(n + "_niche", wx, ry - 0.45, 1.20, wx + s * 0.12, ry - 0.15, 1.212, "marble_counter", "Decor")
        cyl(n + "_bottle1", wx + s * 0.06, ry - 0.40, 1.212, 0.03, 0.18, "ceramic_white", "Decor", 16)
        cyl(n + "_bottle2", wx + s * 0.06, ry - 0.30, 1.212, 0.028, 0.15, "ceramic_black", "Decor", 16)
        cyl(n + "_bottle3", wx + s * 0.06, ry - 0.21, 1.212, 0.025, 0.13, "travertine", "Decor", 16)
    else:
        wy = Y(py0) - FIN if mixer_wall == "N" else Y(py1) + FIN; s = -1 if mixer_wall == "N" else 1
        mx, rx = X(mixer_at), X(rail_at)
        cyl(n + "_mixplate", mx, wy + (0.012 if s > 0 else 0), 1.05, 0.075, 0.012, "black_metal", "Decor", 40, rot=(90, 0, 0))
        box(n + "_mixlever", mx - 0.008, wy + s * 0.012, 1.05, mx + 0.008, wy + s * 0.06, 1.065, "brass", "Decor")
        cyl(n + "_rail", rx, wy + s * 0.04, 0.95, 0.012, 0.8, "black_metal", "Decor", 12)
        cyl(n + "_hand", rx, wy + s * 0.06, 1.45, 0.028, 0.22, "black_metal", "Decor", 16, rot=(-18 * s, 0, 0))
        box(n + "_niche", rx - 0.45, wy, 1.20, rx - 0.15, wy + s * 0.12, 1.212, "marble_counter", "Decor")
        cyl(n + "_bottle1", rx - 0.40, wy + s * 0.06, 1.212, 0.03, 0.18, "ceramic_white", "Decor", 16)
        cyl(n + "_bottle2", rx - 0.30, wy + s * 0.06, 1.212, 0.028, 0.15, "ceramic_black", "Decor", 16)
    ex, ey, ef = exhaust
    g = group(n + "_exhaust", X(ex), Y(ey), 0, ef, "Decor", FIN)
    adopt(g, [box(n + "_exbody", 0.0, -0.13, 2.28, 0.025, 0.13, 2.54, "ac_white", "Decor", bevel=0.006),
              box(n + "_exgrille", 0.025, -0.10, 2.31, 0.028, 0.10, 2.51, "ac_grille", "Decor")])

def towel_rail(n, x, y, face, z=1.15, w=0.55):
    g = group(n, x, y, 0, face, "Decor", FIN)
    adopt(g, [cyl(n + "_bar", 0.06, -w / 2, z, 0.011, w, "brass", "Decor", 12, rot=(-90, 0, 0)),
              box(n + "_b1", 0.0, -w / 2, z - 0.015, 0.07, -w / 2 + 0.02, z + 0.015, "brass", "Decor"),
              box(n + "_b2", 0.0, w / 2 - 0.02, z - 0.015, 0.07, w / 2, z + 0.015, "brass", "Decor"),
              box(n + "_towel", 0.035, -w / 2 + 0.05, z - 0.62, 0.085, w / 2 - 0.05, z + 0.02, "terry_white", "Decor", bevel=0.015, seg=3)])

def mat_rug(n, px0, py0, px1, py1):
    box(n, X(px0), Y(py1), 0.006, X(px1), Y(py0), 0.02, "terry_white", "Decor", bevel=0.006, seg=2)

# Toilet 1 (master): basin on the west wall, WC on the north wall, walk-in shower along the east wall
wc("T1_wc", X(268), Y(172), "S")
vanity("T1_van", X(192), Y(238), "E", 0.9)
shower("T1_sh", (305, 172, 365, 288), ((305, 172), (305, 250)), (336, 222), "E", 205, 245, (340, 172, "S"))
towel_rail("T1_towel", X(214), Y(288), "N", 1.15, 0.42)
mat_rug("T1_mat", 260, 252, 300, 282)
# Toilet 2: shower across the north end, WC then basin on the west wall
wc("T2_wc", X(935), Y(285), "E", tp_side=1)
vanity("T2_van", X(935), Y(345), "E", 0.75)
shower("T2_sh", (935, 172, 1047, 248), ((935, 248), (1012, 248)), (990, 208), "W", 205, 228, (1030, 172, "S"))
towel_rail("T2_towel", X(1047), Y(278), "W", 1.15, 0.45)
mat_rug("T2_mat", 1000, 252, 1040, 282)
# Toilet 3: basin in the north-west corner, WC on the west wall, shower across the south end
vanity("T3_van", X(325), Y(596), "E", 0.7, ring_side=-1)
wc("T3_wc", X(325), Y(655), "E", tp_side=0)
shower("T3_sh", (325, 680, 437, 745), ((325, 680), (400, 680)), (378, 712), "S", 350, 400, (412, 745, "N"))
towel_rail("T3_towel", X(437), Y(620), "W", 1.15, 0.45)
mat_rug("T3_mat", 400, 646, 432, 676)

# ---------------------------------------------------------------- kitchen: fridge in the north-east corner (as on the plan)
FRX0 = kx1 - 0.716
box("K_fridge", FRX0 + 0.005, ky_n - 0.62, 0.0, kx1 - 0.016, ky_n - 0.02, 1.86, "steel", "Furniture", True, bevel=0.01)
box("K_fridgegap", FRX0 + 0.005, ky_n - 0.623, 0.70, kx1 - 0.016, ky_n - 0.619, 0.71, "black_metal", "Furniture")
box("K_fridgesplit", (FRX0 + kx1) / 2 - 0.002, ky_n - 0.623, 0.71, (FRX0 + kx1) / 2 + 0.002, ky_n - 0.619, 1.86, "black_metal", "Furniture")
for s_ in (-1, 1):
    box(f"K_fridgeh{s_}", (FRX0 + kx1) / 2 + s_ * 0.03 - 0.008, ky_n - 0.66, 0.95, (FRX0 + kx1) / 2 + s_ * 0.03 + 0.008, ky_n - 0.625, 1.55, "brass", "Furniture")
box("K_fridgehB", FRX0 + 0.12, ky_n - 0.66, 0.62, kx1 - 0.14, ky_n - 0.625, 0.636, "brass", "Furniture")
box("K_fridgedisp", FRX0 + 0.07, ky_n - 0.6235, 1.30, FRX0 + 0.25, ky_n - 0.6225, 1.48, "screen", "Furniture")
# fruit bowl, kettle and a board on the counters
fb = lathe("K_fruitbowl", [(0.0, 0.0), (0.08, 0.0), (0.15, 0.05), (0.17, 0.09), (0.16, 0.09), (0.14, 0.055), (0.07, 0.012), (0.0, 0.012)], "ceramic_white", "Decor", 48)
fb.location = (kx1 - 0.32, Y(728), 0.91)
for i, (dx, dy, dz, m_) in enumerate([(-0.05, 0.03, 0.05, "fruit_orange"), (0.05, -0.02, 0.05, "fruit_green"), (0.0, -0.06, 0.06, "fruit_red"),
                                      (0.02, 0.06, 0.09, "fruit_orange"), (-0.06, -0.04, 0.09, "fruit_green")]):
    sphere(f"K_fruit{i}", kx1 - 0.32 + dx, Y(728) + dy, 0.91 + dz, 0.042, m_)
cyl("K_kettle", kx1 - 0.3, Y(632), 0.91, 0.085, 0.2, "steel", "Decor", 32, r2=0.07)
cyl("K_kettlelid", kx1 - 0.3, Y(632), 1.11, 0.05, 0.02, "black_metal", "Decor", 24)
tube("K_kettlespout", [(kx1 - 0.37, Y(632), 1.0), (kx1 - 0.44, Y(632), 1.07)], 0.012, "steel", "Decor", 10)

# ---------------------------------------------------------------- utility: a deep steel sink beside the washer
box("U_sink", X(1086), Y(797), 0.886, X(1128), Y(765), 0.892, "steel", "Furniture")
box("U_sinkbowl", X(1090), Y(794), 0.884, X(1124), Y(768), 0.887, "black_metal", "Furniture")
cyl("U_tap", X(1137) - 0.05, Y(781), 0.89, 0.012, 0.3, "chrome", "Decor", 12)
tube("U_tapspout", [(X(1137) - 0.05, Y(781), 1.19), (X(1137) - 0.18, Y(781), 1.17)], 0.01, "chrome", "Decor", 10)

# ---------------------------------------------------------------- dining: a place setting at each chair
for i in range(3):
    for s_ in (-1, 1):
        cx_ = tx + (i - 1) * 0.68; cy_ = ty + s_ * 0.27
        box(f"Dine_mat{i}{s_}", cx_ - 0.22, cy_ - 0.16, 0.775, cx_ + 0.22, cy_ + 0.16, 0.779, "linen_charcoal", "Decor")
        pl_ = lathe(f"Dine_plate{i}{s_}", [(0.0, 0.0), (0.08, 0.0), (0.10, 0.008), (0.13, 0.018), (0.128, 0.022), (0.10, 0.012), (0.0, 0.01)], "porcelain", "Decor", 48)
        pl_.location = (cx_, cy_, 0.779)
        cyl(f"Dine_glass{i}{s_}", cx_ + 0.17, cy_ - s_ * 0.12, 0.779, 0.035, 0.13, "glass", "Decor", 20, r2=0.04)
        box(f"Dine_fork{i}{s_}", cx_ - 0.17, cy_ - 0.09, 0.779, cx_ - 0.155, cy_ + 0.09, 0.782, "brass", "Decor")
        box(f"Dine_knife{i}{s_}", cx_ + 0.155, cy_ - 0.09, 0.779, cx_ + 0.17, cy_ + 0.09, 0.782, "brass", "Decor")

# ---------------------------------------------------------------- switch plates beside the doors
def switch(n, x, y, face, z=1.2, w=0.2):
    g = group(n, x, y, 0, face, "Decor")
    adopt(g, [box(n + "_plate", 0.0, -w / 2, z - 0.045, 0.008, w / 2, z + 0.045, "switch_glass", "Decor"),
              box(n + "_k1", 0.008, -w / 2 + 0.03, z - 0.02, 0.011, -0.01, z + 0.02, "brass_brushed", "Decor"),
              box(n + "_k2", 0.008, 0.01, z - 0.02, 0.011, w / 2 - 0.03, z + 0.02, "brass_brushed", "Decor")])
switch("Sw_Foyer", X(1137), Y(468), "W", w=0.12)
switch("Sw_BR2", X(1072), Y(452), "N")
switch("Sw_BR3", X(635), Y(448), "W")
switch("Sw_Master", X(365), Y(482), "W")
switch("Sw_Living", X(649), Y(458), "E", w=0.12)

# ---------------------------------------------------------------- balcony sit-out: jute rug, coffee for one, a book
box("Bal_rug", X(712), Y(140), -0.03, X(852), Y(70), -0.022, "rug", "Furniture", bevel=0.003)
CUP = (X(782) - 0.09, Y(110) - 0.06, 0.47)
sau = lathe("Bal_saucer", [(0.0, 0.0), (0.05, 0.0), (0.07, 0.008), (0.075, 0.014), (0.07, 0.016), (0.05, 0.007), (0.0, 0.006)], "ceramic_white", "Decor", 48)
sau.location = CUP
cup = lathe("Bal_cup", [(0.0, 0.0), (0.03, 0.0), (0.036, 0.004), (0.042, 0.05), (0.044, 0.072), (0.040, 0.072), (0.038, 0.05), (0.032, 0.012), (0.0, 0.012)], "ceramic_white", "Decor", 48)
cup.location = (CUP[0], CUP[1], CUP[2] + 0.006)
cyl("Bal_coffee", CUP[0], CUP[1], CUP[2] + 0.062, 0.0385, 0.003, "coffee", "Decor", 32)
torus("Bal_cuphandle", CUP[0] + 0.05, CUP[1], CUP[2] + 0.045, 0.018, 0.005, "ceramic_white", "Decor", rot=(90, 0, 0))
cyl("Bal_spoon", CUP[0] + 0.055, CUP[1] - 0.04, CUP[2] + 0.012, 0.004, 0.09, "brass", "Decor", 8, rot=(0, 90, 20))
for i, (mt, rr) in enumerate([("book_c", 0), ("book_a", 7)]):
    boxc(f"Bal_book{i}", X(782) + 0.07, Y(110) + 0.08, 0.47 + i * 0.03, 0.2, 0.14, 0.028, mt, "Decor", rot=rr + 20)
st = cyl("Bal_steam", CUP[0], CUP[1], CUP[2] + 0.07, 0.022, 0.24, "steam", "FX", 24, r2=0.07)
STEAM_AT = (CUP[0], CUP[1], CUP[2] + 0.08)
