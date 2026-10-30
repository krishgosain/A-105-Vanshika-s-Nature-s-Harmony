import bpy, re
bpy.ops.wm.open_mainfile(filepath="/home/claude/house/build2/A105_lux.blend")
base=lambda n: re.sub(r"\.\d{3}$","",n)
seen={}
for me in list(bpy.data.meshes):
    k=(base(me.name), len(me.vertices), len(me.polygons), tuple(m.name if m else "" for m in me.materials))
    if k in seen and seen[k]!=me: me.user_remap(seen[k])
    else: seen[k]=me
import hashlib
seeni={}
for im in list(bpy.data.images):
    k=hashlib.sha1(im.packed_file.data).hexdigest() if im.packed_file else (im.filepath or im.name, tuple(im.size))
    if k in seeni and seeni[k]!=im: im.user_remap(seeni[k])
    else: seeni[k]=im
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/house/build2/A105_Luxury_Vanshikas_Type5.blend", compress=True)
print("PACKED", len(bpy.data.images), "images")
