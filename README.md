# A-105 Walkthrough

First-person walkable 3D model of flat A-105 (Type 5, 3BHK + Family, 2,011 sq ft) at Vanshika's Nature's Harmony, Bengaluru.
Walls traced to scale from the published Type-5 unit plan; interiors from the sample-flat walkthrough video.

- `index.html` — the walkthrough (three.js, static; no build step). WASD/mouse on desktop, drag on phones.
- `a105.json` — the model (glTF with embedded textures). `layout.json` — collision + room data. `minimap.png` — top-down render.
- `blender/` — editable Blender project and FBX for Unreal/Unity/Godot.
- `source/` — Blender Python scripts that generate the model.

Deploy: import this repo in Vercel as a static site (framework: Other, no build command).
