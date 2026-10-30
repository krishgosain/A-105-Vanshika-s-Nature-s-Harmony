# Shared helpers for the luxury rebuild of A-105 (Blender 5, bpy module).
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

ROOT = "/home/claude/house/build2"
TEX = os.path.join(ROOT, "textures")
ASSETS = "/home/claude/house/assets"
S = 74.0
H = 2.85
DOOR_H = 2.40
SLIDE_H = 2.55

def X(px): return (px - 45) / S
def Y(py): return -(py - 160) / S

COLLIDERS = []
COLL = {}
MATS = {}

def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLL[name] = c
    return COLL[name]

def _img(name, noncolor=False):
    img = bpy.data.images.load(os.path.join(TEX, name), check_existing=True)
    if noncolor:
        img.colorspace_settings.name = "Non-Color"
    return img

def mat(name, color=(0.8, 0.8, 0.8), tex=None, normal=None, nstr=0.6, tile=1.0, rough=0.5, metal=0.0,
        coat=0.0, sheen=0.0, sheen_tint=(1, 1, 1), alpha=1.0, emit=None, emit_strength=0.0,
        transmission=0.0, ior=1.45, spec=0.5, subsurface=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["IOR"].default_value = ior
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.05
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
        b.inputs["Sheen Tint"].default_value = (*sheen_tint, 1)
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if subsurface:
        b.inputs["Subsurface Weight"].default_value = subsurface
    if tex:
        tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = _img(tex); tn.location = (-500, 250)
        if isinstance(color, tuple) and color != (0.8, 0.8, 0.8) and False:
            pass
        nt.links.new(tn.outputs["Color"], b.inputs["Base Color"])
    if normal:
        nn = nt.nodes.new("ShaderNodeTexImage"); nn.image = _img(normal, True); nn.location = (-700, -250)
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr; nm.location = (-300, -250)
        nt.links.new(nn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
        m.use_backface_culling = False
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    m["tile"] = tile
    MATS[name] = m
    return m

def T(name): return MATS[name]["tile"] if name in MATS else 1.0

def _link(obj, cname):
    coll(cname).objects.link(obj)
    return obj

def _uv_box(bm, x0, y0, z0, x1, y1, z1, tile, unit=False):
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        n = f.normal
        for l in f.loops:
            p = l.vert.co
            if unit:
                if abs(n.z) > 0.5: u, v = (p.x - x0) / max(x1 - x0, 1e-6), (p.y - y0) / max(y1 - y0, 1e-6)
                elif abs(n.x) > 0.5: u, v = (p.y - y0) / max(y1 - y0, 1e-6), (p.z - z0) / max(z1 - z0, 1e-6)
                else: u, v = (p.x - x0) / max(x1 - x0, 1e-6), (p.z - z0) / max(z1 - z0, 1e-6)
                if (abs(n.x) > 0.5 and n.x < 0) or (abs(n.y) > 0.5 and n.y > 0): u = 1 - u
            else:
                if abs(n.z) > 0.5: u, v = p.x, p.y
                elif abs(n.x) > 0.5: u, v = p.y, p.z
                else: u, v = p.x, p.z
                u /= tile; v /= tile
            l[uv].uv = (u, v)

def box(name, x0, y0, z0, x1, y1, z1, material, cname="Furniture", collide=False, bevel=0.0, seg=3, unit=False, subsurf=0):
    """Axis-aligned box in metres (world-scaled UVs)."""
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1); z0, z1 = min(z0, z1), max(z0, z1)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([vs[i] for i in f])
    _uv_box(bm, x0, y0, z0, x1, y1, z1, T(material), unit)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    if bevel:
        md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = seg; md.limit_method = 'NONE'
        md.harden_normals = False
    if subsurf:
        md = o.modifiers.new("sub", "SUBSURF"); md.levels = subsurf; md.render_levels = subsurf
    if bevel or subsurf:
        for p in me.polygons: p.use_smooth = True
    if collide:
        COLLIDERS.append([round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)])
    return _link(o, cname)

def boxc(name, cx, cy, cz, sx, sy, sz, material, cname="Furniture", collide=False, rot=0.0, bevel=0.0, seg=3, subsurf=0, unit=False):
    """Box by centre (x,y), bottom z, size; optional Z rotation in degrees."""
    o = box(name, -sx / 2, -sy / 2, 0, sx / 2, sy / 2, sz, material, cname, False, bevel, seg, unit, subsurf)
    o.location = (cx, cy, cz); o.rotation_euler[2] = math.radians(rot)
    if collide:
        c, s = abs(math.cos(math.radians(rot))), abs(math.sin(math.radians(rot)))
        hx, hy = (sx * c + sy * s) / 2, (sx * s + sy * c) / 2
        COLLIDERS.append([round(cx - hx, 3), round(cy - hy, 3), round(cx + hx, 3), round(cy + hy, 3)])
    return o

def cyl(name, cx, cy, cz, r, h, material, cname="Furniture", verts=32, r2=None, sx=1.0, sy=1.0, rot=(0, 0, 0), smooth=True, collide=False):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co
            l[uv].uv = (p.x / max(r, 1e-6) * 0.5 + 0.5, p.y / max(r, 1e-6) * 0.5 + 0.5) if abs(f.normal.z) > 0.7 else (math.atan2(p.y, p.x) / 6.283 * 2 * math.pi * r / T(material), p.z / T(material))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    if smooth:
        for p in me.polygons:
            p.use_smooth = abs(p.normal.z) < 0.7
    o.location = (cx, cy, cz); o.scale = (sx, sy, 1); o.rotation_euler = tuple(math.radians(a) for a in rot)
    if collide:
        COLLIDERS.append([round(cx - r * sx, 3), round(cy - r * sy, 3), round(cx + r * sx, 3), round(cy + r * sy, 3)])
    return _link(o, cname)

def sphere(name, cx, cy, cz, r, material, cname="Decor", sx=1, sy=1, sz=1, seg=24):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    o.location = (cx, cy, cz); o.scale = (sx, sy, sz)
    return _link(o, cname)

def torus(name, cx, cy, cz, R, r, material, cname="Decor", rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    seg, ring = 64, 12
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(ring):
            b = 2 * math.pi * j / ring
            row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        verts.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new([verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % ring], verts[i][(j + 1) % ring]])
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    o.location = (cx, cy, cz); o.rotation_euler = tuple(math.radians(a) for a in rot)
    return _link(o, cname)

def panel_art(name, cx, cy, cz, w, h, material, facing, frame="brass", depth=0.035, cname="Decor"):
    """Framed canvas centred at (cx,cy,cz) hung on a wall; facing N/S/E/W = the direction the image faces."""
    fw = 0.025
    if facing in "NS":
        sgn = 1 if facing == "N" else -1
        box(name, cx - w / 2, cy, cz - h / 2, cx + w / 2, cy + sgn * depth, cz + h / 2, material, cname, unit=True)
        for (a0, a1, b0, b1) in [(-w / 2 - fw, w / 2 + fw, h / 2, h / 2 + fw), (-w / 2 - fw, w / 2 + fw, -h / 2 - fw, -h / 2), (-w / 2 - fw, -w / 2, -h / 2, h / 2), (w / 2, w / 2 + fw, -h / 2, h / 2)]:
            box(name + "_fr", cx + a0, cy, cz + b0, cx + a1, cy + sgn * (depth + 0.008), cz + b1, frame, cname)
    else:
        sgn = 1 if facing == "E" else -1
        box(name, cx, cy - w / 2, cz - h / 2, cx + sgn * depth, cy + w / 2, cz + h / 2, material, cname, unit=True)
        for (a0, a1, b0, b1) in [(-w / 2 - fw, w / 2 + fw, h / 2, h / 2 + fw), (-w / 2 - fw, w / 2 + fw, -h / 2 - fw, -h / 2), (-w / 2 - fw, -w / 2, -h / 2, h / 2), (w / 2, w / 2 + fw, -h / 2, h / 2)]:
            box(name + "_fr", cx, cy + a0, cz + b0, cx + sgn * (depth + 0.008), cy + a1, cz + b1, frame, cname)

def curtain(name, x0, y0, x1, y1, z0, z1, material, folds_per_m=7, amp=0.045, cname="Decor"):
    """Ripple-fold curtain between two plan points (metres)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (x1 - x0) / L, (y1 - y0) / L; px, py = -ny, nx
    folds = max(2, int(L * folds_per_m)); seg = folds * 10; rows = 8
    grid = []
    for j in range(rows):
        t = j / (rows - 1); z = z0 + (z1 - z0) * t
        a_here = amp * (1.0 + 0.35 * (1 - t))  # slight flare toward the hem
        row = []
        for i in range(seg + 1):
            s = i / seg; w = math.sin(s * folds * 2 * math.pi) * a_here
            row.append(bm.verts.new((x0 + nx * L * s + px * w, y0 + ny * L * s + py * w, z)))
        grid.append(row)
    uv = bm.loops.layers.uv.new("UVMap")
    for j in range(rows - 1):
        for i in range(seg):
            f = bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
            for l, (u, v) in zip(f.loops, [(i / seg, j), ((i + 1) / seg, j), ((i + 1) / seg, j + 1), (i / seg, j + 1)]):
                l[uv].uv = (u * L * 1.4 / T(material), v / (rows - 1) * (z1 - z0) / T(material))
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    md = o.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.004
    return _link(o, cname)

def cushion(name, cx, cy, cz, sx, sy, sz, material, rot=(0, 0, 0), cname="Decor"):
    o = box(name, -sx / 2, -sy / 2, -sz / 2, sx / 2, sy / 2, sz / 2, material, cname, bevel=min(sx, sy, sz) * 0.45, seg=4, subsurf=1)
    o.location = (cx, cy, cz + sz / 2); o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o

def asset(name, fname, x, y, z=0.0, rot=0.0, scale=1.0, recolor=None, cname="Assets", collide=False):
    """Import a glTF model, centre it on (x,y), sit it on z, rotate about Z (deg)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, fname))
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in new:
        if o.type == 'MESH':
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    root = bpy.data.objects.new(name, None); _link(root, cname)
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        _link(o, cname)
        if o.parent is None:
            o.parent = root
            o.location = o.location - Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    root.location = (x, y, z); root.rotation_euler[2] = math.radians(rot); root.scale = (scale,) * 3
    if recolor:
        for o in new:
            for slot in getattr(o, "material_slots", []):
                m = slot.material
                if not m: continue
                for key, spec in recolor.items():
                    if key.lower() in m.name.lower():
                        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                        if not b: continue
                        for l in list(b.inputs["Base Color"].links): m.node_tree.links.remove(l)
                        b.inputs["Base Color"].default_value = (*spec[0], 1)
                        if len(spec) > 1 and spec[1] is not None: b.inputs["Roughness"].default_value = spec[1]
                        for l in list(b.inputs["Sheen Tint"].links): m.node_tree.links.remove(l)
                        b.inputs["Sheen Tint"].default_value = (min(1, spec[0][0] * 2.2 + 0.25), min(1, spec[0][1] * 2.2 + 0.25), min(1, spec[0][2] * 2.2 + 0.25), 1)
                        b.inputs["Sheen Weight"].default_value = min(b.inputs["Sheen Weight"].default_value, 0.6)
    if collide:
        sx, sy = (mx.x - mn.x) * scale, (mx.y - mn.y) * scale
        c, s = abs(math.cos(math.radians(rot))), abs(math.sin(math.radians(rot)))
        hx, hy = (sx * c + sy * s) / 2, (sx * s + sy * c) / 2
        COLLIDERS.append([round(x - hx, 3), round(y - hy, 3), round(x + hx, 3), round(y + hy, 3)])
    return root


def tube(name, pts, r, material, cname="Furniture", ring=12):
    """Sweep a circle along a polyline of (x,y,z) points."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    P = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized(); v = t.cross(u).normalized()
        rings.append([bm.verts.new(p + (u * math.cos(2 * math.pi * k / ring) + v * math.sin(2 * math.pi * k / ring)) * r) for k in range(ring)])
    for i in range(len(rings) - 1):
        for k in range(ring):
            bm.faces.new([rings[i][k], rings[i][(k + 1) % ring], rings[i + 1][(k + 1) % ring], rings[i + 1][k]])
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    return _link(o, cname)

def shell_back(name, cx, cy, z0, z1, radius, arc_deg, thick, face_deg, material, cname="Furniture"):
    """Curved chair back: a cylindrical shell segment centred at (cx,cy), opening toward face_deg."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    n = 16; vs = []
    for j, z in enumerate((z0, z1)):
        for side, rr in enumerate((radius, radius + thick)):
            row = []
            for i in range(n + 1):
                a = math.radians(face_deg + 180 - arc_deg / 2 + arc_deg * i / n)
                row.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z)))
            vs.append(row)
    inner0, outer0, inner1, outer1 = vs
    for i in range(n):
        bm.faces.new([inner0[i], inner1[i], inner1[i + 1], inner0[i + 1]])
        bm.faces.new([outer0[i + 1], outer1[i + 1], outer1[i], outer0[i]])
        bm.faces.new([inner1[i], outer1[i], outer1[i + 1], inner1[i + 1]])
        bm.faces.new([inner0[i + 1], outer0[i + 1], outer0[i], inner0[i]])
    bm.faces.new([inner0[0], outer0[0], outer1[0], inner1[0]])
    bm.faces.new([inner1[n], outer1[n], outer0[n], inner0[n]])
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co; l[uv].uv = ((p.x + p.y) / T(material), p.z / T(material))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(MATS[material])
    md = o.modifiers.new("bev", "BEVEL"); md.width = thick * 0.45; md.segments = 3
    md2 = o.modifiers.new("sub", "SUBSURF"); md2.levels = 1; md2.render_levels = 2
    for p in me.polygons: p.use_smooth = True
    return _link(o, cname)
