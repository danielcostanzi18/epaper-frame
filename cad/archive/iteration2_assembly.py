"""
Iteration 2 - adds a back cover that closes the enclosure, with standoffs
for the Waveshare e-Paper ESP32 Driver Board, and a cable exit cutout.

Coordinate system (shared by both parts, so they can be sanity-checked
together in one document):
    z = 0                 : back face of the front frame (where iteration 1's
                             panel pocket is recessed FROM)
    z = +frame_thickness  : front face of the frame (viewing side)
    z = -cavity_depth     : inner face of the back cover (where the ESP32
                             standoffs rise FROM, going toward z=0)
    z = -cavity_depth - back_cover_t : outer face of the back cover (the
                             surface the product rests/hangs on - iteration 3
                             adds feet / wall-mount features here)

Two separate parts/files are produced (two separate print jobs):
    iteration2_frame.*        - iteration 1 frame + cavity side walls (rim)
                                 + 4 corner bosses with heat-set insert holes
    iteration2_back_cover.*   - flat back plate + ESP32 standoffs + screw
                                 clearance holes/counterbores

Known assumptions flagged below (search for "ASSUMPTION") still need
verifying against the physical board/panel - see docs/REQUIREMENTS.md.

Run with: freecadcmd iteration2_assembly.py
"""
import FreeCAD as App
import Part

# ---------------------------------------------------------------------------
# Panel + frame parameters (same as iteration 1)
# ---------------------------------------------------------------------------
panel_w, panel_h, panel_t = 170.2, 111.2, 1.18
active_w, active_h = 163.2, 97.92
clearance_xy, clearance_z, window_margin = 0.3, 0.3, 1.0
margin = 15.0
frame_thickness = 5.0

pocket_l = panel_w + 2 * clearance_xy
pocket_w = panel_h + 2 * clearance_xy
pocket_depth = panel_t + clearance_z

window_l = active_w + 2 * window_margin
window_w = active_h + 2 * window_margin

outer_l = pocket_l + 2 * margin
outer_w = pocket_w + 2 * margin

window_offset_x = (pocket_l - window_l) / 2.0
window_offset_y = (pocket_w - window_w) / 2.0

# ---------------------------------------------------------------------------
# New iteration-2 parameters
# ---------------------------------------------------------------------------
wall_t = 2.4            # cavity side wall thickness
cavity_depth = 12.0     # how far the cavity extends behind the frame (z<0)

boss_d = 8.0            # corner boss outer diameter
boss_inset = 7.5        # boss center distance from each outer edge (fits in the 15mm margin)
insert_hole_d = 4.2     # typical M3 brass heat-set insert hole diameter - VERIFY against your insert brand
insert_depth = 6.0      # blind hole depth into the boss, drilled from the boss's bottom face

screw_clear_d = 3.4     # M3 clearance hole through the back cover
counterbore_d = 6.2     # recess so screw heads sit flush on the back cover's outer face
counterbore_depth = 1.8

back_cover_t = 2.5      # back cover plate thickness

# ---------------------------------------------------------------------------
# Cavity interior usable region (inside the rim walls) - everything below
# must be laid out inside this rectangle, with no overlaps between parts.
# ---------------------------------------------------------------------------
interior_x0 = margin + wall_t
interior_x1 = margin + pocket_l - wall_t
interior_y0 = margin + wall_t
interior_y1 = margin + pocket_w - wall_t


def rects_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def assert_inside_interior(name, rect):
    x0, y0, x1, y1 = rect
    assert interior_x0 <= x0 and x1 <= interior_x1 and interior_y0 <= y0 and y1 <= interior_y1, (
        f"{name} footprint {rect} does not fit inside cavity interior "
        f"({interior_x0:.1f},{interior_y0:.1f})-({interior_x1:.1f},{interior_y1:.1f})"
    )


# ESP32 driver board (Waveshare e-Paper ESP32 Driver Board), real outline
# 29.46 x 48.25mm. Oriented with the long edge (48.25mm) horizontal.
# ASSUMPTION: only the J3-J4 hole spacing (22.65mm) is known from the manual;
# which axis the holes run along, and their inset from the board edges, are
# not confirmed. Assumed here to run along the long (X) edge, centered on
# the board footprint - verify against the real board and adjust
# esp32_holes_along_x / the board position below if wrong.
esp32_w_x = 48.25
esp32_w_y = 29.46
esp32_hole_spacing = 22.65
esp32_holes_along_x = True
esp32_standoff_d = 6.0
esp32_standoff_h = 8.0       # rises from the back cover's inner face toward the frame
esp32_pilot_hole_d = 2.0     # self-tapping pilot hole for a small (M2/M2.5) self-tapping screw
esp32_pilot_depth = 6.0

# Board placed on the right-hand side of the cavity, clear of the adapter
# board cradle (left side, see below) and the rim walls.
esp32_x0 = 115.0
esp32_y0 = 42.0
esp32_footprint = (esp32_x0, esp32_y0, esp32_x0 + esp32_w_x, esp32_y0 + esp32_w_y)
esp32_center_x = esp32_x0 + esp32_w_x / 2.0
esp32_center_y = esp32_y0 + esp32_w_y / 2.0

# ---------------------------------------------------------------------------
# Adapter board cradle (small FPC-to-FFC breakout that plugs directly into
# the panel's own FPC tail). Real outline 31.75 x 17.50mm (measured by user).
# ASSUMPTION, read off the panel's mechanical drawing (docs/REQUIREMENTS.md
# links the source PDF): the FPC tail exits from one of the panel's LONG
# (170.2mm) edges, offset ~24-96mm from one end (left-of-center, not
# centered) - NOT from a short end. Mapped into this script's coordinates
# (panel_w=170.2 along X, panel_h=111.2 along Y), that puts the tail near the
# BOTTOM edge of the pocket (low Y), at local X 24-96mm -> global X 39-111mm.
# VERIFY against the physical panel (look for the black flex tail) - if it's
# actually on the top edge instead of the bottom, flip adapter_cradle_y0 below.
adapter_board_w = 31.75
adapter_board_d = 17.50
adapter_clearance = 1.0        # per side, so the real board slides in easily
adapter_cradle_wall_h = 4.0
adapter_cradle_wall_t = 1.2
adapter_cradle_x_center = 65.0   # within the 39-111mm assumed tail range, clear of the ESP32 board
adapter_cradle_notch_w = 14.0    # gap in the wall facing the panel, for the FPC ribbon to enter

adapter_interior_w = adapter_board_w + 2 * adapter_clearance
adapter_interior_d = adapter_board_d + 2 * adapter_clearance
adapter_cradle_w = adapter_interior_w + 2 * adapter_cradle_wall_t
adapter_cradle_d = adapter_interior_d + 2 * adapter_cradle_wall_t
adapter_cradle_x0 = adapter_cradle_x_center - adapter_cradle_w / 2.0
adapter_cradle_y0 = interior_y0 + 0.5  # hugs the inner face of the bottom rim wall
adapter_footprint = (adapter_cradle_x0, adapter_cradle_y0,
                      adapter_cradle_x0 + adapter_cradle_w, adapter_cradle_y0 + adapter_cradle_d)

assert_inside_interior("ESP32 board", esp32_footprint)
assert_inside_interior("Adapter cradle", adapter_footprint)
assert not rects_overlap(esp32_footprint, adapter_footprint), (
    f"ESP32 footprint {esp32_footprint} overlaps adapter cradle {adapter_footprint}"
)

# Cable exit cutout in the bottom rim wall (for the ESP32's USB-C power
# cable), centered under the ESP32 board for a short, direct cable run.
cable_cutout_w = 12.0
cable_cutout_h = 6.0
cable_cutout_x_center = esp32_center_x

# ---------------------------------------------------------------------------
# Part A: frame (iteration 1 shape + cavity rim + corner bosses)
# ---------------------------------------------------------------------------
outer = Part.makeBox(outer_l, outer_w, frame_thickness)

pocket = Part.makeBox(pocket_l, pocket_w, pocket_depth, App.Vector(margin, margin, 0.0))
window = Part.makeBox(window_l, window_w, frame_thickness,
                       App.Vector(margin + window_offset_x, margin + window_offset_y, 0.0))

frame_shape = outer.cut(pocket).cut(window)

# Cavity rim: outer footprint = pocket footprint (flush under the shoulder),
# wall_t thick, extending from z=0 down to z=-cavity_depth.
rim_outer = Part.makeBox(pocket_l, pocket_w, cavity_depth, App.Vector(margin, margin, -cavity_depth))
rim_inner = Part.makeBox(pocket_l - 2 * wall_t, pocket_w - 2 * wall_t, cavity_depth,
                          App.Vector(margin + wall_t, margin + wall_t, -cavity_depth))
rim = rim_outer.cut(rim_inner)

# Cable exit notch cut through the bottom rim wall
cable_cutout = Part.makeBox(cable_cutout_w, wall_t + 0.4, cable_cutout_h,
                             App.Vector(cable_cutout_x_center - cable_cutout_w / 2.0,
                                        margin - 0.2, -cavity_depth + (cavity_depth - cable_cutout_h) / 2.0))
rim = rim.cut(cable_cutout)

frame_shape = frame_shape.fuse(rim)

# Corner bosses (standoff + heat-set insert holes), one in each corner's margin band
boss_centers = [
    (boss_inset, boss_inset),
    (outer_l - boss_inset, boss_inset),
    (boss_inset, outer_w - boss_inset),
    (outer_l - boss_inset, outer_w - boss_inset),
]
for cx, cy in boss_centers:
    boss = Part.makeCylinder(boss_d / 2.0, cavity_depth, App.Vector(cx, cy, -cavity_depth))
    frame_shape = frame_shape.fuse(boss)

for cx, cy in boss_centers:
    hole = Part.makeCylinder(insert_hole_d / 2.0, insert_depth, App.Vector(cx, cy, -cavity_depth))
    frame_shape = frame_shape.cut(hole)

assert frame_shape.isValid() and frame_shape.isClosed(), "Frame shape is not a valid watertight solid"

# ---------------------------------------------------------------------------
# Part B: back cover (flat plate + ESP32 standoffs + screw holes)
# ---------------------------------------------------------------------------
cover_z0 = -cavity_depth - back_cover_t
cover = Part.makeBox(outer_l, outer_w, back_cover_t, App.Vector(0, 0, cover_z0))

for cx, cy in boss_centers:
    clear_hole = Part.makeCylinder(screw_clear_d / 2.0, back_cover_t + 0.2, App.Vector(cx, cy, cover_z0 - 0.1))
    cover = cover.cut(clear_hole)
    counterbore = Part.makeCylinder(counterbore_d / 2.0, counterbore_depth,
                                     App.Vector(cx, cy, cover_z0 - 0.1))
    cover = cover.cut(counterbore)

if esp32_holes_along_x:
    esp32_centers = [
        (esp32_center_x - esp32_hole_spacing / 2.0, esp32_center_y),
        (esp32_center_x + esp32_hole_spacing / 2.0, esp32_center_y),
    ]
else:
    esp32_centers = [
        (esp32_center_x, esp32_center_y - esp32_hole_spacing / 2.0),
        (esp32_center_x, esp32_center_y + esp32_hole_spacing / 2.0),
    ]
for cx, cy in esp32_centers:
    standoff = Part.makeCylinder(esp32_standoff_d / 2.0, esp32_standoff_h, App.Vector(cx, cy, -cavity_depth))
    cover = cover.fuse(standoff)

for cx, cy in esp32_centers:
    pilot = Part.makeCylinder(esp32_pilot_hole_d / 2.0, esp32_pilot_depth,
                               App.Vector(cx, cy, -cavity_depth + esp32_standoff_h - esp32_pilot_depth))
    cover = cover.cut(pilot)

# Adapter board cradle: a low 4-wall fence (open notch facing the panel, +Y
# side) that locates the small adapter board in X/Y. The board just rests on
# the back cover's inner face inside the fence - no screws, held by the
# FFC/FPC cables either side plus a dab of tape/glue if needed once the real
# board is in hand.
cradle_outer = Part.makeBox(adapter_cradle_w, adapter_cradle_d, adapter_cradle_wall_h,
                             App.Vector(adapter_cradle_x0, adapter_cradle_y0, -cavity_depth))
cradle_inner = Part.makeBox(adapter_interior_w, adapter_interior_d, adapter_cradle_wall_h,
                             App.Vector(adapter_cradle_x0 + adapter_cradle_wall_t,
                                        adapter_cradle_y0 + adapter_cradle_wall_t, -cavity_depth))
cradle = cradle_outer.cut(cradle_inner)
notch = Part.makeBox(adapter_cradle_notch_w, adapter_cradle_wall_t + 0.4, adapter_cradle_wall_h,
                      App.Vector(adapter_cradle_x_center - adapter_cradle_notch_w / 2.0,
                                 adapter_cradle_y0 + adapter_cradle_d - adapter_cradle_wall_t - 0.2, -cavity_depth))
cradle = cradle.cut(notch)
cover = cover.fuse(cradle)

assert cover.isValid() and cover.isClosed(), "Back cover shape is not a valid watertight solid"

# ---------------------------------------------------------------------------
# Save: two printable parts + one combined doc for a visual sanity check
# ---------------------------------------------------------------------------
out_dir = "/home/danielcostanzi/epaper-frame/cad"

doc_frame = App.newDocument("epaper_frame_iteration2_frame")
f_obj = doc_frame.addObject("Part::Feature", "Frame")
f_obj.Shape = frame_shape
doc_frame.recompute()
doc_frame.saveAs(f"{out_dir}/iteration2_frame.FCStd")
frame_shape.exportStl(f"{out_dir}/iteration2_frame.stl")
frame_shape.exportStep(f"{out_dir}/iteration2_frame.step")

doc_cover = App.newDocument("epaper_frame_iteration2_back_cover")
c_obj = doc_cover.addObject("Part::Feature", "BackCover")
c_obj.Shape = cover
doc_cover.recompute()
doc_cover.saveAs(f"{out_dir}/iteration2_back_cover.FCStd")
cover.exportStl(f"{out_dir}/iteration2_back_cover.stl")
cover.exportStep(f"{out_dir}/iteration2_back_cover.step")

doc_asm = App.newDocument("epaper_frame_iteration2_assembly")
a1 = doc_asm.addObject("Part::Feature", "Frame")
a1.Shape = frame_shape
a2 = doc_asm.addObject("Part::Feature", "BackCover")
a2.Shape = cover
doc_asm.recompute()
doc_asm.saveAs(f"{out_dir}/iteration2_assembly.FCStd")

print(f"Frame: {outer_l:.2f} x {outer_w:.2f} x {frame_thickness:.2f}mm, cavity depth {cavity_depth:.1f}mm")
print(f"Cable exit cutout: {cable_cutout_w:.1f} x {cable_cutout_h:.1f}mm in bottom rim wall")
print(f"Corner bosses: d={boss_d}mm at inset {boss_inset}mm, insert hole d={insert_hole_d}mm x {insert_depth}mm deep")
print(f"Back cover: {outer_l:.2f} x {outer_w:.2f} x {back_cover_t:.2f}mm")
print(f"Cavity interior: ({interior_x0:.1f},{interior_y0:.1f}) to ({interior_x1:.1f},{interior_y1:.1f}) "
      f"= {interior_x1-interior_x0:.1f} x {interior_y1-interior_y0:.1f}mm usable")
print(f"ESP32 board footprint: {esp32_footprint} ({esp32_w_x}x{esp32_w_y}mm), "
      f"standoffs d={esp32_standoff_d}mm h={esp32_standoff_h}mm spacing {esp32_hole_spacing}mm")
print(f"Adapter board cradle footprint: {adapter_footprint} "
      f"(real board {adapter_board_w}x{adapter_board_d}mm + {adapter_clearance}mm clearance/side)")
print("Saved: iteration2_frame.*, iteration2_back_cover.*, iteration2_assembly.FCStd")
