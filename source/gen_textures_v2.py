# High-detail texture set for the luxury rebuild: colour + normal (+ roughness where useful).
import numpy as np, os, sys
from PIL import Image, ImageFilter, ImageOps, ImageDraw
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

def save(a, name, q=92):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=q)

def fbm(h, w, base=8, octaves=6, seed=None, tile=True):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        g = r.random((n, n))
        if tile:
            g = np.pad(g, ((0, 1), (0, 1)), mode="wrap")
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + (w // n if tile else 0), h + (h // n if tile else 0)), Image.BICUBIC)
        a = np.array(im, float)[:h, :w] / 255
        acc += a * amp; tot += amp; amp *= 0.5
    acc /= tot
    return (acc - acc.min()) / (acc.max() - acc.min() + 1e-9)

def normal_from_height(hgt, strength=2.0):
    gy, gx = np.gradient(hgt)
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(hgt)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.stack([(nx / l + 1) * 127.5, (ny / l + 1) * 127.5, (nz / l + 1) * 127.5], -1)

# ------------------------------------------------------------- Calacatta marble (floor slabs 1.2 m)
def marble(N, base, vein, gold, seed, nveins=5, fine=0.5):
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:N, 0:N] / N
    a = np.ones((N, N, 3)) * np.array(base, float)
    cloud = fbm(N, N, 4, 6, seed + 1)
    a += (cloud[..., None] - 0.5) * 18
    mask_total = np.zeros((N, N))
    for v in range(nveins):
        warp = fbm(N, N, 3, 6, seed + 10 + v)
        ang = r.uniform(0.3, 1.2) * (1 if r.random() > 0.5 else -1)
        f = (xx * np.cos(ang) + yy * np.sin(ang)) * r.uniform(1.2, 2.4) + warp * r.uniform(1.0, 1.8) + r.random()
        d = np.abs((f % 1.0) - 0.5)
        w = r.uniform(0.004, 0.012)
        m = np.exp(-(d / w) ** 2)
        halo = np.exp(-(d / (w * 6)) ** 2) * 0.35
        mask_total = np.maximum(mask_total, m)
        col = np.array(vein if r.random() > 0.35 else gold, float)
        a = a * (1 - m[..., None] * 0.85) + col * m[..., None] * 0.85
        a = a * (1 - halo[..., None] * 0.25) + col * halo[..., None] * 0.25
    # fine hair veins
    warp = fbm(N, N, 8, 5, seed + 99)
    f = (xx * 0.7 + yy * 1.3) * 9 + warp * 5
    d = np.abs((f % 1.0) - 0.5); m = np.exp(-(d / 0.006) ** 2) * fine
    a = a * (1 - m[..., None] * 0.5) + np.array(vein, float) * m[..., None] * 0.5
    return a, mask_total

N = 2048
a, m = marble(N, [242, 239, 234], [128, 124, 120], [176, 150, 112], 3, 5)
# slab joint (texture = one 1.2 m slab; thin joint on two edges)
a[:3, :] = a[:3, :] * 0.86; a[:, :3] = a[:, :3] * 0.86
save(a, "marble_calacatta.jpg")
hgt = np.zeros((N, N)); hgt[:3, :] = -1; hgt[:, :3] = -1
save(normal_from_height(np.array(Image.fromarray(((hgt + 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), float) / 255.0, 3), "marble_calacatta_n.png")
a, _ = marble(1024, [236, 233, 228], [140, 134, 128], [190, 160, 118], 21, 3, 0.3)
save(a, "marble_counter.jpg")
a, _ = marble(1024, [40, 40, 42], [175, 170, 160], [196, 168, 120], 31, 4, 0.2)
save(a, "marble_nero.jpg")
# travertine (warm beige, pores, layered bands)
yy, xx = np.mgrid[0:1024, 0:1024] / 1024
bands = np.sin((yy * 18 + fbm(1024, 1024, 4, 5, 41) * 3) * np.pi) * 0.5 + 0.5
pores = (fbm(1024, 1024, 64, 2, 42) > 0.78).astype(float)
a = np.array([214, 196, 168.]) * (0.92 + 0.08 * bands[..., None]) - pores[..., None] * 25
save(a, "travertine.jpg")
# grey stone (bathrooms) 1.2 m slab
c = fbm(1024, 1024, 6, 6, 51)
a = np.array([128, 126, 122.]) * (0.85 + 0.25 * c[..., None]); a[:3] *= 0.7; a[:, :3] *= 0.7
save(a, "stone_grey.jpg")
c = fbm(1024, 1024, 6, 6, 52)
a = np.array([206, 202, 196.]) * (0.9 + 0.12 * c[..., None]); a[:3] *= 0.85; a[:, :3] *= 0.85
save(a, "stone_light.jpg")

# ------------------------------------------------------------- woods
def grain(h, w, base, var, seed, rows=12, rays=True):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w))
    for cols, amp in [(w // 2, 0.45), (w // 7, 0.35), (w, 0.2)]:
        n = r.random((rows, cols))
        acc += np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255 * amp
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    # cathedral figure
    yy, xx = np.mgrid[0:h, 0:w] / max(h, w)
    fig = np.sin((xx * 9 + np.abs(yy - 0.5) * 2 + fbm(h, w, 3, 4, seed + 5) * 2.0) * np.pi * 2) * 0.5 + 0.5
    t = 0.65 * acc + 0.35 * fig
    return np.array(base, float)[None, None] * (1 - var / 2 + var * t[..., None]), t

a, t = grain(1024, 1024, [118, 72, 42], 0.45, 61); save(a, "walnut.jpg")
save(normal_from_height(t, 1.0), "walnut_n.png")
a, t = grain(1024, 1024, [196, 164, 124], 0.30, 62); save(a, "oak.jpg")
# fluted walnut: 32 flutes across 1 m texture -> ~3 cm reeds
N = 1024; x = np.linspace(0, 1, N, endpoint=False)
flute = np.sqrt(np.clip(1 - ((x * 32 % 1) * 2 - 1) ** 2, 0, 1))
hf = np.tile(flute, (N, 1))
a, _ = grain(N, N, [112, 66, 38], 0.4, 63)
a = a * (0.72 + 0.28 * hf[..., None])
save(a, "fluted_walnut.jpg"); save(normal_from_height(hf * 6, 1.2), "fluted_n.png")
# herringbone oak: texture 1.2 m, planks 0.6 x 0.1 m
N = 2048; px = N / 1.2
a = np.zeros((N, N, 3)); hgt = np.zeros((N, N))
yy, xx = np.mgrid[0:N, 0:N].astype(float)
u = (xx + yy) / np.sqrt(2); v = (yy - xx) / np.sqrt(2)
pw = 0.1 * px; pl = 0.6 * px
# herringbone indexing in rotated space
col = np.floor(u / pw); rowA = np.floor((v + col * pw) / pl)
idA = col * 1000 + rowA
cols = np.array([[176, 128, 84], [190, 140, 92], [164, 116, 76], [184, 134, 90], [170, 124, 82], [196, 148, 100]], float)
pal = cols[(np.abs(idA).astype(int) * 7919) % len(cols)]
g = fbm(N, N, 16, 4, 71)
a = pal * (0.88 + 0.2 * g[..., None])
edge = (np.abs(u / pw - np.round(u / pw)) < 0.03) | (np.abs(((v + col * pw) / pl) - np.round((v + col * pw) / pl)) < 0.006)
a[edge] *= 0.55; hgt[edge] = -1
save(a, "herringbone.jpg"); save(normal_from_height(np.array(Image.fromarray(((hgt + 1) * 127).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), float) / 255, 4), "herringbone_n.png")
# teak decking (balcony): planks 0.14 m across, texture 1.12 m
N = 1024; a, t = grain(N, N, [150, 102, 64], 0.35, 81)
for i in range(8):
    a[:, int(i * N / 8):int(i * N / 8) + 5] = [62, 44, 30]
save(a.transpose(1, 0, 2), "teak_deck.jpg")

# ------------------------------------------------------------- walls & fabrics
c = fbm(1024, 1024, 5, 7, 91)
a = np.array([226, 218, 206.]) * (0.95 + 0.07 * c[..., None]); save(a, "plaster.jpg")
save(normal_from_height(fbm(1024, 1024, 32, 4, 92), 0.6), "plaster_n.png")
def fabric_normal(seed, kind):
    N = 512
    if kind == "boucle":
        h = fbm(N, N, 48, 3, seed) + 0.6 * fbm(N, N, 96, 2, seed + 1)
        return normal_from_height(h, 5)
    if kind == "linen":
        yy, xx = np.mgrid[0:N, 0:N]
        h = (np.sin(xx * np.pi / 3) * 0.5 + np.sin(yy * np.pi / 3) * 0.5) + fbm(N, N, 32, 3, seed) * 1.5
        return normal_from_height(h, 1.5)
    if kind == "velvet":
        return normal_from_height(fbm(N, N, 24, 4, seed), 1.2)
    if kind == "wool":
        return normal_from_height(fbm(N, N, 64, 3, seed) + fbm(N, N, 8, 3, seed + 3) * 0.5, 4)
for k in ["boucle", "linen", "velvet", "wool"]:
    save(fabric_normal(100 + len(k), k), f"{k}_n.png")
# rug: warm ivory field with tonal border
N = 1024; c = fbm(N, N, 64, 3, 111)
a = np.array([214, 204, 186.]) * (0.9 + 0.12 * c[..., None])
b = 60; a[:b] = a[:b] * 0.78; a[-b:] *= 0.78; a[:, :b] *= 0.78; a[:, -b:] *= 0.78
save(a, "rug.jpg")

# ------------------------------------------------------------- abstract artworks (gallery-style canvases)
def painting(W, H, palette, seed, gold=True):
    r = np.random.default_rng(seed)
    im = Image.new("RGB", (W, H), tuple(palette[0]))
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(140):
        c = palette[r.integers(1, len(palette))]
        x0, y0 = r.integers(-W // 4, W), r.integers(-H // 4, H)
        w, h = r.integers(W // 10, W // 2), r.integers(H // 20, H // 3)
        d.ellipse([x0, y0, x0 + w, y0 + h], fill=(*c, int(r.integers(20, 70))))
    im = im.filter(ImageFilter.GaussianBlur(18))
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(60):
        c = palette[r.integers(1, len(palette))]
        x0, y0 = r.integers(0, W), r.integers(0, H)
        pts = [(x0 + r.normal(0, W / 6) * t, y0 + r.normal(0, H / 10) * t) for t in np.linspace(0, 1, 6)]
        d.line(pts, fill=(*c, int(r.integers(60, 160))), width=int(r.integers(6, 40)), joint="curve")
    if gold:
        for i in range(10):
            x0, y0 = r.integers(0, W), r.integers(0, H)
            pts = [(x0 + r.normal(0, W / 5) * t, y0 + r.normal(0, H / 12) * t) for t in np.linspace(0, 1, 8)]
            d.line(pts, fill=(201, 164, 92, 230), width=int(r.integers(3, 14)), joint="curve")
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    # canvas texture
    a = np.array(im, float); a += (fbm(H, W, 128, 2, seed + 7, tile=False)[..., None] - 0.5) * 18
    return a
save(painting(2000, 1200, [[236, 230, 218], [28, 52, 60], [196, 120, 82], [230, 214, 190], [52, 92, 96], [160, 150, 136]], 201), "art_living.jpg")
save(painting(1200, 1500, [[226, 216, 200], [120, 92, 70], [32, 40, 48], [200, 180, 150], [170, 100, 72]], 202), "art_dining.jpg")
save(painting(1600, 1000, [[214, 206, 196], [64, 74, 86], [150, 160, 166], [236, 232, 226], [110, 96, 86]], 203), "art_br3.jpg")
save(painting(1000, 1400, [[232, 224, 212], [24, 30, 36], [190, 150, 96], [140, 120, 100]], 204), "art_foyer.jpg")
print("textures v2 ok")
