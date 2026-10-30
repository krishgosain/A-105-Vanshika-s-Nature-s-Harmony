# A-105 luxury rebuild. Walls traced from the Type-5 plan (74 px = 1 m); furnishing is a luxury design concept.
import bpy, math, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix
from lib_v2 import *
import lib_v2

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ============================================================== MATERIALS
mat("plaster", (0.86, 0.82, 0.76), tex="plaster.jpg", normal="plaster_n.png", nstr=0.25, tile=2.0, rough=0.9)
mat("plaster_ext", (0.82, 0.80, 0.77), rough=0.9)
mat("ceiling", (0.93, 0.92, 0.90), rough=0.92)
mat("marble_floor", tex="marble_calacatta.jpg", normal="marble_calacatta_n.png", nstr=0.4, tile=1.2, rough=0.07, coat=0.3)
mat("marble_counter", tex="marble_counter.jpg", tile=1.4, rough=0.06, coat=0.4)
mat("marble_slab", tex="marble_counter.jpg", tile=2.4, rough=0.05, coat=0.5)
mat("marble_nero", tex="marble_nero.jpg", tile=1.4, rough=0.06, coat=0.4)
mat("travertine", tex="travertine.jpg", tile=0.8, rough=0.45)
mat("herringbone", tex="herringbone.jpg", normal="herringbone_n.png", nstr=0.5, tile=1.2, rough=0.32, coat=0.15)
mat("walnut", tex="walnut.jpg", normal="walnut_n.png", nstr=0.15, tile=1.0, rough=0.38)
mat("walnut_dark", (0.75, 0.75, 0.75), tex="walnut.jpg", tile=0.8, rough=0.35)
mat("fluted_walnut", tex="fluted_walnut.jpg", normal="fluted_n.png", nstr=1.0, tile=1.0, rough=0.4)
mat("oak", tex="oak.jpg", tile=1.0, rough=0.42)
mat("teak_deck", tex="teak_deck.jpg", tile=1.12, rough=0.55)
mat("stone_grey", tex="stone_grey.jpg", tile=1.2, rough=0.35)
mat("stone_light", tex="stone_light.jpg", tile=1.2, rough=0.25)
mat("brass", (0.80, 0.62, 0.36), rough=0.22, metal=1.0)
mat("brass_brushed", (0.76, 0.60, 0.38), rough=0.35, metal=1.0)
mat("bronze", (0.30, 0.22, 0.16), rough=0.3, metal=1.0)
mat("black_metal", (0.025, 0.025, 0.028), rough=0.35, metal=0.6)
mat("chrome", (0.9, 0.9, 0.9), rough=0.08, metal=1.0)
mat("glass", (0.92, 0.95, 0.96), rough=0.01, alpha=0.12, ior=1.5)
mat("glass_bronze", (0.25, 0.18, 0.12), rough=0.05, alpha=0.55)
mat("glass_fluted", (0.50, 0.40, 0.28), normal="fluted_n.png", nstr=0.8, tile=0.25, rough=0.2, alpha=0.62)
mat("mirror", (0.92, 0.92, 0.92), rough=0.02, metal=1.0)
mat("smoked_mirror", (0.32, 0.30, 0.28), rough=0.03, metal=1.0)
mat("lacquer_taupe", (0.40, 0.36, 0.32), rough=0.32, coat=0.2)
mat("lacquer_ivory", (0.86, 0.83, 0.77), rough=0.22, coat=0.4)
mat("lacquer_black", (0.03, 0.03, 0.03), rough=0.2, coat=0.5)
mat("porcelain", (0.97, 0.97, 0.96), rough=0.08, coat=0.6)
mat("velvet_emerald", (0.018, 0.14, 0.09), normal="velvet_n.png", nstr=0.3, tile=0.4, rough=0.75, sheen=1.0, sheen_tint=(0.6, 0.9, 0.7))
mat("velvet_cognac", (0.36, 0.16, 0.06), normal="velvet_n.png", nstr=0.3, tile=0.4, rough=0.7, sheen=1.0, sheen_tint=(1, 0.8, 0.6))
mat("velvet_gold", (0.55, 0.40, 0.16), normal="velvet_n.png", nstr=0.3, tile=0.4, rough=0.6, sheen=1.0)
mat("velvet_taupe", (0.30, 0.25, 0.21), normal="velvet_n.png", nstr=0.3, tile=0.4, rough=0.75, sheen=0.8)
mat("boucle", (0.84, 0.80, 0.73), normal="boucle_n.png", nstr=0.9, tile=0.25, rough=0.95, sheen=0.4)
mat("linen_white", (0.92, 0.90, 0.86), normal="linen_n.png", nstr=0.4, tile=0.15, rough=0.9, sheen=0.3)
mat("linen_sand", (0.70, 0.62, 0.52), normal="linen_n.png", nstr=0.4, tile=0.15, rough=0.9, sheen=0.3)
mat("linen_charcoal", (0.12, 0.12, 0.13), normal="linen_n.png", nstr=0.4, tile=0.15, rough=0.9, sheen=0.3)
mat("leather_cognac", (0.22, 0.09, 0.035), rough=0.4, coat=0.25)
mat("fabric_charcoal", (0.08, 0.085, 0.09), normal="linen_n.png", nstr=0.5, tile=0.2, rough=0.9, sheen=0.4)
mat("fabric_greige", (0.55, 0.50, 0.44), normal="linen_n.png", nstr=0.5, tile=0.2, rough=0.9, sheen=0.4)
mat("fabric_grey", (0.30, 0.30, 0.31), normal="linen_n.png", nstr=0.5, tile=0.2, rough=0.9, sheen=0.4)
mat("rug", tex="rug.jpg", normal="wool_n.png", nstr=1.0, tile=3.0, rough=1.0)
mat("rug_unit", tex="rug.jpg", normal="wool_n.png", nstr=1.0, tile=1.0, rough=1.0)
mat("sheer", (0.96, 0.95, 0.92), rough=0.9, alpha=0.42, tile=0.5)
mat("drape_sand", (0.62, 0.55, 0.46), normal="linen_n.png", nstr=0.5, tile=0.2, rough=0.95, sheen=0.5)
mat("drape_charcoal", (0.10, 0.10, 0.11), normal="linen_n.png", nstr=0.5, tile=0.2, rough=0.95, sheen=0.5)
mat("led", (1, 0.9, 0.75), emit=(1.0, 0.82, 0.60), emit_strength=18)
mat("led_soft", (1, 0.9, 0.75), emit=(1.0, 0.85, 0.68), emit_strength=6)
mat("opal", (0.95, 0.93, 0.9), rough=0.4, emit=(1.0, 0.86, 0.66), emit_strength=8)
mat("screen", (0.004, 0.004, 0.005), rough=0.04, coat=1.0)
mat("plant_green", (0.10, 0.25, 0.08), rough=0.6, subsurface=0.1)
mat("pot_stone", (0.24, 0.23, 0.22), rough=0.8)
mat("pot_cream", (0.82, 0.78, 0.72), rough=0.7)
mat("book_a", (0.75, 0.70, 0.62), rough=0.7); mat("book_b", (0.12, 0.16, 0.18), rough=0.6); mat("book_c", (0.45, 0.30, 0.20), rough=0.6)
mat("ceramic_black", (0.03, 0.03, 0.03), rough=0.25, coat=0.4)
mat("ceramic_white", (0.9, 0.88, 0.84), rough=0.3, coat=0.3)
mat("backdrop", (1, 1, 1), tex="backdrop_garden.jpg", tile=1.0, rough=1.0, emit=(1, 1, 1), emit_strength=0.0)
for a in ["art_living.jpg", "art_dining.jpg", "art_br3.jpg", "art_foyer.jpg", "art_orange_l.png", "art_orange_r.png", "art_coral.png", "art_sticks.png"]:
    mat(a.split(".")[0], tex=a, tile=1.0, rough=0.75)
mat("chevron", (0.8, 0.8, 0.8), tex="chevron.jpg", tile=1.0, rough=0.9, sheen=0.5)
# backdrop: emission driven by its own texture
bm_ = MATS["backdrop"].node_tree
bsdf = bm_.nodes["Principled BSDF"]; img_node = [n for n in bm_.nodes if n.type == 'TEX_IMAGE'][0]
bm_.links.new(img_node.outputs["Color"], bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = 1.6

# ============================================================== WALLS (with skirting, doors, windows)
def wall(name, px0, py0, px1, py1, openings=(), material="plaster", skirting=True):
    horiz = (px1 - px0) >= (py1 - py0)
    lo, hi = (px0, px1) if horiz else (py0, py1)
    ops = sorted(openings, key=lambda o: o["a"]); cur = lo; k = [0]
    def seg(a, b, z0, z1, tag, collide, skirt):
        k[0] += 1
        if b - a <= 0.01 or z1 - z0 <= 0.001: return
        nm = f"{name}_{tag}{k[0]}"
        if horiz: box(nm, X(a), Y(py0), z0, X(b), Y(py1), z1, material, "Walls", collide)
        else:     box(nm, X(px0), Y(a), z0, X(px1), Y(b), z1, material, "Walls", collide)
        if skirt and skirting and z0 == 0:
            t, hh = 0.012, 0.09
            if horiz:
                for yy, sg in [(Y(py0), 1), (Y(py1), -1)]:
                    box(nm + f"_sk{sg}", X(a), yy, 0, X(b), yy + sg * t, hh, "lacquer_black", "Walls")
            else:
                for xx, sg in [(X(px0), -1), (X(px1), 1)]:
                    box(nm + f"_sk{sg}", xx, Y(a), 0, xx + sg * t, Y(b), hh, "lacquer_black", "Walls")
    for o in ops:
        seg(cur, o["a"], 0, H, "w", True, True)
        if o["bot"] > 0: seg(o["a"], o["b"], 0, o["bot"], "sill", o["bot"] > 0.5, False)
        seg(o["a"], o["b"], o["top"], H, "lintel", False, False)
        fill(name, o, horiz, px0, py0, px1, py1)
        cur = o["b"]
    seg(cur, hi, 0, H, "w", True, True)

def fill(name, o, horiz, px0, py0, px1, py1):
    kind, a, b, bot, top = o["kind"], o["a"], o["b"], o["bot"], o["top"]
    if horiz:
        c = (Y(py0) + Y(py1)) / 2; th = abs(Y(py1) - Y(py0)); A, B = X(a), X(b)
    else:
        c = (X(px0) + X(px1)) / 2; th = abs(X(px1) - X(px0)); A, B = Y(a), Y(b)
    lo, hi = min(A, B), max(A, B)
    def fb(nm, u0, u1, z0, z1, mt, d0, d1):   # box spanning along-wall [u0,u1], across-wall [c+d0, c+d1]
        if horiz: box(nm, u0, c + d0, z0, u1, c + d1, z1, mt, "Openings")
        else:     box(nm, c + d0, u0, z0, c + d1, u1, z1, mt, "Openings")
    if kind in ("window", "slider"):
        f = 0.045; d = 0.035
        for nm, u0, u1, z0, z1 in [("t", lo, hi, top - f, top), ("b", lo, hi, bot, bot + f), ("l", lo, lo + f, bot, top), ("r", hi - f, hi, bot, top)]:
            fb(f"{name}_wf{nm}", u0, u1, z0, z1, "black_metal", -d, d)
        if kind == "window":
            n = max(1, round((hi - lo) / 0.9))
            for i in range(1, n):
                u = lo + (hi - lo) * i / n
                fb(f"{name}_wm{i}", u - 0.02, u + 0.02, bot, top, "black_metal", -d * 0.8, d * 0.8)
            fb(f"{name}_glass", lo + f, hi - f, bot + f, top - f, "glass", -0.004, 0.004)
        else:
            mid = (lo + hi) / 2
            fb(f"{name}_pA", lo + f, mid + 0.04, bot + f, top - f, "glass", -0.025, -0.015)
            fb(f"{name}_pAf", mid, mid + 0.04, bot + f, top - f, "black_metal", -0.03, -0.01)
            fb(f"{name}_pB", lo + f + 0.03, mid + 0.07, bot + f, top - f, "glass", 0.015, 0.025)
            fb(f"{name}_pBf", mid + 0.03, mid + 0.07, bot + f, top - f, "black_metal", 0.01, 0.03)
            COLLIDERS.append(([lo, c - 0.05, mid + 0.07, c + 0.05] if horiz else [c - 0.05, lo, c + 0.05, mid + 0.07]))
    elif kind == "door":
        leafm = o.get("leaf", "walnut"); trim = o.get("trim", "black_metal")
        aw, ad = 0.06, 0.018                                  # architrave width / projection
        # jamb lining (inside the opening) + head
        fb(f"{name}_jl", lo, lo + 0.02, 0, top, leafm, -th / 2, th / 2)
        fb(f"{name}_jr", hi - 0.02, hi, 0, top, leafm, -th / 2, th / 2)
        fb(f"{name}_jh", lo, hi, top - 0.02, top, leafm, -th / 2, th / 2)
        for sg in (-1, 1):                                    # architraves on both faces
            d0, d1 = (th / 2 + 0.001, th / 2 + ad) if sg > 0 else (-th / 2 - ad, -th / 2 - 0.001)
            fb(f"{name}_al{sg}", lo - aw, lo, 0, top + aw, trim, d0, d1)
            fb(f"{name}_ar{sg}", hi, hi + aw, 0, top + aw, trim, d0, d1)
            fb(f"{name}_ah{sg}", lo - aw, hi + aw, top, top + aw, trim, d0, d1)
        # leaf open at 90 degrees, clear of the wall face
        width = hi - lo - 0.05
        hinge_lo = (o.get("hinge", "a") == "a") == (A <= B)
        hinge = lo + 0.025 if hinge_lo else hi - 0.025
        along = 1 if hinge_lo else -1
        side = o.get("swing", 1)
        if horiz:
            out = Vector((0, -side, 0)); hp = Vector((hinge, c, 0)); al = Vector((along, 0, 0))
        else:
            out = Vector((side, 0, 0)); hp = Vector((c, hinge, 0)); al = Vector((0, along, 0))
        face = hp + out * (th / 2 + 0.012)
        lt = 0.045
        cen = face + out * (width / 2) + al * (lt / 2 + 0.005)
        ang = math.degrees(math.atan2(out.y, out.x)) - 90
        boxc(f"{name}_leaf", cen.x, cen.y, 0.008, lt, width, top - 0.02, leafm, "Openings", rot=ang)
        # vertical grooves (proud, so they never coincide with the leaf faces)
        for g in (-0.18, 0.18):
            p = cen + out * g
            for sgn in (-1, 1):
                q = p + al * sgn * (lt / 2 + 0.0015)
                boxc(f"{name}_gr{g}{sgn}", q.x, q.y, 0.15, 0.003, 0.006, top - 0.35, "lacquer_black", "Openings", rot=ang)
        # brass lever handles on both faces
        hpnt = face + out * (width - 0.08)
        for sgn in (-1, 1):
            q = hpnt + al * (lt / 2 + 0.005 + 0.03) * sgn + al * (lt / 2 + 0.005) * 0
            q = (face + out * (width - 0.08)) + al * ((lt / 2 + 0.005) + sgn * (lt / 2 + 0.03))
            boxc(f"{name}_hd{sgn}", q.x, q.y, 1.02, 0.02, 0.14, 0.02, "brass", "Openings", rot=ang, bevel=0.008)
            boxc(f"{name}_ro{sgn}", q.x, q.y, 0.99, 0.02, 0.05, 0.08, "brass", "Openings", rot=ang, bevel=0.008)

def D(a, b, hinge="a", swing=1, **kw):
    d = dict(a=a, b=b, bot=0, top=DOOR_H, kind="door", hinge=hinge, swing=swing); d.update(kw); return d
def W(a, b, bot=0.75, top=2.4): return dict(a=a, b=b, bot=bot, top=top, kind="window")
def SL(a, b): return dict(a=a, b=b, bot=0, top=SLIDE_H, kind="slider")

wall("MasterWest", 45, 160, 55, 752, [W(290, 368, 0.6, 2.4)])
wall("BalconyT1", 180, 160, 192, 292)
wall("MasterNorth", 55, 288, 365, 297, [SL(70, 180), D(238, 300, hinge="a", swing=-1)])
wall("T1North", 180, 160, 438, 172, [W(195, 240, 1.6, 2.3)])
wall("MasterEast", 365, 172, 378, 557, [D(492, 557, hinge="b", swing=-1)])
wall("MasterSouth", 45, 597, 313, 605)
wall("T3North", 313, 557, 450, 564, [D(378, 437, hinge="b", swing=1)])
wall("T3West", 313, 564, 325, 745, [W(687, 740, 1.6, 2.3)], skirting=False)
wall("T3East", 437, 564, 450, 752)
wall("BR3South", 378, 462, 635, 470, [D(572, 632, hinge="b", swing=-1)])
wall("NorthMid", 438, 160, 935, 172, [SL(450, 572), SL(692, 872)])
wall("BR3Living", 635, 172, 649, 470)
wall("T2West", 922, 172, 935, 385)
wall("T2South", 935, 378, 1047, 385)
wall("T2North", 935, 160, 1047, 172, [W(960, 1010, 1.7, 2.3)])
wall("BR2West", 1047, 160, 1057, 452, [D(318, 376, hinge="a", swing=-1), D(390, 450, hinge="b", swing=1)])
wall("BR2North", 1057, 160, 1325, 172, [SL(1117, 1253)])
wall("BR2East", 1313, 172, 1325, 452)
wall("BR2South", 1047, 452, 1420, 462)
wall("MainDoorLine", 1137, 462, 1150, 562, [D(475, 557, hinge="a", swing=-1, leaf="walnut_dark", trim="brass_brushed")])
wall("KitchenEast", 1137, 562, 1150, 850)
wall("KitchenNorth", 935, 562, 1137, 568)
box("Pillar", X(905), Y(592), 0, X(935), Y(555), H, "plaster", "Walls", True)
wall("KitchenSouth", 847, 745, 1137, 752, [D(1002, 1060, hinge="b", swing=1)])
wall("DiningSouth", 313, 745, 847, 752, [W(712, 845, 0.6, 2.4)])
wall("UtilityWest", 922, 752, 935, 850)
box("UtilityParapet", X(935), Y(850), 0, X(1137), Y(842), 1.0, "plaster", "Walls", True)
wall("VestibuleSouth", 1150, 583, 1420, 597)
wall("VestibuleEnd", 1410, 462, 1420, 583)
for nm, r in {"ShaftW": (248, 95, 262, 160), "ShaftE": (365, 95, 378, 160), "Shaft2W": (922, 95, 935, 160), "Shaft2E": (1047, 95, 1057, 160)}.items():
    box(nm, X(r[0]), Y(r[3]), 0, X(r[2]), Y(r[1]), H, "plaster_ext", "Walls", True)
box("ShaftN1", X(248), Y(98), 0, X(378), Y(95), H, "plaster_ext", "Walls", True)
box("ShaftN2", X(922), Y(98), 0, X(1057), Y(95), H, "plaster_ext", "Walls", True)

# ============================================================== FLOORS / CEILINGS
def floor(name, px0, py0, px1, py1, material, z=0.0, cname="Floors"):
    box(name, X(px0), Y(py1), z - 0.05, X(px1), Y(py0), z, material, cname)
floor("Floor_Main", 55, 172, 1137, 745, "marble_floor")
floor("Floor_BR2", 1137, 172, 1313, 452, "marble_floor")
floor("Floor_DoorSill", 1137, 475, 1150, 557, "marble_nero", 0.003)
box("Floor_Master", X(55), Y(557), 0, X(365), Y(297), 0.006, "herringbone", "Floors")
box("Floor_Master2", X(55), Y(597), 0, X(313), Y(557), 0.006, "herringbone", "Floors")
for nm, r in {"T1": (192, 172, 365, 288), "T2": (935, 172, 1047, 378), "T3": (325, 564, 437, 745)}.items():
    box("Floor_" + nm, X(r[0]), Y(r[3]), 0, X(r[2]), Y(r[1]), 0.006, "stone_grey", "Floors")
floor("Floor_Utility", 935, 752, 1137, 842, "stone_grey", -0.02)
floor("Floor_Vestibule", 1150, 462, 1410, 583, "marble_nero", 0.0)
# one continuous balcony along the whole north facade (master -> living -> bedroom 2)
floor("Balcony_Deck", 55, 40, 1313, 160, "teak_deck", -0.03)
floor("Balcony_Master", 55, 160, 180, 288, "teak_deck", -0.03)
floor("Slab_Below", 30, 20, 1430, 870, "plaster_ext", -0.1, "Exterior")
box("Balcony_Soffit", X(55), Y(160), H + 0.15, X(1313), Y(40), H + 0.35, "plaster_ext", "Exterior")
box("Balcony_SoffitM", X(55), Y(288), H + 0.15, X(180), Y(160), H + 0.35, "plaster_ext", "Exterior")
for nm, (a, b) in {"RailN": ((55, 37), (1313, 41))}.items():
    box(nm + "_glass", X(a[0]), Y(b[1]), -0.03, X(b[0]), Y(a[1]), 1.05, "glass", "Exterior", True)
    box(nm + "_cap", X(a[0]), Y(b[1]) - 0.01, 1.05, X(b[0]), Y(a[1]) + 0.01, 1.09, "black_metal", "Exterior")
for nm, xx in {"RailW": 52, "RailE": 1313}.items():
    box(nm + "_glass", X(xx), Y(160), -0.03, X(xx + 3), Y(40), 1.05, "glass", "Exterior", True)
    box(nm + "_cap", X(xx) - 0.01, Y(160), 1.05, X(xx + 3) + 0.01, Y(40), 1.09, "black_metal", "Exterior")
for i in range(0, 14):
    xx = 55 + i * (1313 - 55) / 13
    box(f"RailPost{i}", X(xx) - 0.02, Y(41) - 0.0, -0.03, X(xx) + 0.02, Y(37), 1.05, "black_metal", "Exterior")

box("Ceiling", X(45), Y(752), H, X(1150), Y(160), H + 0.12, "ceiling", "Ceiling")
box("Ceiling_Vest", X(1150), Y(597), H, X(1420), Y(452), H + 0.12, "ceiling", "Ceiling")
box("Ceiling_BR2", X(1150), Y(462), H, X(1325), Y(160), H + 0.12, "ceiling", "Ceiling")

# cove-lit false ceilings: perimeter band dropped 20 cm, LED hidden in the step, glowing onto the recessed field
COVES = {"Living": (649, 172, 922, 462), "Dining": (450, 535, 905, 745), "BR2": (1057, 172, 1313, 452),
         "BR3": (378, 172, 635, 462), "Master": (55, 297, 365, 597)}
def cove(name, px0, py0, px1, py1, band=0.42, drop=0.20):
    x0, x1, y1, y0 = X(px0), X(px1), Y(py0), Y(py1)  # y0 south (smaller), y1 north
    z0 = H - drop
    for nm, a in {"N": (x0, y1 - band, x1, y1), "S": (x0, y0, x1, y0 + band), "W": (x0, y0 + band, x0 + band, y1 - band), "E": (x1 - band, y0 + band, x1, y1 - band)}.items():
        box(f"Cove_{name}_{nm}", a[0], a[1], z0, a[2], a[3], H, "ceiling", "Ceiling")
    # lip + hidden LED strip on the inner edge
    for nm, a in {"N": (x0 + band, y1 - band - 0.03, x1 - band, y1 - band), "S": (x0 + band, y0 + band, x1 - band, y0 + band + 0.03),
                  "W": (x0 + band, y0 + band, x0 + band + 0.03, y1 - band), "E": (x1 - band - 0.03, y0 + band, x1 - band, y1 - band)}.items():
        box(f"CoveLip_{name}_{nm}", a[0], a[1], z0 - 0.0, a[2], a[3], z0 + 0.06, "ceiling", "Ceiling")
    for nm, a in {"N": (x0 + band - 0.06, y1 - band - 0.04, x1 - band + 0.06, y1 - band - 0.03), "S": (x0 + band - 0.06, y0 + band + 0.03, x1 - band + 0.06, y0 + band + 0.04),
                  "W": (x0 + band + 0.03, y0 + band, x0 + band + 0.04, y1 - band), "E": (x1 - band - 0.04, y0 + band, x1 - band - 0.03, y1 - band)}.items():
        box(f"CoveLED_{name}_{nm}", a[0], a[1], z0 + 0.06, a[2], a[3], z0 + 0.075, "led", "Ceiling")
    return z0
for k, r in COVES.items():
    cove(k, *r)
# linear profile band through foyer and hall (walnut slats + two LED lines)
box("HallBand", X(470), Y(528), H - 0.03, X(1137), Y(482), H, "fluted_walnut", "Ceiling")
box("HallLED_N", X(470), Y(484), H - 0.035, X(1137), Y(482), H - 0.03, "led", "Ceiling")
box("HallLED_S", X(470), Y(528), H - 0.035, X(1137), Y(526), H - 0.03, "led", "Ceiling")

SPOTS = []   # (x, y, z, watts)
def spot(px, py, z=None, w=18):
    SPOTS.append((X(px), Y(py), (z if z is not None else H - 0.2) - 0.005, w))
    zz = (z if z is not None else H - 0.2)
    cyl(f"Spot{len(SPOTS)}", X(px), Y(py), zz - 0.008, 0.035, 0.008, "black_metal", "Ceiling", 20)
    cyl(f"SpotLens{len(SPOTS)}", X(px), Y(py), zz - 0.010, 0.022, 0.003, "led_soft", "Ceiling", 16)

# ============================================================== LIVING
lx0, lx1, ly_n, ly_s = X(649), X(922), Y(172), Y(462)
# TV wall: fluted walnut cladding with a book-matched marble slab and backlit edges
box("TV_flutes", lx0, Y(455), 0, lx0 + 0.04, Y(178), H - 0.2, "fluted_walnut", "Decor")
box("TV_marble", lx0 + 0.04, Y(300) - 1.0, 0, lx0 + 0.07, Y(300) + 1.0, H - 0.2, "marble_slab", "Decor")
for s_ in (-1, 1):
    box(f"TV_glow{s_}", lx0 + 0.041, Y(300) + s_ * 1.0 - (0.01 if s_ > 0 else 0), 0.2, lx0 + 0.05, Y(300) + s_ * 1.0 + (0.0 if s_ > 0 else 0.01), H - 0.25, "led_soft", "Decor")
box("TV", lx0 + 0.075, Y(300) - 0.84, 0.82, lx0 + 0.105, Y(300) + 0.84, 1.79, "screen", "Furniture")
box("TV_bezel", lx0 + 0.07, Y(300) - 0.845, 0.815, lx0 + 0.076, Y(300) + 0.845, 1.795, "black_metal", "Furniture")
box("Console", lx0 + 0.07, Y(300) - 1.25, 0.24, lx0 + 0.52, Y(300) + 1.25, 0.52, "walnut", "Furniture", True, bevel=0.01)
box("Console_brass", lx0 + 0.52, Y(300) - 1.25, 0.36, lx0 + 0.525, Y(300) + 1.25, 0.38, "brass", "Furniture")
box("Console_top", lx0 + 0.07, Y(300) - 1.26, 0.52, lx0 + 0.53, Y(300) + 1.26, 0.545, "marble_nero", "Furniture", bevel=0.005)
box("Console_glow", lx0 + 0.1, Y(300) - 1.2, 0.235, lx0 + 0.5, Y(300) + 1.2, 0.24, "led_soft", "Furniture")
cyl("Console_vase1", lx0 + 0.3, Y(300) + 0.95, 0.545, 0.09, 0.42, "ceramic_black", "Decor", 32, r2=0.05)
cyl("Console_vase2", lx0 + 0.3, Y(300) + 0.75, 0.545, 0.07, 0.26, "ceramic_white", "Decor", 32, r2=0.09)
for i, (mt, hh) in enumerate([("book_a", 0.05), ("book_b", 0.04), ("book_c", 0.035)]):
    boxc(f"Console_book{i}", lx0 + 0.3, Y(300) - 0.85, 0.545 + i * 0.045, 0.24, 0.32, 0.04, mt, "Decor", rot=4 * i)
sphere("Console_orb", lx0 + 0.3, Y(300) - 0.85, 0.72, 0.06, "brass")
# emerald velvet sofa against the toilet-2 wall, facing the TV
asset("Sofa", "GlamVelvetSofa.glb", lx1 - 0.57, Y(318), 0, rot=-90, recolor={"fabric": ((0.008, 0.075, 0.048), 0.85)}, collide=True)
cushion("Sofa_c1", lx1 - 0.55, Y(318) + 0.62, 0.44, 0.16, 0.46, 0.44, "boucle", rot=(0, 12, -90))
cushion("Sofa_c2", lx1 - 0.55, Y(318) - 0.62, 0.44, 0.16, 0.46, 0.44, "velvet_gold", rot=(0, 12, -90))
cushion("Sofa_c3", lx1 - 0.5, Y(318) - 0.2, 0.46, 0.14, 0.38, 0.32, "velvet_cognac", rot=(0, 10, -80))
panel_art("Art_living", lx1 - 0.002, Y(318), 1.78, 1.8, 1.08, "art_living", "W")
# two ivory boucle lounge chairs facing south, side by side at the balcony end
asset("Lounge_A", "SheenChair.glb", X(730), Y(232), 0, rot=0, recolor={"fabric": ((0.80, 0.76, 0.69), 0.95)}, collide=True)
asset("Lounge_B", "SheenChair.glb", X(822), Y(232), 0, rot=0, recolor={"fabric": ((0.80, 0.76, 0.69), 0.95)}, collide=True)
cyl("Lounge_table", X(776), Y(222), 0, 0.22, 0.52, "travertine", "Furniture", 40, collide=True)
asset("Lounge_vase", "GlassVaseFlowers.glb", X(776), Y(222), 0.52, scale=1.3)
# rug + nesting marble coffee tables
box("Rug_living", X(700), Y(410), 0.0, X(870), Y(255), 0.012, "rug", "Furniture", bevel=0.004)
cyl("Coffee_top", X(770), Y(330), 0.36, 0.48, 0.035, "marble_counter", "Furniture", 64)
cyl("Coffee_base", X(770), Y(330), 0.0, 0.34, 0.36, "brass_brushed", "Furniture", 64, r2=0.28)
COLLIDERS.append([X(770) - 0.48, Y(330) - 0.48, X(770) + 0.48, Y(330) + 0.48])
cyl("Coffee2_top", X(812), Y(372), 0.26, 0.3, 0.03, "travertine", "Furniture", 48)
cyl("Coffee2_base", X(812), Y(372), 0.0, 0.2, 0.26, "black_metal", "Furniture", 48)
asset("Coffee_candle", "GlassHurricaneCandleHolder.glb", X(770) + 0.12, Y(330) + 0.1, 0.395, scale=1.0)
for i, (mt, rr) in enumerate([("book_b", 0), ("book_a", 8)]):
    boxc(f"Coffee_book{i}", X(770) - 0.18, Y(330) - 0.12, 0.395 + i * 0.04, 0.3, 0.24, 0.035, mt, "Decor", rot=rr)
sphere("Coffee_bowl", X(770) - 0.18, Y(330) - 0.12, 0.49, 0.09, "ceramic_black", sz=0.45)
# arc floor lamp at the south end of the sofa
ax, ay = X(895), Y(445)
cyl("ArcLamp_base", ax, ay, 0, 0.17, 0.04, "marble_nero", "Furniture", 40)
cyl("ArcLamp_stem", ax, ay, 0.04, 0.012, 1.6, "brass", "Furniture", 12)
arc_pts = [(ax - 0.45 + 0.45 * math.cos(math.radians(t)), ay, 1.64 + 0.55 * math.sin(math.radians(t))) for t in range(0, 181, 6)]
tube("ArcLamp_arc", arc_pts, 0.012, "brass")
cyl("ArcLamp_drop", ax - 0.9, ay, 1.52, 0.006, 0.12, "brass", "Furniture", 8)
sphere("ArcLamp_shade", ax - 0.9, ay, 1.52, 0.2, "brass", sz=0.55)
sphere("ArcLamp_bulb", ax - 0.9, ay, 1.46, 0.07, "opal")
COLLIDERS.append([ax - 0.18, ay - 0.18, ax + 0.18, ay + 0.18])
asset("Plant_living", "DiffuseTransmissionPlant.glb", X(668), Y(200), 0, rot=30, scale=1.9, recolor={"base": ((0.22, 0.21, 0.20), 0.8)}, collide=True)
# ring chandelier over the seating
for i, (R, z) in enumerate([(0.55, 2.42), (0.42, 2.30), (0.30, 2.18)]):
    torus(f"Ring{i}", X(776), Y(325), z, R, 0.018, "brass", "Decor")
    torus(f"RingLED{i}", X(776), Y(325), z - 0.012, R, 0.008, "led", "Decor")
for k in range(3):
    a = k * 2 * math.pi / 3
    cyl(f"RingWire{k}", X(776) + 0.55 * math.cos(a), Y(325) + 0.55 * math.sin(a), 2.42, 0.002, H - 2.42 - 0.2, "black_metal", "Decor", 6)
# curtains: sheer ripple-fold across the glazing, linen drapes stacked at the ends
curtain("Sheer_L", X(694), Y(176), X(868), Y(176), 0.02, 2.62, "sheer", 9, 0.035)
curtain("Drape_L1", X(680), Y(180), X(712), Y(180), 0.02, 2.62, "drape_sand", 10, 0.05)
curtain("Drape_L2", X(852), Y(180), X(884), Y(180), 0.02, 2.62, "drape_sand", 10, 0.05)
for (px, py) in [(700, 230), (850, 230), (700, 410), (850, 410), (776, 200), (776, 440)]:
    spot(px, py)

# ============================================================== DINING & FAMILY
tx, ty = X(600), Y(650)
box("Dine_top", tx - 1.1, ty - 0.5, 0.735, tx + 1.1, ty + 0.5, 0.775, "marble_counter", "Furniture", True, bevel=0.035, seg=6)
for s_ in (-1, 1):
    cyl(f"Dine_ped{s_}", tx + s_ * 0.6, ty, 0.0, 0.2, 0.735, "fluted_walnut", "Furniture", 48, r2=0.14, sy=0.55)
    cyl(f"Dine_pedcap{s_}", tx + s_ * 0.6, ty, 0.0, 0.24, 0.02, "brass", "Furniture", 48, sy=0.55)
def dining_chair(n, cx, cy, face):   # face: +1 chair faces +Y (north), -1 faces south
    fdeg = 90 if face > 0 else -90
    cushion(n + "_seat", cx, cy, 0.43, 0.5, 0.48, 0.09, "leather_cognac")
    shell_back(n + "_back", cx, cy + face * 0.02, 0.56, 0.92, 0.25, 150, 0.05, fdeg, "leather_cognac")
    boxc(n + "_apron", cx, cy, 0.38, 0.44, 0.42, 0.05, "black_metal")
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            tube(f"{n}_leg{sx_}{sy_}", [(cx + sx_ * 0.17, cy + sy_ * 0.17, 0.4), (cx + sx_ * 0.22, cy + sy_ * 0.22, 0.0)], 0.012, "brass")
for i in range(3):
    dining_chair(f"DChairN{i}", tx + (i - 1) * 0.68, ty + 0.72, -1)
    dining_chair(f"DChairS{i}", tx + (i - 1) * 0.68, ty - 0.72, 1)
COLLIDERS.append([tx - 1.2, ty - 1.0, tx + 1.2, ty + 1.0])
# linear chandelier: brass bar + opal globes
box("Chand_bar", tx - 0.8, ty - 0.015, 2.05, tx + 0.8, ty + 0.015, 2.08, "brass", "Decor")
for s_ in (-0.7, 0.7):
    cyl(f"Chand_rod{s_}", tx + s_, ty, 2.08, 0.004, H - 2.08, "brass", "Decor", 8)
for i in range(6):
    sphere(f"Chand_globe{i}", tx - 0.65 + i * 0.26, ty, 1.97, 0.075, "opal")
asset("Dine_dish", "IridescentDishWithOlives.glb", tx, ty, 0.775, scale=0.9)
# client's round mirror cluster, upgraded with brass rims, on the south wall
wy = Y(745) + 0.03
for nm, (px, z, r) in {"big": (560, 1.62, 0.42), "s": (632, 2.0, 0.2), "m": (640, 1.38, 0.26)}.items():
    cyl(f"Mir_{nm}_rim", X(px), wy, z, r + 0.03, 0.03, "brass", "Decor", 64, rot=(90, 0, 0))
    cyl(f"Mir_{nm}", X(px), wy + 0.004, z, r, 0.03, "mirror", "Decor", 64, rot=(90, 0, 0))
# bar / crockery unit on the west wall: walnut carcass, bronze-glass doors, lit marble niche
cx0 = X(450) + 0.005
box("Bar_carcass", cx0, Y(742), 0, cx0 + 0.5, Y(562), 2.55, "walnut", "Furniture", True)
box("Bar_niche_back", cx0 + 0.495, Y(712), 0.9, cx0 + 0.5, Y(592), 2.2, "smoked_mirror", "Furniture")
box("Bar_niche_cut", cx0 + 0.5, Y(712), 0.9, cx0 + 0.501, Y(592), 2.2, "smoked_mirror", "Furniture")
box("Bar_counter", cx0 + 0.02, Y(714), 0.88, cx0 + 0.56, Y(590), 0.92, "marble_nero", "Furniture", bevel=0.005)
for z in (1.35, 1.8):
    box(f"Bar_shelf{z}", cx0 + 0.25, Y(712), z, cx0 + 0.5, Y(592), z + 0.012, "glass", "Furniture")
    box(f"Bar_shelfLED{z}", cx0 + 0.25, Y(712), z - 0.006, cx0 + 0.27, Y(592), z, "led_soft", "Furniture")
for nm, (a, b) in {"L": (742, 714), "R": (590, 562)}.items():
    box(f"Bar_door{nm}", cx0 + 0.5, Y(a), 0.06, cx0 + 0.515, Y(b), 2.5, "glass_fluted", "Furniture")
    box(f"Bar_doorfr{nm}", cx0 + 0.5, Y(a), 0.04, cx0 + 0.52, Y(a) + 0.02, 2.52, "brass", "Furniture")
for i in range(6):
    cyl(f"Bar_glass{i}", cx0 + 0.35, Y(705) + i * 0.27, 1.362, 0.035, 0.18, "glass", "Decor", 20, r2=0.04)
    cyl(f"Bar_bottle{i}", cx0 + 0.38, Y(700) + i * 0.27, 1.812, 0.04, 0.3, "glass_bronze", "Decor", 20, r2=0.035)
curtain("Drape_D1", X(704), Y(740), X(734), Y(740), 0.02, 2.55, "drape_sand", 10, 0.05)
curtain("Drape_D2", X(823), Y(740), X(853), Y(740), 0.02, 2.55, "drape_sand", 10, 0.05)
curtain("Sheer_D", X(712), Y(738), X(845), Y(738), 0.02, 2.55, "sheer", 9, 0.03)
# family corner: large planter + a sculptural console with art
asset("Plant_family", "DiffuseTransmissionPlant.glb", X(880), Y(712), 0, rot=-20, scale=1.7, recolor={"base": ((0.75, 0.71, 0.65), 0.7)}, collide=True)
for (px, py) in [(520, 600), (680, 600), (520, 700), (680, 700), (800, 600), (800, 700)]:
    spot(px, py)

# ============================================================== FOYER & ENTRANCE
fy = Y(562)
box("Foyer_flutes", X(955), fy, 0, X(1125), fy + 0.04, H - 0.03, "fluted_walnut", "Decor")
box("Foyer_console", X(985), fy + 0.04, 0.82, X(1095), fy + 0.42, 0.87, "marble_nero", "Furniture", True, bevel=0.005)
box("Foyer_consoleB", X(985), fy + 0.04, 0.74, X(1095), fy + 0.40, 0.82, "walnut_dark", "Furniture")
box("Foyer_glow", X(990), fy + 0.06, 0.735, X(1090), fy + 0.38, 0.74, "led_soft", "Furniture")
cyl("Foyer_mirror_rim", X(1040), fy + 0.05, 1.62, 0.42, 0.025, "brass", "Decor", 64, rot=(90, 0, 0))
cyl("Foyer_mirror", X(1040), fy + 0.055, 1.62, 0.39, 0.025, "mirror", "Decor", 64, rot=(90, 0, 0))
cyl("Foyer_vase", X(1072), fy + 0.25, 0.87, 0.07, 0.36, "ceramic_black", "Decor", 32, r2=0.04)
asset("Foyer_flowers", "GlassVaseFlowers.glb", X(1005), fy + 0.25, 0.87, scale=1.2)
for s_ in (-1, 1):
    sx_ = X(1040) + s_ * 0.75
    box(f"Sconce{s_}", sx_ - 0.04, fy + 0.04, 1.5, sx_ + 0.04, fy + 0.12, 1.9, "brass", "Decor", bevel=0.01)
    box(f"SconceL{s_}", sx_ - 0.03, fy + 0.12, 1.52, sx_ + 0.03, fy + 0.125, 1.88, "opal", "Decor")
panel_art("Art_foyer", X(1000), Y(462) - 0.002, 1.55, 0.7, 0.98, "art_foyer", "S")
box("Vest_sign", X(1190), Y(462) - 0.05, 1.25, X(1235), Y(462) - 0.012, 1.85, "walnut_dark", "Decor")
box("Vest_glow", X(1188), Y(462) - 0.012, 1.23, X(1237), Y(462) - 0.008, 1.87, "led_soft", "Decor")
box("Vest_brass", X(1195), Y(462) - 0.052, 1.32, X(1230), Y(462) - 0.05, 1.36, "brass", "Decor")
asset("Plant_vest", "DiffuseTransmissionPlant.glb", X(1175), Y(560), 0, scale=1.4, recolor={"base": ((0.75, 0.71, 0.65), 0.7)}, collide=True)
for (px, py) in [(1000, 515), (1090, 515), (1250, 522), (1350, 522)]:
    spot(px, py, H - 0.04)

# ============================================================== KITCHEN
kx0, kx1, ky_n, ky_s = X(935), X(1137), Y(568), Y(745)
d = 0.62
box("K_lowN", kx0 + 0.62, ky_n - d, 0.1, kx1, ky_n, 0.87, "lacquer_taupe", "Furniture", True)
box("K_lowE", kx1 - d, ky_s + 0.02, 0.1, kx1, ky_n - d, 0.87, "lacquer_taupe", "Furniture", True)
box("K_plinthN", kx0 + 0.62, ky_n - d + 0.06, 0, kx1, ky_n, 0.1, "lacquer_black", "Furniture")
box("K_plinthE", kx1 - d + 0.06, ky_s + 0.02, 0, kx1, ky_n - d, 0.1, "lacquer_black", "Furniture")
for i in range(5):                                   # shadow-gap groove lines between fronts
    xx = kx0 + 0.62 + i * (kx1 - kx0 - 0.62) / 4
    box(f"K_gapN{i}", xx - 0.002, ky_n - d - 0.002, 0.1, xx + 0.002, ky_n - d, 0.87, "lacquer_black", "Furniture")
box("K_grooveN", kx0 + 0.62, ky_n - d - 0.003, 0.80, kx1, ky_n - d, 0.83, "brass_brushed", "Furniture")
box("K_grooveE", kx1 - d - 0.003, ky_s + 0.02, 0.80, kx1 - d, ky_n - d, 0.83, "brass_brushed", "Furniture")
box("K_topN", kx0 + 0.62, ky_n - d - 0.02, 0.87, kx1, ky_n, 0.91, "marble_counter", "Furniture", bevel=0.004)
box("K_topE", kx1 - d - 0.02, ky_s + 0.02, 0.87, kx1, ky_n - d - 0.02, 0.91, "marble_counter", "Furniture", bevel=0.004)
box("K_waterfall", kx0 + 0.6, ky_n - d - 0.02, 0.0, kx0 + 0.64, ky_n, 0.91, "marble_counter", "Furniture")
box("K_splashN", kx0 + 0.62, ky_n - 0.015, 0.91, kx1, ky_n, H - 0.02, "marble_slab", "Decor")
box("K_splashE", kx1 - 0.015, ky_s + 0.02, 0.91, kx1, ky_n, H - 0.02, "marble_slab", "Decor")
# fluted bronze-glass wall cabinets: walnut carcass, lit shelves with crockery, brass-framed fronts
box("K_upcarcass", kx0 + 0.62, ky_n - 0.36, 1.55, kx0 + 0.62 + 4 * 0.46, ky_n - 0.015, 2.35, "walnut", "Furniture")
for z in (1.82, 2.08):
    box(f"K_upshelf{z}", kx0 + 0.64, ky_n - 0.35, z, kx0 + 0.6 + 4 * 0.46, ky_n - 0.03, z + 0.012, "glass", "Furniture")
for i in range(8):
    cyl(f"K_plate{i}", kx0 + 0.75 + i * 0.22, ky_n - 0.2, 1.57, 0.1, 0.03, "ceramic_white", "Decor", 24)
    cyl(f"K_cup{i}", kx0 + 0.75 + i * 0.22, ky_n - 0.2, 1.832, 0.04, 0.09, "ceramic_black" if i % 2 else "ceramic_white", "Decor", 16)
for i in range(4):
    x0_ = kx0 + 0.64 + i * 0.46
    box(f"K_up{i}", x0_, ky_n - 0.375, 1.56, x0_ + 0.44, ky_n - 0.362, 2.34, "glass_fluted", "Furniture")
    for (a_, b_) in [(x0_, x0_ + 0.02), (x0_ + 0.42, x0_ + 0.44)]:
        box(f"K_upfr{i}{a_:.2f}", a_, ky_n - 0.38, 1.55, b_, ky_n - 0.36, 2.35, "brass", "Furniture")
    box(f"K_upglow{i}", x0_ + 0.02, ky_n - 0.06, 1.58, x0_ + 0.42, ky_n - 0.05, 2.32, "led_soft", "Furniture")
box("K_uptop", kx0 + 0.62, ky_n - 0.38, 2.35, kx0 + 0.62 + 4 * 0.46, ky_n - 0.015, 2.38, "walnut", "Furniture")
box("K_under", kx0 + 0.64, ky_n - 0.36, 1.54, kx0 + 0.62 + 4 * 0.46, ky_n - 0.34, 1.55, "led", "Furniture")
box("K_sink", kx0 + 1.0, ky_n - 0.5, 0.893, kx0 + 1.6, ky_n - 0.13, 0.912, "black_metal", "Furniture")
cyl("K_tap", kx0 + 1.3, ky_n - 0.07, 0.91, 0.013, 0.36, "brass", "Furniture", 16)
torus("K_tapneck", kx0 + 1.3, ky_n - 0.15, 1.27, 0.08, 0.012, "brass", "Furniture", rot=(90, 0, 90))
box("K_hob", kx1 - 0.55, Y(700), 0.905, kx1 - 0.06, Y(662), 0.913, "screen", "Furniture")
box("K_hood", kx1 - 0.5, Y(702), 1.75, kx1 - 0.015, Y(660), 1.82, "black_metal", "Furniture")
box("K_hoodglass", kx1 - 0.5, Y(702), 1.82, kx1 - 0.48, Y(660), 2.2, "smoked_mirror", "Furniture")
box("K_tower", kx0 + 0.005, ky_s + 0.02, 0, kx0 + 0.62, ky_s + 0.66, H - 0.03, "walnut", "Furniture", True)
box("K_oven", kx0 + 0.62, ky_s + 0.08, 0.95, kx0 + 0.625, ky_s + 0.6, 1.55, "screen", "Furniture")
box("K_micro", kx0 + 0.62, ky_s + 0.08, 1.6, kx0 + 0.625, ky_s + 0.6, 1.98, "screen", "Furniture")
box("K_ovenbar", kx0 + 0.625, ky_s + 0.12, 1.47, kx0 + 0.64, ky_s + 0.56, 1.49, "brass", "Furniture")
asset("K_teacup", "DiffuseTransmissionTeacup.glb", kx1 - 0.35, Y(610), 0.91, scale=1.0)
for i in range(3):
    cyl(f"K_jar{i}", kx0 + 1.9 + i * 0.13, ky_n - 0.18, 0.91, 0.05, 0.16 + i * 0.04, "glass", "Decor", 20)
for (px, py) in [(1000, 620), (1080, 620), (1000, 700), (1080, 700)]:
    spot(px, py, H - 0.04)
box("U_washer", X(1080), Y(842) + 0.02, 0, X(1132), Y(800), 0.85, "lacquer_ivory", "Furniture", True)
box("U_counter", X(1080), Y(800), 0.85, X(1132), Y(760), 0.89, "marble_counter", "Furniture", True)

# ============================================================== BEDROOM BUILDER
def bed(n, hx, cy, head_dir, width, length, base_mat, duvet_mat, throw_mat, pillow_mats, headboard):
    """hx = headboard wall coordinate (m, along x); head_dir = +1 if headboard on the +x wall."""
    sgn = head_dir
    cx = hx - sgn * (length / 2 + 0.08)
    boxc(n + "_plinth", cx, cy, 0.0, length - 0.15, width - 0.15, 0.1, "lacquer_black", collide=False)
    boxc(n + "_base", cx, cy, 0.1, length + 0.04, width + 0.08, 0.26, base_mat, collide=True, bevel=0.05, seg=4)
    boxc(n + "_mattress", cx, cy, 0.36, length - 0.02, width, 0.24, "linen_white", bevel=0.06, seg=4)
    dv_len = length * 0.72
    dcx = cx - sgn * (length - dv_len) / 2
    boxc(n + "_duvet", dcx, cy, 0.30, dv_len, width + 0.16, 0.34, duvet_mat, bevel=0.08, seg=5)
    boxc(n + "_throw", cx - sgn * (length / 2 - 0.35), cy, 0.62, 0.55, width + 0.2, 0.05, throw_mat, bevel=0.025, seg=4)
    px_ = hx - sgn * 0.22
    for i, s_ in enumerate((-1, 1)):
        cushion(f"{n}_euro{i}", px_, cy + s_ * width / 4, 0.58, 0.18, width / 2 - 0.06, 0.62, pillow_mats[0], rot=(0, -sgn * 14, 0))
        cushion(f"{n}_std{i}", px_ - sgn * 0.14, cy + s_ * width / 4.4, 0.6, 0.16, 0.66, 0.42, pillow_mats[1], rot=(0, -sgn * 20, 0))
    cushion(f"{n}_lumbar", px_ - sgn * 0.28, cy, 0.6, 0.14, 0.55, 0.3, pillow_mats[2], rot=(0, -sgn * 24, 0))
    return cx

def channel_headboard(n, hx, cy, width, z0, z1, material, sgn, channels=14):
    w = width / channels
    for i in range(channels):
        yy = cy - width / 2 + (i + 0.5) * w
        o = cyl(f"{n}_ch{i}", hx - sgn * 0.04, yy, z0, w * 0.5, z1 - z0, material, "Furniture", 16, sx=0.6, sy=1.0)
    box(n + "_chback", hx - sgn * 0.04, cy - width / 2, z0, hx, cy + width / 2, z1, material, "Furniture")

def nightstand(n, x, y, sgn, pendant=True):
    boxc(n, x, y, 0.42, 0.5, 0.42, 0.14, "walnut", rot=0, bevel=0.01)
    boxc(n + "_brass", x, y, 0.40, 0.48, 0.40, 0.02, "brass", rot=0)
    asset(n + "_vase", "GlassVaseFlowers.glb", x, y + 0.08, 0.56, scale=0.9)
    if pendant:
        cyl(n + "_wire", x, y - 0.06, 1.25, 0.002, H - 1.25 - 0.2, "black_metal", "Decor", 6)
        sphere(n + "_globe", x, y - 0.06, 1.15, 0.11, "opal")
        cyl(n + "_cap", x, y - 0.06, 1.24, 0.04, 0.05, "brass", "Decor", 20)

def wardrobe(n, x0, y0, x1, y1, front_axis, front_sign, style):
    """front_axis 'y' => doors face +/-Y at y0/y1; style: 'bronze', 'oak', 'ivory'."""
    body = {"bronze": "walnut_dark", "oak": "oak", "ivory": "lacquer_ivory"}[style]
    box(n, x0, y0, 0, x1, y1, H - 0.21, body, "Furniture", True)
    if style == "bronze":
        fy0 = y1 if front_sign > 0 else y0
        nd = max(2, round((x1 - x0) / 0.6))
        for i in range(nd):
            a = x0 + i * (x1 - x0) / nd; b = a + (x1 - x0) / nd
            box(f"{n}_g{i}", a + 0.02, fy0, 0.08, b - 0.02, fy0 + front_sign * 0.012, H - 0.29, "glass_bronze", "Furniture")
            box(f"{n}_f{i}", a, fy0 + front_sign * 0.012, 0.06, a + 0.02, fy0 + front_sign * 0.02, H - 0.27, "black_metal", "Furniture")
            box(f"{n}_led{i}", a + 0.03, fy0 - front_sign * 0.04, 0.1, b - 0.03, fy0 - front_sign * 0.03, H - 0.3, "led_soft", "Furniture")
    else:
        fy0 = y1 if front_sign > 0 else y0
        nd = max(2, round((x1 - x0) / 0.55))
        for i in range(nd):
            a = x0 + i * (x1 - x0) / nd
            box(f"{n}_gap{i}", a - 0.002, fy0, 0.05, a + 0.002, fy0 + front_sign * 0.003, H - 0.25, "lacquer_black", "Furniture")
            hxp = a + ((x1 - x0) / nd) * (0.9 if i % 2 == 0 else 0.1)
            box(f"{n}_h{i}", hxp - 0.008, fy0 + front_sign * 0.003, 0.7, hxp + 0.008, fy0 + front_sign * 0.03, 1.7, "brass", "Furniture")

# ---------------------------------------------------------------- BEDROOM 2 (NE): oak + grey chevron, from the video
bx0, bx1, by_n, by_s = X(1057), X(1313), Y(172), Y(452)
bcy = Y(305)
box("BR2_oakwall", bx1 - 0.03, Y(445), 0, bx1, Y(180), 1.3, "oak", "Decor")
box("BR2_paper", bx1 - 0.012, Y(450), 1.3, bx1 - 0.002, Y(175), H - 0.21, "plaster", "Decor")
box("BR2_oakLED", bx1 - 0.04, Y(445), 1.3, bx1 - 0.03, Y(180), 1.31, "led_soft", "Decor")
boxc("BR2_headboard", bx1 - 0.08, bcy, 0.4, 0.08, 2.0, 0.85, "chevron", bevel=0.02, seg=3)
bed("BR2_bed", bx1 - 0.12, bcy, 1, 1.85, 2.05, "fabric_grey", "linen_white", "velvet_taupe", ["fabric_grey", "linen_white", "velvet_gold"], None)
nightstand("BR2_ns1", bx1 - 0.3, bcy + 1.28, 1); nightstand("BR2_ns2", bx1 - 0.3, bcy - 1.28, 1)
panel_art("BR2_art", bx1 - 0.015, bcy, 1.92, 1.5, 0.75, "art_sticks", "W", frame="black_metal")
wardrobe("BR2_ward", X(1125), by_s, bx1, by_s + 0.62, "y", 1, "oak")
box("BR2_desk", bx0 + 0.005, Y(285), 0.74, bx0 + 0.5, Y(190), 0.78, "oak", "Furniture", True)
box("BR2_deskleg", bx0 + 0.45, Y(283), 0, bx0 + 0.48, Y(280), 0.74, "brass", "Furniture")
asset("BR2_chair", "SheenChair.glb", bx0 + 0.65, Y(238), 0, rot=90, scale=0.9, recolor={"fabric": ((0.33, 0.33, 0.34), 0.9)})
box("BR2_rug", X(1130), Y(420), 0, X(1290), Y(200), 0.012, "rug", "Furniture", bevel=0.004)
curtain("BR2_sheer", X(1119), Y(176), X(1251), Y(176), 0.02, 2.62, "sheer", 9, 0.03)
curtain("BR2_d1", X(1105), Y(180), X(1132), Y(180), 0.02, 2.62, "drape_charcoal", 10, 0.05)
curtain("BR2_d2", X(1238), Y(180), X(1266), Y(180), 0.02, 2.62, "drape_charcoal", 10, 0.05)
for (px, py) in [(1110, 230), (1110, 400), (1260, 230), (1260, 400)]:
    spot(px, py)

# ---------------------------------------------------------------- BEDROOM 3: charcoal channel headboard wall, cream panel, art
cx0_, cx1_, cy_n, cy_s = X(378), X(635), Y(172), Y(462)
c3 = Y(305)
box("BR3_dark", cx0_, Y(455), 0, cx0_ + 0.012, Y(178), H - 0.21, "fabric_charcoal", "Decor")
channel_headboard("BR3_hb", cx0_ + 0.06, c3, 2.4, 0.45, 1.45, "fabric_charcoal", -1, 16)
box("BR3_cream", cx0_ + 0.012, c3 - 1.2, 1.45, cx0_ + 0.05, c3 + 1.2, 2.55, "lacquer_ivory", "Decor")
box("BR3_creamLED", cx0_ + 0.05, c3 - 1.2, 1.45, cx0_ + 0.055, c3 + 1.2, 1.46, "led_soft", "Decor")
panel_art("BR3_art", cx0_ + 0.05, c3, 2.0, 1.25, 0.78, "art_br3", "E", frame="brass")
bed("BR3_bed", cx0_ + 0.1, c3, -1, 1.65, 2.05, "fabric_charcoal", "linen_white", "linen_sand", ["linen_sand", "linen_white", "velvet_emerald"], None)
nightstand("BR3_ns1", cx0_ + 0.3, c3 + 1.18, -1); nightstand("BR3_ns2", cx0_ + 0.3, c3 - 1.18, -1)
boxc("BR3_bench", cx0_ + 2.45, c3, 0.0, 0.45, 1.3, 0.45, "boucle", collide=True, bevel=0.06, seg=4)
wardrobe("BR3_ward", cx0_, cy_s, X(565), cy_s + 0.62, "y", 1, "ivory")
box("BR3_desk", cx1_ - 0.5, Y(300), 0.74, cx1_, Y(190), 0.78, "walnut", "Furniture", True)
box("BR3_shelf", cx1_ - 0.28, Y(300), 1.55, cx1_, Y(190), 1.58, "walnut", "Furniture")
box("BR3_rug", X(410), Y(420), 0, X(600), Y(190), 0.012, "rug", "Furniture", bevel=0.004)
curtain("BR3_sheer", X(452), Y(176), X(570), Y(176), 0.02, 2.62, "sheer", 9, 0.03)
curtain("BR3_d1", X(440), Y(180), X(466), Y(180), 0.02, 2.62, "drape_sand", 10, 0.05)
curtain("BR3_d2", X(556), Y(180), X(582), Y(180), 0.02, 2.62, "drape_sand", 10, 0.05)
for (px, py) in [(430, 230), (430, 400), (585, 230), (585, 400)]:
    spot(px, py)

# ---------------------------------------------------------------- MASTER: herringbone, beige channel wall, client's orange prints, bronze-glass wardrobe
mx0, mx1, my_n, my_s = X(55), X(365), Y(297), Y(597)
mb = Y(428)
box("MB_panel", mx0, my_s + 0.62, 0, mx0 + 0.03, my_n - 0.02, H - 0.21, "fabric_greige", "Decor")
channel_headboard("MB_hb", mx0 + 0.07, mb, 2.6, 0.4, 1.35, "velvet_taupe", -1, 18)
for s_ in (-1, 1):
    box(f"MB_side{s_}", mx0 + 0.03, mb + s_ * 1.3 - 0.3 * (1 if s_ < 0 else 0), 0, mx0 + 0.06, mb + s_ * 1.3 + 0.3 * (1 if s_ > 0 else 0), H - 0.21, "walnut", "Decor")
panel_art("MB_art_l", mx0 + 0.035, mb + 0.34, 1.9, 0.52, 0.86, "art_orange_l", "E", frame="brass")
panel_art("MB_art_r", mx0 + 0.035, mb - 0.34, 1.9, 0.48, 0.86, "art_orange_r", "E", frame="brass")
bed("MB_bed", mx0 + 0.1, mb, -1, 1.95, 2.1, "velvet_taupe", "linen_white", "fabric_charcoal", ["linen_sand", "linen_white", "velvet_cognac"], None)
nightstand("MB_ns1", mx0 + 0.3, mb + 1.32, -1); nightstand("MB_ns2", mx0 + 0.3, mb - 1.32, -1)
boxc("MB_bench", mx0 + 2.5, mb, 0.0, 0.48, 1.5, 0.46, "velvet_cognac", collide=True, bevel=0.06, seg=4)
for s_ in (-1, 1):
    for t_ in (-1, 1):
        cyl(f"MB_benchleg{s_}{t_}", mx0 + 2.5 + s_ * 0.18, mb + t_ * 0.68, 0, 0.015, 0.06, "brass", "Furniture", 10)
wardrobe("MB_ward", mx0, my_s, X(313), my_s + 0.62, "y", 1, "bronze")
asset("MB_lounge", "SheenChair.glb", X(150), Y(325), 0, rot=200, recolor={"fabric": ((0.40, 0.19, 0.08), 0.6)}, collide=True)
asset("MB_pouf", "SpecularSilkPouf.glb", X(205), Y(345), 0, scale=0.75)
box("MB_vanity", mx1 - 0.5, Y(420), 0.74, mx1, Y(318), 0.78, "walnut", "Furniture", True)
cyl("MB_vmirror_rim", mx1 - 0.01, Y(369), 1.5, 0.36, 0.02, "brass", "Decor", 64, rot=(0, 90, 0))
cyl("MB_vmirror", mx1 - 0.015, Y(369), 1.5, 0.33, 0.02, "mirror", "Decor", 64, rot=(0, 90, 0))
box("MB_rug", X(150), Y(530), 0.006, X(345), Y(330), 0.018, "rug", "Furniture", bevel=0.004)
curtain("MB_sheerW", mx0 + 0.03, Y(368), mx0 + 0.03, Y(290), 0.6, 2.6, "sheer", 9, 0.03)
curtain("MB_sheerN", X(70), Y(292), X(180), Y(292), 0.02, 2.62, "sheer", 9, 0.03)
curtain("MB_drape", X(170), Y(294), X(200), Y(294), 0.02, 2.62, "drape_sand", 10, 0.05)
for (px, py) in [(110, 350), (110, 520), (300, 350), (300, 520), (210, 560)]:
    spot(px, py)

# ============================================================== BATHROOMS
def bathroom(n, px0, py0, px1, py1, wc_side, van_side, accent="marble_nero"):
    x0, x1, y_n, y_s = X(px0), X(px1), Y(py0), Y(py1)
    t = 0.01
    box(n + "_wN", x0, y_n - t, 0, x1, y_n, H - 0.02, accent, "Decor")
    box(n + "_wS", x0, y_s, 0, x1, y_s + t, H - 0.02, "stone_light", "Decor")
    box(n + "_wW", x0, y_s, 0, x0 + t, y_n, H - 0.02, "stone_light", "Decor")
    box(n + "_wE", x1 - t, y_s, 0, x1, y_n, H - 0.02, "stone_light", "Decor")
    if wc_side == "N": cx, cy, r = (x0 + x1) / 2 - 0.3, y_n - 0.32, 90
    elif wc_side == "W": cx, cy, r = x0 + 0.33, (y_n + y_s) / 2 + 0.3, 0
    else: cx, cy, r = x1 - 0.33, (y_n + y_s) / 2 + 0.2, 0
    boxc(n + "_wc", cx, cy, 0.24, 0.55, 0.37, 0.18, "porcelain", rot=r, bevel=0.08, seg=5)
    boxc(n + "_wcseat", cx, cy, 0.42, 0.5, 0.36, 0.02, "porcelain", rot=r, bevel=0.01)
    if van_side == "S": vx, vy, vr = (x0 + x1) / 2 + 0.25, y_s + 0.26, 0
    elif van_side == "W": vx, vy, vr = x0 + 0.26, y_n - 0.5, 90
    else: vx, vy, vr = x1 - 0.26, y_s + 0.5, 90
    boxc(n + "_vanity", vx, vy, 0.42, 0.9, 0.5, 0.42, "walnut", rot=vr, collide=True, bevel=0.01)
    boxc(n + "_vtop", vx, vy, 0.84, 0.92, 0.52, 0.03, "marble_counter", rot=vr, bevel=0.004)
    sphere(n + "_basin", vx, vy, 0.9, 0.22, "porcelain", sx=1.0, sy=0.75, sz=0.32)
    cyl(n + "_tap", vx + (0.0 if vr == 0 else 0.0), vy + (0.0), 0.87, 0.012, 0.32, "brass", "Decor", 12)
    ld = bpy.data.lights.new(n + "_fill", "POINT"); ld.energy = 45; ld.color = (1.0, 0.86, 0.7); ld.shadow_soft_size = 0.2
    lo_ = bpy.data.objects.new(n + "_fill", ld); lo_.location = ((x0 + x1) / 2, (y_n + y_s) / 2, H - 0.4); coll("Lights").objects.link(lo_)
    if van_side == "S":
        torus(n + "_mglow", vx, y_s + 0.014, 1.58, 0.31, 0.012, "led_soft", "Decor", rot=(90, 0, 0))
        cyl(n + "_mrim", vx, y_s + 0.012, 1.58, 0.33, 0.02, "brass", "Decor", 64, rot=(90, 0, 0))
        cyl(n + "_mir", vx, y_s + 0.016, 1.58, 0.31, 0.02, "mirror", "Decor", 64, rot=(90, 0, 0))
    elif van_side == "W":
        torus(n + "_mglow", x0 + 0.014, vy, 1.58, 0.31, 0.012, "led_soft", "Decor", rot=(0, 90, 0))
        cyl(n + "_mrim", x0 + 0.012, vy, 1.58, 0.33, 0.02, "brass", "Decor", 64, rot=(0, 90, 0))
        cyl(n + "_mir", x0 + 0.016, vy, 1.58, 0.31, 0.02, "mirror", "Decor", 64, rot=(0, 90, 0))
    else:
        cyl(n + "_mrim", x1 - 0.032, vy, 1.58, 0.33, 0.02, "brass", "Decor", 64, rot=(0, 90, 0))
        cyl(n + "_mir", x1 - 0.036, vy, 1.58, 0.31, 0.02, "mirror", "Decor", 64, rot=(0, 90, 0))
bathroom("T1", 192, 172, 365, 288, "N", "W")
bathroom("T2", 935, 172, 1047, 378, "W", "S")
bathroom("T3", 325, 564, 437, 745, "E", "S")
for n, (a, b, c_) in {"T3": (330, 437, 660), "T2": (940, 1047, 250)}.items():
    box(n + "_glass", X(a), Y(c_) - 0.005, 0, X(b), Y(c_) + 0.005, 2.1, "glass", "Decor")
    box(n + "_glassfr", X(a), Y(c_) - 0.01, 2.1, X(b), Y(c_) + 0.01, 2.13, "black_metal", "Decor")
cyl("T1_rain", X(220), Y(200), H - 0.25, 0.15, 0.01, "chrome", "Decor", 32)
for (px, py) in [(278, 230), (990, 300), (380, 690), (990, 210), (230, 230), (380, 610)]:
    spot(px, py, H - 0.04, 30)

# ============================================================== BALCONY (continuous)
asset("Bal_chairA", "SheenChair.glb", X(745), Y(105), -0.03, rot=180, recolor={"fabric": ((0.62, 0.58, 0.50), 0.9)}, collide=True)
asset("Bal_chairB", "SheenChair.glb", X(820), Y(105), -0.03, rot=180, recolor={"fabric": ((0.62, 0.58, 0.50), 0.9)}, collide=True)
cyl("Bal_table", X(782), Y(110), -0.03, 0.22, 0.5, "travertine", "Furniture", 40, collide=True)
asset("Bal_lantern", "GlassHurricaneCandleHolder.glb", X(782), Y(110), 0.47, scale=1.2)
for i, px in enumerate([150, 470, 640, 1000, 1150, 1290]):
    asset(f"Bal_plant{i}", "DiffuseTransmissionPlant.glb", X(px), Y(62), -0.03, rot=40 * i, scale=1.6, recolor={"base": ((0.22, 0.21, 0.20), 0.8)}, collide=True)
for i, px in enumerate([250, 600, 900, 1200]):
    cyl(f"Bal_downlight{i}", X(px), Y(100), H + 0.14, 0.04, 0.01, "led_soft", "Exterior", 16)

# ============================================================== EXTERIOR backdrop (the project's own landscape renders)
import bmesh
me = bpy.data.meshes.new("Backdrop"); bmb = bmesh.new()
R_, zb, zt, segs = 26.0, -3.15, 11.0, 120
cxB, cyB = X(700), Y(450)
ring_lo = [bmb.verts.new((cxB + R_ * math.cos(2 * math.pi * i / segs), cyB + R_ * math.sin(2 * math.pi * i / segs), zb)) for i in range(segs)]
ring_hi = [bmb.verts.new((cxB + R_ * math.cos(2 * math.pi * i / segs), cyB + R_ * math.sin(2 * math.pi * i / segs), zt)) for i in range(segs)]
uvl = bmb.loops.layers.uv.new("UVMap")
for i in range(segs):
    j = (i + 1) % segs
    f = bmb.faces.new([ring_lo[j], ring_lo[i], ring_hi[i], ring_hi[j]])
    for l, uvv in zip(f.loops, [((i + 1) / segs * 1.5, 0), (i / segs * 1.5, 0), (i / segs * 1.5, 1), ((i + 1) / segs * 1.5, 1)]):
        l[uvl].uv = uvv
bmb.to_mesh(me); bmb.free()
ob = bpy.data.objects.new("Backdrop", me); ob.data.materials.append(MATS["backdrop"]); coll("Exterior").objects.link(ob)
mat("lawn", (0.10, 0.20, 0.07), rough=1.0)
box("Ground", cxB - 30, cyB - 30, -3.2, cxB + 30, cyB + 30, -3.1, "lawn", "Exterior")

# ============================================================== LIGHTS + WORLD + RENDER DEFAULTS
for i, (x, y, z, w) in enumerate(SPOTS):
    ld = bpy.data.lights.new(f"SpotL{i}", "SPOT"); ld.energy = w * 2.2; ld.color = (1.0, 0.84, 0.66)
    ld.spot_size = math.radians(70); ld.spot_blend = 0.7; ld.shadow_soft_size = 0.03
    o = bpy.data.objects.new(f"SpotL{i}", ld); o.location = (x, y, z - 0.02); coll("Lights").objects.link(o)
def pl(name, x, y, z, w, col=(1.0, 0.82, 0.62), r=0.05):
    ld = bpy.data.lights.new(name, "POINT"); ld.energy = w; ld.color = col; ld.shadow_soft_size = r
    o = bpy.data.objects.new(name, ld); o.location = (x, y, z); coll("Lights").objects.link(o)
pl("ChandD", tx, ty, 1.9, 60); pl("RingL", X(776), Y(325), 2.2, 50); pl("ArcL", ax - 0.9, ay, 1.38, 25)
for n_ in ["BR2_ns1", "BR2_ns2", "BR3_ns1", "BR3_ns2", "MB_ns1", "MB_ns2"]:
    g = bpy.data.objects.get(n_ + "_globe")
    if g: pl(n_ + "_L", g.location.x, g.location.y, g.location.z - 0.05, 18)
# daylight
world = bpy.data.worlds.new("Sky"); scene.world = world; world.use_nodes = True
nt = world.node_tree; bg = nt.nodes["Background"]
sky = nt.nodes.new("ShaderNodeTexSky")
try:
    sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(24); sky.sun_rotation = math.radians(205); sky.sun_disc = False
except Exception: pass
nt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.6
sd = bpy.data.lights.new("Sun", "SUN"); sd.energy = 3.0; sd.angle = math.radians(1.5); sd.color = (1.0, 0.9, 0.78)
so = bpy.data.objects.new("Sun", sd); coll("Lights").objects.link(so); so.rotation_euler = (math.radians(66), 0, math.radians(205))
# window portals to guide daylight sampling
def portal(name, x, y, z, sx, sy, rot):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    try: ld.cycles.is_portal = True
    except Exception: pass
    o = bpy.data.objects.new(name, ld); o.location = (x, y, z); o.rotation_euler = rot; coll("Lights").objects.link(o)
R = math.radians
for nm, (a, b) in {"P_liv": (692, 872), "P_br3": (450, 572), "P_br2": (1117, 1253)}.items():
    portal(nm, X((a + b) / 2), Y(166), 1.28, (b - a) / S, 2.5, (R(-90), 0, 0))
portal("P_din", X(778), Y(748), 1.5, 133 / S, 1.8, (R(90), 0, 0))
portal("P_mbal", X(125), Y(292), 1.28, 110 / S, 2.5, (R(-90), 0, 0))
portal("P_mw", X(50), Y(329), 1.5, 1.8, 78 / S, (0, R(90), 0))

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.03
scene.cycles.samples = 64
scene.cycles.use_denoising = True
try: scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 4; scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 8; scene.cycles.transparent_max_bounces = 16
scene.cycles.sample_clamp_indirect = 8.0
scene.cycles.blur_glossy = 1.0
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
scene.view_settings.exposure = 0.3

# ============================================================== METADATA for the web experience
meta = {"scale_px_per_m": S, "ceiling": H,
        "colliders": [[round(v, 3) for v in c] for c in lib_v2.COLLIDERS],
        "rooms": {
            "Living": [X(649), Y(462), X(922), Y(172)], "Family & Dining": [X(450), Y(745), X(922), Y(470)],
            "Foyer": [X(935), Y(562), X(1137), Y(462)], "Kitchen": [X(935), Y(745), X(1137), Y(568)],
            "Utility": [X(935), Y(842), X(1137), Y(752)], "Bedroom 2": [X(1057), Y(452), X(1313), Y(172)],
            "Bedroom 3": [X(378), Y(462), X(635), Y(172)], "Master Bedroom": [X(55), Y(597), X(365), Y(297)],
            "Master Bath": [X(192), Y(288), X(365), Y(172)], "Bath 2": [X(935), Y(378), X(1047), Y(172)],
            "Bath 3": [X(325), Y(745), X(437), Y(564)], "Entrance": [X(1150), Y(583), X(1410), Y(462)],
            "Balcony": [X(55), Y(160), X(1313), Y(40)], "Master Balcony": [X(55), Y(288), X(180), Y(160)]},
        "spots": [[round(s[0], 3), round(s[1], 3)] for s in SPOTS]}
with open(os.path.join(ROOT, "layout.json"), "w") as f:
    json.dump(meta, f)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "A105_lux.blend"))
print("BUILD V2 OK", len(bpy.data.objects), "objects", len(lib_v2.COLLIDERS), "colliders", len(SPOTS), "spots")
