# Denoise the raw baked atlases with OIDN and encode them for the web as sRGB(L / LMAX).
# Run with LD_LIBRARY_PATH pointing at the oidn package's lib folder.
import bpy, numpy as np, json, os, glob, ctypes, oidn
from PIL import Image
ROOT = "/home/claude/house/build2"; OUT = "/home/claude/house/site/model"
LMAX = 6.0
lib = ctypes.CDLL(sorted(glob.glob(os.path.join(os.path.dirname(oidn.__file__), "lib.linux.x64", "libOpenImageDenoise.so*")))[0])
set1b = lib.oidnSetFilter1b; set1b.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]; set1b.restype = None

def encode(src, dst, fill=0):
    im = bpy.data.images.load(os.path.join(ROOT, src))
    W, H = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(H, W, 4)[:, :, :3].copy()
    # texels no triangle covered (tiny faces, chart gaps) are black: grow lit neighbours into them,
    # so bilinear lookups on small furniture faces never pick up black
    hole = px.sum(2) < 1e-5
    print(src, "empty texels", round(float(hole.mean()), 3))
    for _ in range(fill):
        if not hole.any(): break
        acc = np.zeros_like(px); cnt = np.zeros(px.shape[:2], np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                sh = np.roll(np.roll(px, dy, 0), dx, 1); ok = ~np.roll(np.roll(hole, dy, 0), dx, 1)
                acc += sh * ok[..., None]; cnt += ok
        grow = hole & (cnt > 0)
        px[grow] = acc[grow] / cnt[grow][:, None]; hole &= ~grow
    dev = oidn.NewDevice(oidn.DEVICE_TYPE_CPU); oidn.CommitDevice(dev)
    flt = oidn.NewFilter(dev, "RT"); out = np.zeros_like(px)
    oidn.SetSharedFilterImage(flt, "color", px, oidn.FORMAT_FLOAT3, W, H)
    oidn.SetSharedFilterImage(flt, "output", out, oidn.FORMAT_FLOAT3, W, H)
    set1b(flt, b"hdr", True)
    oidn.CommitFilter(flt); oidn.ExecuteFilter(flt)
    err = oidn.GetDeviceError(dev); oidn.ReleaseFilter(flt); oidn.ReleaseDevice(dev)
    v = np.clip(out / LMAX, 0, 1)
    srgb = np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1 / 2.4) - 0.055)
    u8 = (np.flipud(srgb) * 255 + 0.5).astype(np.uint8)       # Blender pixels start bottom-left
    Image.fromarray(u8).save(os.path.join(OUT, dst), quality=92, subsampling=0)
    print(src, "->", dst, "mean", float(out.mean()), "clipped", float((out > LMAX).mean()), "oidn err", err,
          round(os.path.getsize(os.path.join(OUT, dst)) / 1e6, 2), "MB")

encode("lightmap_raw.exr", "lightmap.jpg")
encode("lightmapV_raw.exr", "lightmapV.jpg", fill=3)
json.dump({"lmax": LMAX}, open(os.path.join(OUT, "bake.json"), "w"))
