import bpy, os
ROOT="/home/claude/house/build2"; OUT="/home/claude/house/site/model"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,"A105_lux.blend"))
import re
# web build: drop tiny props with very heavy meshes, decimate dense scans
DROP=("tea_cup","tea_saucer","SpecularSilkPouf","olives","glassDish","goldLeaf","glassCover","shot silk")
for o in list(bpy.data.objects):
    if o.type=='MESH' and (any(k.lower() in o.name.lower() for k in DROP) or any(k.lower() in o.data.name.lower() for k in DROP)):
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    if o.type=='MESH' and len(o.data.polygons)>6000:
        md=o.modifiers.new("dec","DECIMATE"); md.ratio=max(0.15, 6000/len(o.data.polygons))
base=lambda n: re.sub(r"\.\d{3}$","",n)
# share identical imported meshes, materials and images so repeated chairs/plants are stored once
seen={}
for me in list(bpy.data.meshes):
    k=(base(me.name), len(me.vertices), len(me.polygons))
    if k in seen and seen[k]!=me: me.user_remap(seen[k])
    else: seen[k]=me
seenm={}
for m in list(bpy.data.materials):
    k=base(m.name)
    if k in seenm and seenm[k]!=m and not m.name.startswith(("velvet","boucle","linen")) and "fabric" not in k.lower(): m.user_remap(seenm[k])
    else: seenm.setdefault(k,m)
seeni={}
for im in list(bpy.data.images):
    k=(base(im.name), tuple(im.size))
    if k in seeni and seeni[k]!=im: im.user_remap(seeni[k])
    else: seeni[k]=im
for img in bpy.data.images:
    lim = 1024 if not img.name.startswith("Image") else 512
    if img.users and img.size[0] > lim: img.scale(lim, max(1, int(img.size[1]*lim/img.size[0])))
for o in list(bpy.data.objects):
    if o.type=='LIGHT' or o.name.startswith(("Ground",)): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,"a105.glb"), export_format='GLB', export_apply=True,
    export_image_format='JPEG', export_jpeg_quality=85, export_lights=False, export_cameras=False, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7)
print("EXPORT OK", os.path.getsize(os.path.join(OUT,"a105.glb"))/1e6, "MB")
