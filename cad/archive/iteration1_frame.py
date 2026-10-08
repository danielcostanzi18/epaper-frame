"""
Iteration 1 - e-Paper frame with rabbet pocket (no front lip).

Design (cross-section through the pocket area, back face at z=0, front face at z=frame_thickness):

  z=frame_thickness (FRONT) ---------------------------------
                              |<- shoulder ->|  window  |<- shoulder ->|
  z=pocket_depth             -----___________          ___________-----
                                   |         |          |         |
  z=0 (BACK)                 ------|  pocket (panel sits here)    |------

- Outer slab: outer_L x outer_W x frame_thickness
- Pocket: recessed from the BACK face, sized to panel outline + XY clearance,
  depth = panel thickness + Z clearance. Panel drops in from the back.
- Window: cut all the way through, sized to active area + small safety
  margin, centered within the pocket by default (SYMMETRIC ASSUMPTION -
  the real panel's active area is likely offset within its outline because
  of the FPC tail on one edge; adjust window_offset_x/y below once the
  physical panel is measured - see docs/REQUIREMENTS.md open item).
- The remaining shoulder (pocket minus window) is what the panel's back
  (inactive, non-viewing) border rests against, stopping it falling
  through to the front. No back cover yet in iteration 1 - panel is held
  by friction/fit for now, back cover comes in iteration 2.

Run with: freecadcmd iteration1_frame.py
"""
import FreeCAD as App
import Part

# ---- Panel data (Waveshare 7.5" e-Paper raw panel, datasheet) ----
panel_w = 170.2
panel_h = 111.2
panel_t = 1.18

# ---- Active (viewable) area ----
active_w = 163.2
active_h = 97.92

# ---- Clearances (first-iteration starting point, tune after test fit) ----
clearance_xy = 0.3   # per side, added to panel outline for the pocket
clearance_z = 0.3    # added to panel thickness for pocket depth
window_margin = 1.0  # per side, added to active area for the viewing window

# ---- Frame geometry ----
margin = 15.0          # bezel border width around the pocket, each side
frame_thickness = 5.0  # total Z thickness of the frame

pocket_l = panel_w + 2 * clearance_xy
pocket_w = panel_h + 2 * clearance_xy
pocket_depth = panel_t + clearance_z

window_l = active_w + 2 * window_margin
window_w = active_h + 2 * window_margin

outer_l = pocket_l + 2 * margin
outer_w = pocket_w + 2 * margin

# Window centered in the pocket by default (SYMMETRIC ASSUMPTION, see docstring)
window_offset_x = (pocket_l - window_l) / 2.0
window_offset_y = (pocket_w - window_w) / 2.0

shoulder_x = window_offset_x
shoulder_y = window_offset_y
print(f"Shoulder width (ledge the panel rests on): x={shoulder_x:.2f}mm  y={shoulder_y:.2f}mm")
assert shoulder_x > 1.5 and shoulder_y > 1.5, "Shoulder too thin to reliably retain the panel"

doc = App.newDocument("epaper_frame_iteration1")

outer = Part.makeBox(outer_l, outer_w, frame_thickness)

pocket_origin_x = margin
pocket_origin_y = margin
pocket_origin_z = 0.0  # pocket recessed from the BACK face (z=0)
pocket = Part.makeBox(pocket_l, pocket_w, pocket_depth,
                       App.Vector(pocket_origin_x, pocket_origin_y, pocket_origin_z))

window_origin_x = pocket_origin_x + window_offset_x
window_origin_y = pocket_origin_y + window_offset_y
window = Part.makeBox(window_l, window_w, frame_thickness,
                       App.Vector(window_origin_x, window_origin_y, 0.0))

frame_shape = outer.cut(pocket).cut(window)

obj = doc.addObject("Part::Feature", "Frame")
obj.Shape = frame_shape
doc.recompute()

out_dir = "/home/danielcostanzi/epaper-frame/cad"
doc.saveAs(f"{out_dir}/iteration1_frame.FCStd")
frame_shape.exportStl(f"{out_dir}/iteration1_frame.stl")
frame_shape.exportStep(f"{out_dir}/iteration1_frame.step")

print(f"Outer footprint: {outer_l:.2f} x {outer_w:.2f} x {frame_thickness:.2f} mm")
print(f"Pocket (back recess): {pocket_l:.2f} x {pocket_w:.2f} x {pocket_depth:.2f} mm deep")
print(f"Window (through opening): {window_l:.2f} x {window_w:.2f} mm")
print("Saved: iteration1_frame.FCStd, .stl, .step")
