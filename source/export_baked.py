# Web export of the baked scene: every object keeps its own material (no merging of recoloured copies),
# BakedA and BakedV carry lightmap UVs (TEXCOORD_1) into lightmap.jpg and lightmapV.jpg.
import bpy, os, re
ROOT = "/home/claude/house/build2"; OUT = "/home/claude/house/site/model"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "A105_baked.blend"))
sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type == 'LIGHT' or o.type == 'CAMERA':
        bpy.data.objects.remove(o, do_unlink=True)
# live (unbaked) dense meshes: decimate for the web
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in ("BakedA", "BakedV") and len(o.data.polygons) > 6000:
        md = o.modifiers.new("dec", "DECIMATE"); md.ratio = max(0.15, 6000 / len(o.data.polygons))
# glTF sheen has no weight: fold Blender's Sheen Weight into the tint so velvet/linen read as in Cycles
for m in bpy.data.materials:
    if not (m.use_nodes and m.node_tree): continue
    for nd in m.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED' and not nd.inputs["Sheen Tint"].links and not nd.inputs["Sheen Weight"].links:
            w = nd.inputs["Sheen Weight"].default_value; t = nd.inputs["Sheen Tint"].default_value
            nd.inputs["Sheen Tint"].default_value = (t[0] * w, t[1] * w, t[2] * w, 1)
            if w > 0: nd.inputs["Sheen Weight"].default_value = 1.0
# images: share byte-identical copies (repeated imports of the same model), cap size.
# Imported models name their textures Image_0, Image_1... so names alone can't identify a texture.
import hashlib
def key(im):
    if im.packed_file: return hashlib.sha1(im.packed_file.data).hexdigest()
    return (im.filepath, tuple(im.size)) if im.filepath else ("gen", im.name)
seeni = {}
for im in list(bpy.data.images):
    if im.name.startswith(("Lightmap", "LM_")): continue
    k = key(im)
    if k in seeni and seeni[k] != im: im.user_remap(seeni[k])
    else: seeni[k] = im
for img in bpy.data.images:
    if img.name.startswith(("Lightmap", "LM_")): continue
    lim = 1024 if not img.name.startswith("Image") else 512
    if img.users and img.size[0] > lim: img.scale(lim, max(1, int(img.size[1] * lim / img.size[0])))
# remove the bake target from the scene's images so it isn't exported
for im in [i for i in bpy.data.images if i.name.startswith(("Lightmap", "LM_"))]: bpy.data.images.remove(im)
for n in ("BakedA", "BakedV"):
    me = bpy.data.objects[n].data; me.uv_layers.active = me.uv_layers["UVMap"]
kw = dict(filepath=os.path.join(OUT, "a105.glb"), export_format='GLB', export_apply=True,
          export_image_format='JPEG', export_jpeg_quality=85, export_lights=False, export_cameras=False,
          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
          export_draco_color_quantization=10, export_draco_texcoord_quantization=14)
bpy.ops.export_scene.gltf(**kw)
print("EXPORT OK", os.path.getsize(kw["filepath"]) / 1e6, "MB")
