# Bake the Cycles lighting of the luxury scene for the real-time walkthrough.
#   BakedA: low-poly architecture and box furniture -> lightmap atlas (second UV set)
#   BakedV: dense furniture, curtains and imported models -> per-vertex lighting (colour attribute)
# Usage: python bake_v2.py -- <atlas_px> <samples>
import bpy, bmesh, os, sys, math, re, json
import numpy as np
ROOT = "/home/claude/house/build2"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ATLAS = int(argv[0]) if argv else 2048
SAMPLES = int(argv[1]) if len(argv) > 1 else 16
LMAX = 4.0     # lighting values are stored divided by this (decoded in the viewer)

bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "A105_lux.blend"))
sc = bpy.context.scene

SKIP_MAT = re.compile(r"^(glass|sheer|led|opal|backdrop|mirror|smoked_mirror)|glass|Glass|wings", re.I)
BAKE_COLL = {"Walls", "Floors", "Ceiling", "Furniture", "Decor", "Openings", "Assets", "Exterior"}

def principled(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.use_nodes else None
def is_metal(m):
    b = principled(m); return bool(b) and b.inputs["Metallic"].default_value >= 0.5 and not b.inputs["Metallic"].links

cands = []
for o in sc.objects:
    if o.type != 'MESH' or not any(c.name in BAKE_COLL for c in o.users_collection): continue
    if o.name.startswith(("Backdrop", "Ground", "Slab_Below")): continue
    mats = [s.material for s in o.material_slots if s.material]
    if not mats or any(SKIP_MAT.search(m.name) for m in mats): continue
    if all(is_metal(m) for m in mats): continue          # pure metal stays live (reflections only)
    cands.append(o)
for o in cands:
    if len(o.data.polygons) > 6000:
        md = o.modifiers.new("dec", "DECIMATE"); md.ratio = max(0.12, 6000 / len(o.data.polygons))
dg = bpy.context.evaluated_depsgraph_get(); dg.update()

groupA, groupV = [], []
for o in cands:
    ed = o.evaluated_get(dg).data
    n_eval = len(ed.polygons) if ed else 0
    (groupA if n_eval <= 220 else groupV).append(o)
print("atlas objects:", len(groupA), "vertex objects:", len(groupV))

def merge(objs, name, cull=True):
    bm = bmesh.new(); uv0 = bm.loops.layers.uv.new("UVMap")
    mat_index, mat_list = {}, []
    for o in objs:
        eo = o.evaluated_get(dg); me = eo.to_mesh()
        tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world); tmp.normal_update()
        src_uv = tmp.loops.layers.uv.active
        remap = []
        for s in o.material_slots:
            if s.material.name not in mat_index:
                mat_index[s.material.name] = len(mat_list); mat_list.append(s.material)
            remap.append(mat_index[s.material.name])
        tmp.verts.index_update()
        vmap = [bm.verts.new(v.co) for v in tmp.verts]
        for f in tmp.faces:
            if cull:
                n_ = f.normal; cz = f.calc_center_median().z
                if (n_.z < -0.9 and cz < 0.06) or (n_.z > 0.9 and cz > 2.84): continue
            try: nf = bm.faces.new([vmap[v.index] for v in f.verts])
            except ValueError: continue
            nf.material_index = remap[f.material_index] if f.material_index < len(remap) else 0
            nf.smooth = f.smooth
            if src_uv is not None:
                for a, b in zip(nf.loops, f.loops): a[uv0].uv = b[src_uv].uv
        tmp.free(); eo.to_mesh_clear()
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    ob = bpy.data.objects.new(name, mesh); sc.collection.objects.link(ob)
    for m in mat_list: mesh.materials.append(m)
    return ob, mat_list

A, matsA = merge(groupA, "BakedA")
V, matsV = merge(groupV, "BakedV")
for o in cands: bpy.data.objects.remove(o, do_unlink=True)
print("BakedA faces", len(A.data.polygons), "BakedV faces", len(V.data.polygons), "verts", len(V.data.vertices))

def ctx(ob):
    return bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob], selected_editable_objects=[ob])
def select_only(ob):
    for o in sc.objects: o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)

# ---------------- lightmap atlases (xatlas; Blender's UV operators crash in module mode).
# Both merged meshes get their own atlas: per-vertex baking sampled from mesh corners and came out blotchy.
import xatlas
def atlas_uv(ob, res, padding, max_cost=2.0):
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(ob.data); bm.free()
    me = ob.data; nv = len(me.vertices); nf = len(me.polygons)
    co = np.zeros(nv * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    fv = np.zeros(nf * 3, np.int32); me.polygons.foreach_get("vertices", fv); fv = fv.reshape(-1, 3).astype(np.uint32)
    atl = xatlas.Atlas(); atl.add_mesh(co, fv)
    copt = xatlas.ChartOptions(); copt.max_iterations = 1; copt.max_cost = max_cost
    po = xatlas.PackOptions(); po.resolution = res; po.padding = padding; po.bilinear = True; po.rotate_charts = True
    atl.generate(copt, po)
    _, idx, uvs = atl[0]
    print(ob.name, "xatlas", atl.width, atl.height, "charts", atl.chart_count, "util", round(atl.utilization, 3), flush=True)
    lm = me.uv_layers.new(name="LightMap"); me.uv_layers.active = lm; me.uv_layers["UVMap"].active_render = True
    lm.data.foreach_set("uv", uvs[idx.reshape(-1)].astype(np.float32).ravel())   # 3 loops per triangle, face order

def add_target(mats, img):
    for m in mats:
        nt = m.node_tree
        for nm in ("__lightmap__", "__lmuv__"):
            if nm in nt.nodes: nt.nodes.remove(nt.nodes[nm])
        n = nt.nodes.new("ShaderNodeTexImage"); n.name = "__lightmap__"; n.image = img
        u = nt.nodes.new("ShaderNodeUVMap"); u.name = "__lmuv__"; u.uv_map = "LightMap"
        nt.links.new(u.outputs["UV"], n.inputs["Vector"])
        for x in nt.nodes: x.select = False
        n.select = True; nt.nodes.active = n
def clear_target(mats):
    for m in mats:
        nt = m.node_tree
        for nm in ("__lightmap__", "__lmuv__"):
            if nm in nt.nodes: nt.nodes.remove(nt.nodes[nm])

sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False
b = sc.render.bake
b.use_pass_direct = True; b.use_pass_indirect = True; b.use_pass_color = False
b.target = 'IMAGE_TEXTURES'

def bake(ob, mats, res, padding, fname, samples, max_cost=2.0):
    sc.cycles.samples = samples
    atlas_uv(ob, res, padding, max_cost)
    img = bpy.data.images.new("LM_" + ob.name, res, res, float_buffer=True, alpha=False)
    add_target(mats, img); select_only(ob)
    with ctx(ob):
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=padding, use_clear=True, target='IMAGE_TEXTURES')
    img.filepath_raw = os.path.join(ROOT, fname); img.file_format = 'OPEN_EXR'; img.save()
    clear_target(mats); ob.data.uv_layers.active = ob.data.uv_layers["UVMap"]
    print("BAKED", ob.name, flush=True)

# furniture lighting is soft, so it gets a smaller atlas and many more samples per texel
bake(A, matsA, ATLAS, 4, "lightmap_raw.exr", SAMPLES)
bake(V, matsV, ATLAS // 2, 2, "lightmapV_raw.exr", SAMPLES * 2, max_cost=4.0)
json.dump({"atlas": ATLAS}, open(os.path.join(ROOT, "bake_meta.json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "A105_baked.blend"))
print("SAVED")
