"""
E-paper photo frame - full parametric model (all parts).

Hardware:
  - Waveshare 7.5" e-Paper raw panel V2 (800x480): 170.2 x 111.2 x 1.18 mm
  - Waveshare e-Paper ESP32 Driver Board: 29.46 x 48.25 mm, NO mounting holes
  - Waveshare FPC adapter board: 31.75 x 17.50 mm (plugs onto the panel's FPC tail,
    FFC extension cable to the ESP32 board)

Coordinates (all parts share them, so the assembly lines up):
  x right / y up  AS SEEN FROM THE BACK,  z = 0 front face, z grows toward the back.
  The panel's FPC tail is on the BOTTOM long edge.

Parts written to out/:
  frame       front bezel + side walls + corner bosses      (print front face down)
  backer      plate that presses the panel into the bezel   (print back face down)
  back_cover  cover + ESP32 cradle + keyholes + feet bosses (print outer face down)
  esp32_strap bar that clamps the ESP32 by its module can   (print flat)
  foot        removable desk foot, print 2                  (print on its side)

Hardware: M3 x 4 mm heat-set inserts (hole d4.0 x 4.8 deep - check your insert's
datasheet), M3 button-head screws: 4x M3x6 (cover), 4x M3x6 (backer),
2x M3x8 (strap), 4x M3x8 (feet).

Run: freecadcmd epaper_frame.py
"""
import math
import FreeCAD as App
import Part

OUT = "/home/danielcostanzi/epaper-frame/cad/out"
V = App.Vector

# ----------------------------------------------------------------------------
# Hardware specs
# ----------------------------------------------------------------------------
PANEL_W, PANEL_H, PANEL_T = 170.2, 111.2, 1.18
AA_W, AA_H = 163.2, 97.92
# From the panel drawing: active area is centred along the long edge (3.5 mm
# border each side), 3.5 mm border on the top edge, the rest (9.78 mm) on the
# FPC edge where the driver chip sits.
AA_BORDER_SIDE = (PANEL_W - AA_W) / 2.0
AA_BORDER_TOP = 3.5
AA_BORDER_FPC = PANEL_H - AA_H - AA_BORDER_TOP
# FPC tail: ~22 mm wide, centred ~78 mm from one short end (which end depends on
# viewing side), 24 mm long. Relief/cradle are sized to cover both cases.
FPC_ZONE = (60.0, 110.0)          # panel-local x range that the tail can occupy

ADAPTER_W, ADAPTER_H, ADAPTER_PCB_T, ADAPTER_PARTS_H = 31.75, 17.50, 1.6, 3.0
ESP_W, ESP_L, ESP_PCB_T = 29.46, 48.25, 1.6
ESP_PARTS_H = 3.5                 # tallest top-side part (module can ~3.3, USB-C 3.2)
ESP_MODULE_H = 3.3
ESP_MODULE_FROM_TOP = 15.5        # module can centre, from the board end opposite the USB

# ----------------------------------------------------------------------------
# Design parameters
# ----------------------------------------------------------------------------
CLR = 0.3              # panel pocket clearance per side
FOAM_GAP = 0.3         # gap behind the panel, filled by 0.5 mm foam tape on the backer
WINDOW_OVER = 0.5      # window bigger than the active area by this, per side
MARGIN = 14.0          # pocket edge to outer edge
WALL = 2.4
FRONT_T = 2.5
BACKER_T = 4.0
EAR_T = 2.0
COVER_T = 3.0
Z_COVER_IN = 20.5      # inner face of the back cover

INSERT_D, INSERT_DEPTH = 4.0, 4.8
SCREW_D = 3.4
HEAD_D, HEAD_H = 6.2, 1.8
CORNER_BOSS_D, CORNER_INSET = 8.0, 6.0

ESP_PAD_H = 1.0        # raises the board to clear bottom-side solder joints
STRAP_T, STRAP_W, STRAP_FOAM = 2.5, 10.0, 0.8
FOOT_W, FOOT_TILT, FOOT_HEEL, FOOT_TOP = 20.0, 20.0, 45.0, 34.0

# Edge softening (iteration 3). Edges that sit on the print bed get 45 deg chamfers
# (a fillet there would start as a flat overhang); vertical corners get fillets.
CORNER_R = 4.0         # vertical corners of frame + cover
FRONT_CHAMFER = 1.5    # bezel front perimeter (on the bed)
WINDOW_CHAMFER = 1.0   # bevel round the viewing window (on the bed)
BACK_CHAMFER = 1.0     # back cover outer perimeter (on the bed)

MIN_GAP = 0.5

# ----------------------------------------------------------------------------
# Derived layout
# ----------------------------------------------------------------------------
POCKET_W, POCKET_H = PANEL_W + 2 * CLR, PANEL_H + 2 * CLR
OUT_W, OUT_H = POCKET_W + 2 * MARGIN, POCKET_H + 2 * MARGIN
PX0, PY0 = MARGIN, MARGIN
PX1, PY1 = PX0 + POCKET_W, PY0 + POCKET_H
PANEL_X0, PANEL_Y0 = PX0 + CLR, PY0 + CLR

WX0 = PANEL_X0 + AA_BORDER_SIDE - WINDOW_OVER
WX1 = WX0 + AA_W + 2 * WINDOW_OVER
WY0 = PANEL_Y0 + AA_BORDER_FPC - WINDOW_OVER
WY1 = WY0 + AA_H + 2 * WINDOW_OVER

Z_PANEL1 = FRONT_T + PANEL_T
Z_BACKER0 = Z_PANEL1 + FOAM_GAP
Z_SLAB = Z_BACKER0 + BACKER_T - EAR_T       # back face of the bezel slab
Z_BACKER1 = Z_BACKER0 + BACKER_T
Z_COVER_OUT = Z_COVER_IN + COVER_T

corner_centres = [(CORNER_INSET, CORNER_INSET), (OUT_W - CORNER_INSET, CORNER_INSET),
                  (CORNER_INSET, OUT_H - CORNER_INSET), (OUT_W - CORNER_INSET, OUT_H - CORNER_INSET)]
ear_xs = [PANEL_X0 + 0.25 * PANEL_W, PANEL_X0 + 0.75 * PANEL_W]
ear_centres = [(x, PY0 - 5.0) for x in ear_xs] + [(x, PY1 + 5.0) for x in ear_xs]

# Adapter board: lies in a recess on the backer, just above the bottom edge, so
# the panel's FPC tail folds round the backer's bottom edge straight into it.
ADAPTER_SLACK = 12.0   # extra recess width so it can slide to match the tail position
REC_W, REC_H, REC_D = ADAPTER_W + ADAPTER_SLACK, ADAPTER_H + 1.0, 1.2
REC_X0 = PANEL_X0 + sum(FPC_ZONE) / 2.0 - REC_W / 2.0
REC_Y0 = PY0 + 2.0

# ESP32 board: long edge horizontal, USB end against the right-hand short wall
# (seen from the back) so the cable plugs in through a slot in that wall.
ESP_X1 = OUT_W - WALL - 1.8
ESP_X0 = ESP_X1 - ESP_L
ESP_Y0 = 40.0                     # above the feet bosses, below the keyholes
ESP_Y1 = ESP_Y0 + ESP_W
Z_ESP_BOTTOM = Z_COVER_IN - ESP_PAD_H
Z_ESP_TOP = Z_ESP_BOTTOM - ESP_PCB_T
Z_ESP_PARTS = Z_ESP_TOP - ESP_PARTS_H
Z_STRAP1 = Z_ESP_TOP - ESP_MODULE_H - STRAP_FOAM   # strap face touching the foam
Z_STRAP0 = Z_STRAP1 - STRAP_T
STRAP_X = ESP_X0 + ESP_MODULE_FROM_TOP
post_centres = [(STRAP_X, ESP_Y0 - 5.0), (STRAP_X, ESP_Y1 + 5.0)]
USB_Y = (ESP_Y0 + ESP_Y1) / 2.0
USB_Z = Z_ESP_TOP - 1.6
USB_SLOT_W, USB_SLOT_H = 14.0, 9.0

foot_xs = [25.0, OUT_W - 25.0]
foot_screw_ys = [14.0, 26.0]
keyhole_centres = [(OUT_W / 2.0 - 50.0, OUT_H - 24.0), (OUT_W / 2.0 + 50.0, OUT_H - 24.0)]


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(cx, cy, z0, z1, d):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(cx, cy, z0))


def fuse_all(base, shapes):
    for s in shapes:
        base = base.fuse(s)
    return base


def cut_all(base, shapes):
    for s in shapes:
        base = base.cut(s)
    return base


# ----------------------------------------------------------------------------
# Clearance checks (axis-aligned envelopes of everything inside the cavity)
# ----------------------------------------------------------------------------
env = {
    "backer": (PX0, PY0, Z_BACKER0, PX1, PY1, Z_BACKER1),
    "adapter": (REC_X0, REC_Y0, Z_BACKER1 - REC_D, REC_X0 + REC_W, REC_Y0 + REC_H,
                Z_BACKER1 - REC_D + ADAPTER_PCB_T + ADAPTER_PARTS_H),
    "esp32": (ESP_X0, ESP_Y0, Z_ESP_PARTS, ESP_X1, ESP_Y1, Z_COVER_IN),
    "strap": (STRAP_X - STRAP_W / 2, post_centres[0][1] - 4, Z_STRAP0 - HEAD_H,
              STRAP_X + STRAP_W / 2, post_centres[1][1] + 4, Z_STRAP1),
}
for i, (x, y) in enumerate(post_centres):
    env[f"post{i}"] = (x - 4, y - 4, Z_STRAP1, x + 4, y + 4, Z_COVER_IN)
for i, (x, y) in enumerate(ear_centres):
    env[f"ear_screw{i}"] = (x - 3, y - 3, Z_BACKER1, x + 3, y + 3, Z_BACKER1 + HEAD_H)
for i, (x, y) in enumerate(corner_centres):
    env[f"corner_boss{i}"] = (x - 4, y - 4, Z_SLAB, x + 4, y + 4, Z_COVER_IN)
for i, x in enumerate(foot_xs):
    for j, y in enumerate(foot_screw_ys):
        env[f"foot_boss{i}{j}"] = (x - 4.5, y - 4.5, Z_COVER_IN - 4, x + 4.5, y + 4.5, Z_COVER_IN)
for i, (x, y) in enumerate(keyhole_centres):
    # head of the wall screw, which ends up inside the cavity behind the keyhole
    env[f"wall_screw_head{i}"] = (x - 4.25, y - 4.25, Z_COVER_IN - 4, x + 4.25, y + 14.25, Z_COVER_IN)

touching = {("adapter", "backer"), ("strap", "post0"), ("strap", "post1")} | \
           {("backer", f"ear_screw{i}") for i in range(4)}


def gap_ok(a, b):
    return any(a[k + 3] + MIN_GAP <= b[k] or b[k + 3] + MIN_GAP <= a[k] for k in range(3))


names = sorted(env)
problems = []
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if (a, b) in touching or (b, a) in touching:
            continue
        if not gap_ok(env[a], env[b]):
            problems.append(f"{a} collides with {b}")
for n, (x0, y0, z0, x1, y1, z1) in env.items():
    if n.startswith("corner_boss"):
        continue
    if not (WALL <= x0 and x1 <= OUT_W - WALL and WALL <= y0 and y1 <= OUT_H - WALL
            and z1 <= Z_COVER_IN and z0 >= FRONT_T):
        problems.append(f"{n} is outside the cavity")
assert Z_SLAB - INSERT_DEPTH >= 1.0, "backer inserts would break through the front face"
assert not problems, "Clearance problems:\n  " + "\n  ".join(problems)

# ----------------------------------------------------------------------------
# Part: frame
# ----------------------------------------------------------------------------
def edges_on_plane(shape, z, x0=-1e9, y0=-1e9, x1=1e9, y1=1e9):
    return [e for e in shape.Edges
            if all(abs(v.Z - z) < 1e-6 and x0 <= v.X <= x1 and y0 <= v.Y <= y1 for v in e.Vertexes)]


def soft_shell(z0, z1, chamfer_z, chamfer):
    """Outer block with filleted vertical corners and a 45 deg chamfer round the face at chamfer_z."""
    s = box(0, 0, z0, OUT_W, OUT_H, z1)
    vertical = [e for e in s.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6]
    s = s.makeFillet(CORNER_R, vertical)
    return s.makeChamfer(chamfer, edges_on_plane(s, chamfer_z))


frame = soft_shell(0, Z_COVER_IN, 0.0, FRONT_CHAMFER)
frame = frame.cut(box(WX0, WY0, -1, WX1, WY1, FRONT_T + 1))                       # viewing window
frame = frame.makeChamfer(WINDOW_CHAMFER, edges_on_plane(frame, 0.0, WX0 - 0.01, WY0 - 0.01, WX1 + 0.01, WY1 + 0.01))
frame = frame.cut(box(WALL, WALL, Z_SLAB, OUT_W - WALL, OUT_H - WALL, Z_COVER_IN + 1))  # cavity
frame = fuse_all(frame, [cyl(x, y, Z_SLAB - 0.01, Z_COVER_IN, CORNER_BOSS_D) for x, y in corner_centres])
frame = cut_all(frame, [
    box(PX0, PY0, FRONT_T, PX1, PY1, Z_SLAB + 1),                                    # panel + backer pocket
    box(PANEL_X0 + FPC_ZONE[0], PY0 - 4.0, FRONT_T, PANEL_X0 + FPC_ZONE[1], PY0 + 1, Z_SLAB + 1),  # FPC fold relief
    box(PX0 + 10, PY0, FRONT_T - 0.5, PX1 - 10, WY0, FRONT_T + 0.01),               # driver-chip relief
    box(OUT_W - WALL - 1, USB_Y - USB_SLOT_W / 2, USB_Z - USB_SLOT_H / 2, OUT_W + 1, USB_Y + USB_SLOT_W / 2, Z_COVER_IN + 1),
])
frame = cut_all(frame, [cyl(x, y, Z_COVER_IN - INSERT_DEPTH, Z_COVER_IN + 1, INSERT_D) for x, y in corner_centres])
frame = cut_all(frame, [cyl(x, y, Z_SLAB - INSERT_DEPTH, Z_SLAB + 1, INSERT_D) for x, y in ear_centres])

# ----------------------------------------------------------------------------
# Part: backer (presses the panel into the bezel, carries the adapter board)
# ----------------------------------------------------------------------------
backer = box(PX0 + 0.2, PY0 + 0.2, Z_BACKER0, PX1 - 0.2, PY1 - 0.2, Z_BACKER1)
backer = fuse_all(backer, [box(x - 7, min(y - 5, PY1 - 1), Z_SLAB, x + 7, max(y + 5, PY0 + 1), Z_BACKER1)
                           for x, y in ear_centres])
backer = cut_all(backer, [cyl(x, y, Z_SLAB - 1, Z_BACKER1 + 1, SCREW_D) for x, y in ear_centres])
backer = backer.cut(box(REC_X0, REC_Y0, Z_BACKER1 - REC_D, REC_X0 + REC_W, REC_Y0 + REC_H, Z_BACKER1 + 1))

# ----------------------------------------------------------------------------
# Part: back cover
# ----------------------------------------------------------------------------
cover = soft_shell(Z_COVER_IN, Z_COVER_OUT, Z_COVER_OUT, BACK_CHAMFER)

lip_o, lip_t, lip_h = WALL + 0.3, 1.2, 2.0
lip = box(lip_o, lip_o, Z_COVER_IN - lip_h, OUT_W - lip_o, OUT_H - lip_o, Z_COVER_IN + 0.01) \
    .cut(box(lip_o + lip_t, lip_o + lip_t, Z_COVER_IN - lip_h - 1, OUT_W - lip_o - lip_t, OUT_H - lip_o - lip_t, Z_COVER_IN + 1))
lip = cut_all(lip, [cyl(x, y, Z_COVER_IN - lip_h - 1, Z_COVER_IN + 1, CORNER_BOSS_D + 1.0) for x, y in corner_centres])
lip = lip.cut(box(OUT_W - WALL - 3, ESP_Y0 - 3, Z_COVER_IN - lip_h - 1, OUT_W + 1, ESP_Y1 + 3, Z_COVER_IN + 1))
cover = cover.fuse(lip)

# ESP32 cradle: support pads, corner locators, two strap posts with inserts
pads = [cyl(x, y, Z_ESP_BOTTOM, Z_COVER_IN + 0.01, 4.0)
        for x in (ESP_X0 + 3, ESP_X1 - 3) for y in (ESP_Y0 + 3, ESP_Y1 - 3)]
locators = []
c, t, leg = 0.3, 1.2, 5.0
for (x, sx) in ((ESP_X0 - c, -1), (ESP_X1 + c, 1)):
    for (y, sy) in ((ESP_Y0 - c, -1), (ESP_Y1 + c, 1)):
        xa, xb = sorted((x, x + sx * t))
        ya, yb = sorted((y, y + sy * t))
        xl0, xl1 = sorted((x + sx * t, x - sx * leg))
        yl0, yl1 = sorted((y + sy * t, y - sy * leg))
        locators.append(box(xa, yl0, Z_ESP_TOP, xb, yl1, Z_COVER_IN + 0.01))
        locators.append(box(xl0, ya, Z_ESP_TOP, xl1, yb, Z_COVER_IN + 0.01))
posts = [cyl(x, y, Z_STRAP1, Z_COVER_IN + 0.01, 8.0) for x, y in post_centres]
cover = fuse_all(cover, pads + locators + posts)
# Every hole in the cover goes straight through (printed outer face down).
# Strap posts: inserts pressed in from the post top.
cover = cut_all(cover, [cyl(x, y, Z_STRAP1 - 1, Z_COVER_OUT + 1, INSERT_D) for x, y in post_centres])

# Cover screws (into the frame's corner bosses), plain holes
cover = cut_all(cover, [cyl(x, y, Z_COVER_IN - 1, Z_COVER_OUT + 1, SCREW_D) for x, y in corner_centres])

# Feet bosses (inserts pressed in from outside)
foot_pts = [(x, y) for x in foot_xs for y in foot_screw_ys]
cover = fuse_all(cover, [cyl(x, y, Z_COVER_IN - 4, Z_COVER_IN + 0.01, 9.0) for x, y in foot_pts])
cover = cut_all(cover, [cyl(x, y, Z_COVER_IN - 5, Z_COVER_OUT + 1, INSERT_D) for x, y in foot_pts])

# Keyholes for wall mounting (screw head <= 8 mm, shank <= 4 mm): the head goes
# in through the round hole and bears on the cover's inner face.
for x, y in keyhole_centres:
    cover = cut_all(cover, [
        cyl(x, y, Z_COVER_IN - 1, Z_COVER_OUT + 1, 8.5),
        box(x - 2.1, y, Z_COVER_IN - 1, x + 2.1, y + 10, Z_COVER_OUT + 1),
        cyl(x, y + 10, Z_COVER_IN - 1, Z_COVER_OUT + 1, 4.2),
    ])

# ----------------------------------------------------------------------------
# Part: ESP32 strap
# ----------------------------------------------------------------------------
strap = box(STRAP_X - STRAP_W / 2, post_centres[0][1] - 4, Z_STRAP0,
            STRAP_X + STRAP_W / 2, post_centres[1][1] + 4, Z_STRAP1)
strap = cut_all(strap, [cyl(x, y, Z_STRAP0 - 1, Z_STRAP1 + 1, SCREW_D) for x, y in post_centres])

# ----------------------------------------------------------------------------
# Part: foot (one per side). Frame leans back FOOT_TILT degrees, resting on the
# wedge's sole, which starts at the frame's rear bottom edge. Nothing sticks out in
# front of the bezel.
# ----------------------------------------------------------------------------
tan_t = math.tan(math.radians(FOOT_TILT))


def make_foot(xc):
    # Side profile (z, y): attach face on the cover, sole on the desk, sloped back.
    # Seen from the frame, the desk rises going backward: y = (z - Z_COVER_OUT) * tan(tilt).
    x0 = xc - FOOT_W / 2.0
    pts = [(Z_COVER_OUT, 0.0), (Z_COVER_OUT + FOOT_HEEL, FOOT_HEEL * tan_t), (Z_COVER_OUT, FOOT_TOP)]
    wire = Part.makePolygon([V(x0, y, z) for z, y in pts] + [V(x0, pts[0][1], pts[0][0])])
    foot = Part.Face(wire).extrude(V(FOOT_W, 0, 0))
    for y in foot_screw_ys:
        foot = foot.cut(cyl(xc, y, Z_COVER_OUT - 0.1, Z_COVER_OUT + 200, SCREW_D))
        foot = foot.cut(cyl(xc, y, Z_COVER_OUT + 4.0, Z_COVER_OUT + 200, 6.5))
    return foot


feet = [make_foot(x) for x in foot_xs]

# Stability on the desk: the frame can only tip forward over its rear bottom edge,
# so the centre of mass has to land behind that edge by a safe margin.
PLA_DENSITY = 1.24e-3            # g/mm^3, printed parts treated as solid (worst case)
masses = [(sol.Volume * PLA_DENSITY, sol.CenterOfMass)
          for s in (frame, backer, cover, strap, *feet) for sol in s.Solids]
masses.append((44.0, V(PANEL_X0 + PANEL_W / 2, PANEL_Y0 + PANEL_H / 2, (FRONT_T + Z_PANEL1) / 2)))
masses.append((10.0, V(ESP_X0 + ESP_L / 2, ESP_Y0 + ESP_W / 2, Z_ESP_TOP)))
total = sum(m for m, _ in masses)
cog = sum((p * m for m, p in masses), V(0, 0, 0)) * (1.0 / total)
s_t, c_t = math.sin(math.radians(FOOT_TILT)), math.cos(math.radians(FOOT_TILT))
tip_margin = cog.y * s_t + (cog.z - Z_COVER_OUT) * c_t
heel_reach = FOOT_HEEL / c_t
assert 8.0 <= tip_margin <= heel_reach - 8.0, f"desk stance unstable: CoG {tip_margin:.1f} mm behind the rear edge"

# ----------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------
parts = {"frame": frame, "backer": backer, "back_cover": cover, "esp32_strap": strap, "foot": feet[0]}
for name, shape in parts.items():
    shape = shape.removeSplitter()
    assert shape.isValid() and shape.isClosed() and len(shape.Solids) == 1, f"{name}: not a single valid solid"
    parts[name] = shape
    shape.exportStl(f"{OUT}/{name}.stl")
    shape.exportStep(f"{OUT}/{name}.step")

# ----------------------------------------------------------------------------
# Assembly files (assembled + exploded), coloured per part
# ----------------------------------------------------------------------------
# name: (shape, RGB colour, exploded z offset - parts move toward the back)
assembly = {
    "frame":       (parts["frame"],       (70, 70, 75),    0),
    "ref_panel":   (box(PANEL_X0, PANEL_Y0, FRONT_T, PANEL_X0 + PANEL_W, PANEL_Y0 + PANEL_H, Z_PANEL1),
                    (235, 232, 220), 30),
    "backer":      (parts["backer"],      (190, 190, 190), 60),
    "ref_adapter": (box(*env["adapter"]),  (210, 50, 50),   90),
    "esp32_strap": (parts["esp32_strap"], (245, 140, 30),  120),
    "ref_esp32":   (box(*env["esp32"]),    (130, 70, 190),  150),
    "back_cover":  (parts["back_cover"],  (40, 110, 200),  180),
    "foot_1":      (feet[0].removeSplitter(), (60, 170, 90), 230),
    "foot_2":      (feet[1].removeSplitter(), (60, 170, 90), 230),
}


def write_obj(path, items):
    mtl_path = path[:-4] + ".mtl"
    with open(mtl_path, "w") as m:
        for name, _, (r, g, b) in items:
            m.write(f"newmtl {name}\nKd {r / 255:.3f} {g / 255:.3f} {b / 255:.3f}\nKa 0 0 0\n\n")
    with open(path, "w") as f:
        f.write(f"mtllib {mtl_path.split('/')[-1]}\n")
        base = 1
        for name, shape, _ in items:
            pts, tris = shape.tessellate(0.1)
            f.write(f"o {name}\nusemtl {name}\n")
            f.writelines(f"v {p.x:.3f} {p.y:.3f} {p.z:.3f}\n" for p in pts)
            f.writelines(f"f {a + base} {b + base} {c + base}\n" for a, b, c in tris)
            base += len(pts)


import json

with open(f"{OUT}/colours.json", "w") as f:
    json.dump({name: colour for name, (_, colour, _) in assembly.items()}, f, indent=1)

for suffix, explode in (("", False), ("_exploded", True)):
    doc = App.newDocument(f"epaper_frame_assembly{suffix}")
    items = []
    for name, (shape, colour, dz) in assembly.items():
        s = shape.copy()
        if explode:
            s.translate(V(0, 0, dz))
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = s
        obj.Visibility = True  # objects created without the GUI default to hidden
        items.append((name, s, colour))
    doc.recompute()
    fcstd = f"{OUT}/assembly{suffix}.FCStd"
    doc.saveAs(fcstd)
    App.closeDocument(doc.Name)
    write_obj(f"{OUT}/assembly{suffix}.obj", items)

print(f"Outer size: {OUT_W:.1f} x {OUT_H:.1f} x {Z_COVER_OUT:.1f} mm (feet off)")
print(f"Desk stance: {FOOT_TILT:.0f} deg lean, est. mass {total:.0f} g, "
      f"CoG {tip_margin:.1f} mm behind the tipping edge (support reaches {heel_reach:.1f} mm)")
print(f"Visible bezel: sides/top {WX0:.1f} mm, bottom {WY0:.1f} mm")
print(f"Cavity: {Z_COVER_IN - Z_BACKER1:.1f} mm between backer and cover")
print("Min gaps between internal parts >= %.1f mm: OK" % MIN_GAP)
for name, shape in parts.items():
    bb = shape.BoundBox
    print(f"  {name:12s} {bb.XLength:6.1f} x {bb.YLength:6.1f} x {bb.ZLength:5.1f} mm")
