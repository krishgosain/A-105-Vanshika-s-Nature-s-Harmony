# Turahalli forest view for A-105: a 360° render taken from the living-room balcony.
# Rolling forested hills (dense dry-deciduous canopy, eucalyptus stands, granite outcrops) beyond the
# project's landscaped compound. Output:
#   build2/textures/forest_env.exr  scene-linear, used as the backdrop that camera rays see in Cycles
#   site/img/forest.jpg             the same view after A-105's tone mapping, used by the real-time walk
# Usage: python forest_v2.py -- <W> <samples>
import bpy, bmesh, math, os, sys, random
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
W = int(argv[0]) if argv else 4096
SAMPLES = int(argv[1]) if len(argv) > 1 else 32
ROOT = "/home/claude/house/build2"; SITE = "/home/claude/house/site"
rng = np.random.default_rng(11); random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
GROUND = -6.0        # ground level below the balcony floor (m)

# ---------------------------------------------------------------- materials
def haze(m, color=(0.55, 0.64, 0.76), dist=4200.0, strength=0.34):
    """Atmospheric perspective: blend toward a sky-tinted emission with view distance."""
    nt = m.node_tree; out = nt.nodes["Material Output"]; bsdf = out.inputs["Surface"].links[0].from_node
    cam = nt.nodes.new("ShaderNodeCameraData")
    mathn = nt.nodes.new("ShaderNodeMath"); mathn.operation = 'DIVIDE'; mathn.inputs[1].default_value = -dist
    nt.links.new(cam.outputs["View Distance"], mathn.inputs[0])
    ex = nt.nodes.new("ShaderNodeMath"); ex.operation = 'EXPONENT'; nt.links.new(mathn.outputs[0], ex.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; nt.links.new(ex.outputs[0], inv.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = strength
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(inv.outputs[0], mix.inputs[0]); nt.links.new(bsdf.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])

def pmat(name, color, rough=0.8, translucent=0.0, rand_colors=None, noise_scale=None, noise_mix=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    if translucent:
        b.inputs["Subsurface Weight"].default_value = 0.0
        try: b.inputs["Transmission Weight"].default_value = 0.0
        except Exception: pass
    if rand_colors:      # per-instance colour variation through a ramp
        oi = nt.nodes.new("ShaderNodeObjectInfo"); ramp = nt.nodes.new("ShaderNodeValToRGB")
        cr = ramp.color_ramp; cr.interpolation = 'LINEAR'
        while len(cr.elements) < len(rand_colors): cr.elements.new(0.5)
        for i, (pos, col) in enumerate(rand_colors):
            cr.elements[i].position = pos; cr.elements[i].color = (*col, 1)
        nt.links.new(oi.outputs["Random"], ramp.inputs["Fac"])
        if noise_scale:   # break up each crown with a little in-crown variation
            nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs["Factor"].default_value = noise_mix or 0.4
            nt.links.new(ramp.outputs["Color"], mx.inputs[6]); nt.links.new(nz.outputs["Color"], mx.inputs[7])
            nt.links.new(mx.outputs[2], b.inputs["Base Color"])
        else:
            nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    if translucent:
        out = nt.nodes["Material Output"]
        tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.10, 0.16, 0.035, 1)
        mx_ = nt.nodes.new("ShaderNodeMixShader"); mx_.inputs[0].default_value = translucent
        nt.links.new(b.outputs[0], mx_.inputs[1]); nt.links.new(tr.outputs[0], mx_.inputs[2]); nt.links.new(mx_.outputs[0], out.inputs["Surface"])
    haze(m)
    return m

LEAF = pmat("leaf", (0.06, 0.10, 0.03), 0.6, translucent=0.22, rand_colors=[(0.0, (0.030, 0.062, 0.020)), (0.35, (0.055, 0.095, 0.028)),
            (0.7, (0.090, 0.120, 0.035)), (0.9, (0.140, 0.140, 0.045)), (1.0, (0.170, 0.150, 0.060))], noise_scale=3.0, noise_mix=0.35)
EUC = pmat("euc_leaf", (0.10, 0.12, 0.08), 0.6, translucent=0.18, rand_colors=[(0.0, (0.075, 0.095, 0.065)), (1.0, (0.12, 0.13, 0.085))], noise_scale=4.0, noise_mix=0.3)
BARK = pmat("bark", (0.10, 0.08, 0.06), 0.9)
EUCBARK = pmat("euc_bark", (0.30, 0.28, 0.25), 0.8)
ROCK = pmat("granite_rock", (0.36, 0.34, 0.31), 0.85, rand_colors=[(0.0, (0.28, 0.27, 0.25)), (1.0, (0.45, 0.42, 0.38))], noise_scale=6.0, noise_mix=0.5)
WALL = pmat("compound_wall", (0.74, 0.70, 0.63), 0.9)
PAVER = pmat("paver", (0.34, 0.32, 0.30), 0.8)

# ground: grass / dry scrub / soil blend driven by noise
GRD = bpy.data.materials.new("forest_ground"); GRD.use_nodes = True; nt = GRD.node_tree
b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.04; nz.inputs["Detail"].default_value = 8
ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
cr.elements[0].position = 0.35; cr.elements[0].color = (0.05, 0.075, 0.025, 1)
cr.elements[1].position = 0.70; cr.elements[1].color = (0.16, 0.13, 0.07, 1)
nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
haze(GRD)
LAWN = pmat("lawn_near", (0.045, 0.075, 0.015), 0.95, rand_colors=[(0.0, (0.040, 0.068, 0.013)), (1.0, (0.055, 0.080, 0.018))], noise_scale=0.6, noise_mix=0.45)

# ---------------------------------------------------------------- helpers
def link(o, cname):
    c = bpy.data.collections.get(cname)
    if not c:
        c = bpy.data.collections.new(cname); sc.collection.children.link(c)
    c.objects.link(o); return o

def mesh_obj(name, bm, material, cname):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(material); return link(o, cname)

def crown_clumps(bm, cx, cy, cz, rx, ry, rz, n, rmin, rmax, subdiv=1, jitter=0.25, leaves=42, leaf=(0.26, 0.16)):
    for _ in range(n):
        while True:
            p = rng.uniform(-1, 1, 3)
            if (p ** 2).sum() <= 1: break
        p = p * np.array([rx, ry, rz]) * (0.6 + 0.4 * rng.random())
        r = rng.uniform(rmin, rmax)
        c0 = np.array([cx + p[0], cy + p[1], cz + p[2]])
        res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r * 0.55)
        for v in res["verts"]:
            v.co.x += c0[0] + rng.normal(0, r * jitter * 0.5); v.co.y += c0[1] + rng.normal(0, r * jitter * 0.5); v.co.z += c0[2] + rng.normal(0, r * jitter * 0.3)
        # leaf cards scattered through the clump
        q = rng.normal(0, 1, (leaves, 3)); q /= np.linalg.norm(q, axis=1)[:, None]
        q *= (r * rng.uniform(0.45, 1.05, leaves))[:, None]
        nrm = rng.normal(0, 1, (leaves, 3)); nrm /= np.linalg.norm(nrm, axis=1)[:, None]
        for k in range(leaves):
            n_ = nrm[k]; a_ = np.cross(n_, [0.0, 0.0, 1.0]);
            if np.linalg.norm(a_) < 1e-3: a_ = np.array([1.0, 0, 0])
            a_ /= np.linalg.norm(a_); b_ = np.cross(n_, a_)
            L, Wd = leaf[0] * rng.uniform(0.7, 1.3), leaf[1] * rng.uniform(0.7, 1.3)
            ctr = c0 + q[k]
            vs = [bm.verts.new(tuple(ctr + a_ * L * sa + b_ * Wd * sb)) for sa, sb in ((-0.5, 0), (0, -0.5), (0.5, 0), (0, 0.5))]
            bm.faces.new(vs)

def trunk(bm, h, r0, r1, lean=0.0):
    res = bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=r0, radius2=r1, depth=h)
    for v in res["verts"]:
        v.co.z += h / 2; v.co.x += lean * v.co.z

protos_broad, protos_euc = [], []
for k in range(6):          # broadleaf crowns (neem, honge, rain-tree like), unit height ~9 m
    bmL = bmesh.new(); bmT = bmesh.new()
    h = rng.uniform(3.0, 4.5); trunk(bmT, h + 1.5, 0.28, 0.12, rng.uniform(-0.05, 0.05))
    rx = rng.uniform(3.0, 4.2); crown_clumps(bmL, 0, 0, h + 2.3, rx, rx * rng.uniform(0.8, 1.1), rng.uniform(2.0, 2.8), 70, 0.55, 1.15)
    c = bpy.data.collections.new(f"broad{k}")
    o = mesh_obj(f"broad{k}_crown", bmL, LEAF, "protos"); o2 = mesh_obj(f"broad{k}_trunk", bmT, BARK, "protos")
    for ob in (o, o2):
        bpy.data.collections["protos"].objects.unlink(ob); c.objects.link(ob)
    protos_broad.append(c)
for k in range(3):          # eucalyptus: tall pale trunks, light open crowns
    bmL = bmesh.new(); bmT = bmesh.new()
    h = rng.uniform(10, 13); trunk(bmT, h - 2, 0.2, 0.07, rng.uniform(-0.03, 0.03))
    crown_clumps(bmL, 0, 0, h - 3.0, 2.8, 2.6, 3.6, 80, 0.35, 0.8, jitter=0.35, leaves=26, leaf=(0.34, 0.07))
    c = bpy.data.collections.new(f"euc{k}")
    o = mesh_obj(f"euc{k}_crown", bmL, EUC, "protos"); o2 = mesh_obj(f"euc{k}_trunk", bmT, EUCBARK, "protos")
    for ob in (o, o2):
        bpy.data.collections["protos"].objects.unlink(ob); c.objects.link(ob)
    protos_euc.append(c)
protos_shrub = []
for k in range(3):
    bmL = bmesh.new(); crown_clumps(bmL, 0, 0, 1.2, 2.2, 2.0, 1.3, 40, 0.4, 0.8)
    c = bpy.data.collections.new(f"shrub{k}"); o = mesh_obj(f"shrub{k}", bmL, LEAF, "protos")
    bpy.data.collections["protos"].objects.unlink(o); c.objects.link(o); protos_shrub.append(c)
rock_c = bpy.data.collections.new("rocks")
for k in range(4):
    bmR = bmesh.new(); res = bmesh.ops.create_icosphere(bmR, subdivisions=2, radius=1.0)
    s = rng.uniform(0.7, 1.4, 3) * np.array([1.6, 1.2, 0.8])
    for v in res["verts"]:
        n = 1 + 0.18 * math.sin(v.co.x * 3.1 + k) * math.cos(v.co.y * 2.7) + 0.1 * math.sin(v.co.z * 5.3)
        v.co.x *= s[0] * n; v.co.y *= s[1] * n; v.co.z *= s[2] * n
    o = mesh_obj(f"rock{k}", bmR, ROCK, "protos"); bpy.data.collections["protos"].objects.unlink(o); rock_c.objects.link(o)
bpy.data.collections["protos"].hide_render = True
bpy.context.view_layer.layer_collection.children["protos"].exclude = True

# ---------------------------------------------------------------- terrain: Turahalli's forested hill to the north
N_, SIZE = 300, 3200.0
xs = np.linspace(-SIZE / 2, SIZE / 2, N_ + 1); X_, Y_ = np.meshgrid(xs, xs)
def fbm(x, y, oct=5, base=1 / 400):
    h = np.zeros_like(x); a, f = 1.0, base
    for o in range(oct):
        ph = rng.uniform(0, 6.28, 4)
        h += a * (np.sin(x * f + ph[0]) * np.cos(y * f * 1.3 + ph[1]) + np.sin((x + y) * f * 0.7 + ph[2]) * 0.5)
        a *= 0.5; f *= 2.1
    return h
D = np.hypot(X_, Y_)
hill = 95 * np.exp(-(((X_ - 100) / 460) ** 2 + ((Y_ - 620) / 260) ** 2)) + 55 * np.exp(-(((X_ + 560) / 360) ** 2 + ((Y_ - 520) / 230) ** 2))
hill += 22 * np.exp(-(((X_ - 700) / 300) ** 2 + ((Y_ - 520) / 240) ** 2))
roll = 9 * fbm(X_, Y_) + 3 * fbm(X_, Y_, 3, 1 / 60)
ramp_in = np.clip((D - 90) / 240, 0, 1)
Z = GROUND + ramp_in * (hill + roll + 6) + np.where(Y_ < -200, 0.25 * np.clip(-Y_ - 200, 0, 600) * 0.02, 0)
bmG = bmesh.new()
vv = [[bmG.verts.new((X_[i, j], Y_[i, j], Z[i, j])) for j in range(N_ + 1)] for i in range(N_ + 1)]
for i in range(N_):
    for j in range(N_):
        bmG.faces.new([vv[i][j], vv[i][j + 1], vv[i + 1][j + 1], vv[i + 1][j]])
terrain = mesh_obj("Terrain", bmG, GRD, "Land")
def height_at(x, y):
    fi = (y + SIZE / 2) / SIZE * N_; fj = (x + SIZE / 2) / SIZE * N_
    i = int(np.clip(fi, 0, N_ - 1)); j = int(np.clip(fj, 0, N_ - 1)); return Z[i, j]

# near field: the project's landscaped compound below the balcony
bmL_ = bmesh.new(); bmesh.ops.create_grid(bmL_, x_segments=2, y_segments=2, size=95)
for v in bmL_.verts: v.co.y = min(v.co.y, 32.0)
for v in bmL_.verts: v.co.z = GROUND + 0.02
mesh_obj("Compound_lawn", bmL_, LAWN, "Land")
def box(name, x0, y0, z0, x1, y1, z1, m):
    bm = bmesh.new(); res = bmesh.ops.create_cube(bm, size=1.0)
    for v in res["verts"]:
        v.co.x = (x0 + x1) / 2 + v.co.x * (x1 - x0); v.co.y = (y0 + y1) / 2 + v.co.y * (y1 - y0); v.co.z = (z0 + z1) / 2 + v.co.z * (z1 - z0)
    o = mesh_obj(name, bm, m, "Land")
    for p in o.data.polygons: p.use_smooth = False
    return o
box("Walkway", -95, 12, GROUND, 95, 15, GROUND + 0.05, PAVER)
box("Walkway2", -95, -40, GROUND, 95, -36, GROUND + 0.05, PAVER)
for nm, (x0, y0, x1, y1) in {"N": (-95, 32, 95, 32.4), "W": (-95.4, -95, -95, 32.4), "E": (95, -95, 95.4, 32.4), "S": (-95, -95, 95, -94.6)}.items():
    box("Wall" + nm, x0, y0, GROUND, x1, y1, GROUND + 2.0, WALL)
    box("WallCap" + nm, x0 - 0.1, y0 - 0.1, GROUND + 2.0, x1 + 0.1, y1 + 0.1, GROUND + 2.12, PAVER)

# ---------------------------------------------------------------- scatter trees and rocks as instances
def inst(name, coll, x, y, z, s, rot):
    o = bpy.data.objects.new(name, None); o.instance_type = 'COLLECTION'; o.instance_collection = coll
    o.location = (x, y, z); o.scale = (s, s, s); o.rotation_euler = (0, 0, rot); sc.collection.objects.link(o)
cnt = 0
# compound landscaping: a few garden trees inside the wall
for k in range(34):
    x = rng.uniform(-90, 90); y = rng.uniform(19, 30) if k < 18 else rng.uniform(-90, -45)
    inst(f"g{k}", protos_broad[k % 6], x, y, GROUND, rng.uniform(0.45, 0.7), rng.uniform(0, 6.28)); cnt += 1
# the forest: dense beyond the compound, thinning into clearings; eucalyptus stands and granite outcrops on the hill
pts = []
for ring_r, spacing in [(55, 7.0), (250, 9.0), (600, 13.0), (1100, 20.0)]:
    pass
NS = 260000
xs_ = rng.uniform(-1500, 1500, NS); ys_ = rng.uniform(-1500, 1500, NS)
dd = np.hypot(xs_, ys_)
keep_p = np.where(dd < 36, 0, np.where(dd < 500, 0.85, np.where(dd < 900, 0.35, 0.16)))
inside_compound = (np.abs(xs_) < 97) & (ys_ < 34) & (ys_ > -97)
keep_p = np.where(inside_compound, 0, keep_p)
clear = np.sin(xs_ / 70.0) * np.cos(ys_ / 55.0) > 0.82          # a few natural clearings
keep_p = np.where(clear, keep_p * 0.15, keep_p)
sel = rng.random(len(xs_)) < keep_p
for x, y in zip(xs_[sel], ys_[sel]):
    z = height_at(x, y)
    euc_zone = math.sin(x / 140.0 + 1.3) * math.cos(y / 160.0) > 0.55
    if euc_zone and rng.random() < 0.35:
        inst(f"e{cnt}", protos_euc[cnt % 3], x, y, z - 0.3, rng.uniform(0.8, 1.25), rng.uniform(0, 6.28))
    else:
        d_ = math.hypot(x, y); s = rng.uniform(0.95, 1.5) * (1.0 if d_ < 500 else 1.6)
        inst(f"b{cnt}", protos_broad[cnt % 6], x, y, z - 0.3, s, rng.uniform(0, 6.28))
    cnt += 1
sx_ = rng.uniform(-420, 420, 30000); sy_ = rng.uniform(-420, 420, 30000)
sd_ = np.hypot(sx_, sy_); ok = (sd_ > 34) & ~((np.abs(sx_) < 97) & (sy_ < 34) & (sy_ > -97))
for x, y in zip(sx_[ok][:9000], sy_[ok][:9000]):
    inst(f"s{cnt}", protos_shrub[cnt % 3], x, y, height_at(x, y) - 0.2, rng.uniform(0.8, 1.6), rng.uniform(0, 6.28)); cnt += 1
# hedges and palms-free garden shrubs along the compound wall
for k in range(60):
    x = -92 + k * 3.1
    inst(f"h{k}", protos_shrub[k % 3], x, 30.5, GROUND, rng.uniform(0.6, 0.8), rng.uniform(0, 6.28))
# granite boulders breaking through the canopy on the hill (Turahalli's rocky crest)
rk = 0
for k in range(700):
    x = rng.normal(120, 320); y = rng.normal(800, 170)
    z = height_at(x, y)
    if z < GROUND + 35: continue
    inst(f"r{rk}", rock_c, x, y, z - 1.0, rng.uniform(4, 11), rng.uniform(0, 6.28)); rk += 1
for k in range(160):
    x = rng.normal(-520, 200); y = rng.normal(620, 120); z = height_at(x, y)
    if z < GROUND + 20: continue
    inst(f"q{rk}", rock_c, x, y, z - 1.0, rng.uniform(3, 8), rng.uniform(0, 6.28)); rk += 1
print("instances", cnt, "rocks", rk, flush=True)

# ---------------------------------------------------------------- sky, sun, clouds (same time of day as the flat)
world = bpy.data.worlds.new("Sky"); sc.world = world; world.use_nodes = True
wnt = world.node_tree; bg = wnt.nodes["Background"]
sky = wnt.nodes.new("ShaderNodeTexSky")
try:
    # late-morning sun behind the building, so the forest to the north is front-lit under a clear sky
    sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(25); sky.sun_disc = False
    sky.air_density = 1.0; sky.dust_density = 0.6
except Exception: pass
wnt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.6
sd = bpy.data.lights.new("Sun", "SUN"); sd.energy = 3.0; sd.angle = math.radians(1.5); sd.color = (1.0, 0.9, 0.78)
so = bpy.data.objects.new("Sun", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(52), 0, math.radians(25))
CL = bpy.data.materials.new("clouds"); CL.use_nodes = True; cnt_ = CL.node_tree
cb = cnt_.nodes["Principled BSDF"]; cb.inputs["Base Color"].default_value = (1, 1, 1, 1); cb.inputs["Roughness"].default_value = 1.0
cn = cnt_.nodes.new("ShaderNodeTexNoise"); cn.inputs["Scale"].default_value = 0.0009 * 1000; cn.inputs["Detail"].default_value = 6; cn.inputs["Roughness"].default_value = 0.6
tc = cnt_.nodes.new("ShaderNodeTexCoord")
cmap = cnt_.nodes.new("ShaderNodeMapping"); cmap.inputs["Scale"].default_value = (0.00045, 0.0008, 0.00045)
cnt_.links.new(tc.outputs["Object"], cmap.inputs["Vector"]); cnt_.links.new(cmap.outputs["Vector"], cn.inputs["Vector"])
cr2 = cnt_.nodes.new("ShaderNodeValToRGB"); cr2.color_ramp.elements[0].position = 0.60; cr2.color_ramp.elements[1].position = 0.80
cnt_.links.new(cn.outputs["Fac"], cr2.inputs["Fac"]); cnt_.links.new(cr2.outputs["Color"], cb.inputs["Alpha"])
cb.inputs["Emission Color"].default_value = (0.86, 0.88, 0.92, 1); cb.inputs["Emission Strength"].default_value = 0.6
bmC = bmesh.new(); bmesh.ops.create_grid(bmC, x_segments=1, y_segments=1, size=9000)
for v in bmC.verts: v.co.z = 1400
cl = mesh_obj("Clouds", bmC, CL, "Land")

# ---------------------------------------------------------------- camera: equirect at the balcony, eye height
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.type = 'PANO'
try: cam_d.panorama_type = 'EQUIRECTANGULAR'
except Exception: cam_d.cycles.panorama_type = 'EQUIRECTANGULAR'
cam.location = (0, 0, 1.55); cam.rotation_euler = (math.radians(90), 0, math.radians(-90))
cam_d.clip_end = 20000
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False          # denoised below with OIDN, outside the renderer (keeps memory in check)
sc.cycles.use_auto_tile = True; sc.cycles.tile_size = 1024
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1; sc.cycles.transparent_max_bounces = 8
sc.render.resolution_x, sc.render.resolution_y = W, W // 2; sc.render.resolution_percentage = 100
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.view_settings.exposure = 0.0
os.makedirs(os.path.join(ROOT, "textures"), exist_ok=True)
RAW = os.path.join(ROOT, "forest_raw.exr")
sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
sc.render.filepath = RAW
bpy.ops.render.render(write_still=True)
print("RENDERED RAW", flush=True)
# OIDN on the raw render
import oidn, ctypes, glob
im = bpy.data.images.load(RAW); Wd, Hd = im.size
px = np.array(im.pixels[:], dtype=np.float32).reshape(Hd, Wd, 4)[:, :, :3].copy()
lib = ctypes.CDLL(sorted(glob.glob(os.path.join(os.path.dirname(oidn.__file__), "lib.linux.x64", "libOpenImageDenoise.so*")))[0])
set1b = lib.oidnSetFilter1b; set1b.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]; set1b.restype = None
dev = oidn.NewDevice(oidn.DEVICE_TYPE_CPU); oidn.CommitDevice(dev)
flt = oidn.NewFilter(dev, "RT"); out = np.zeros_like(px)
oidn.SetSharedFilterImage(flt, "color", px, oidn.FORMAT_FLOAT3, Wd, Hd); oidn.SetSharedFilterImage(flt, "output", out, oidn.FORMAT_FLOAT3, Wd, Hd)
set1b(flt, b"hdr", True); oidn.CommitFilter(flt); oidn.ExecuteFilter(flt); oidn.ReleaseFilter(flt); oidn.ReleaseDevice(dev)
den = bpy.data.images.new("forest_den", Wd, Hd, float_buffer=True, alpha=False)
rgba = np.ones((Hd, Wd, 4), np.float32); rgba[:, :, :3] = out; den.pixels.foreach_set(rgba.ravel())
s_ = sc.render.image_settings
s_.file_format = 'OPEN_EXR'; s_.color_depth = '16'; s_.exr_codec = 'DWAA'
den.save_render(os.path.join(ROOT, "textures", "forest_env.exr"), scene=sc)
sc.view_settings.exposure = 0.3 + math.log2(0.8)  # A-105's +0.3 EV with the forest at strength 0.8, as the 360 renders show it
s_.file_format = 'JPEG'; s_.quality = 90
den.save_render(os.path.join(SITE, "img", "forest.jpg"), scene=sc)
den.save_render(os.path.join(ROOT, "forest_preview.jpg"), scene=sc)
print("FOREST OK", W, SAMPLES)
