import bpy, os, sys
ROOT = "/home/claude/house/build"
WEB = "/home/claude/house/web"
os.makedirs(WEB, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "A105_raw.blend"))
os.makedirs(os.path.join(ROOT, "unreal"), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT, "unreal", "A105_Vanshikas_Type5.fbx"), apply_unit_scale=True,
                         use_mesh_modifiers=True, path_mode='COPY', embed_textures=True, axis_forward='-Z', axis_up='Y')
# web: smaller textures
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
# drop objects that only matter for offline renders
for o in list(bpy.data.objects):
    if o.name.startswith(("Neighbour",)):
        bpy.data.objects.remove(o, do_unlink=True)
for img in bpy.data.images:
    img.file_format = 'JPEG'
bpy.ops.export_scene.gltf(filepath=os.path.join(WEB, "a105.glb"), export_format='GLB',
                          export_apply=True, export_image_format='JPEG', export_jpeg_quality=82,
                          export_lights=False, export_cameras=False, use_selection=False)
print("EXPORT OK", os.path.getsize(os.path.join(WEB, "a105.glb")) / 1e6, "MB")
