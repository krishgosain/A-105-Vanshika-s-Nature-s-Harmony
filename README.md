# Residence A-105 · Vanshika's Nature's Harmony

A photoreal 360° tour and real-time walkthrough of flat A-105, a Type 5, 3BHK + Family home (2,011 sq ft saleable) in Bengaluru.

- `index.html`: the 360° tour, with nine Cycles-rendered rooms, doorway hotspots, a floor plan, a guided tour and gyro look on phones.
- `walk.html`: the real-time first-person walkthrough. It uses the same Blender scene, materials and Cycles lighting as the 360° tour: the lighting is baked into two lightmaps (`model/lightmap.jpg` for architecture, `model/lightmapV.jpg` for furniture and decor), and reflections come from the living-room panorama. Deep links work: `walk.html#at=745,440,60` (plan x, plan y, heading).
- `pano/`: 3072×1536 equirectangular panoramas with 1536 px previews. `img/`: hero shots and the plan.
- `blender/A105_Luxury_Vanshikas_Type5.blend`: the editable scene, with textures packed in.
- `source/`: the Blender Python scripts that build, render, bake (`bake_v2.py`, `encode_lightmap.py`) and export (`export_baked.py`) the scene.

The walls are traced to scale from the published Type 5 unit plan. The furnishing is a luxury design concept.

Third-party models come from the Khronos glTF Sample Assets and are licensed CC BY 4.0: GlamVelvetSofa and SheenChair © Wayfair, DiffuseTransmissionPlant © DGG, plus glassware.

Deploy: this is a static site, so import the repo in Vercel with framework "Other" and no build step.
