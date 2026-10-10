# E-Paper Photo Frame — Requirements

3D-printed enclosure for a 7.5" e-paper panel driven by an ESP32. It can hang
on a wall or stand on a desk using removable feet.

## Hardware

| Item | Size (mm) | Notes |
|---|---|---|
| Waveshare 7.5" e-Paper raw panel V2 (800x480) | 170.2 x 111.2 x 1.18 | Active area 163.2 x 97.92. Borders: 3.5 on the sides and top, 9.78 on the FPC edge (the driver chip sits there) |
| Panel FPC tail | ~22 wide, 24 long | On a long edge, centred ~78 mm from one short end |
| FPC adapter board | 31.75 x 17.50 | Plugs onto the panel's FPC tail; FFC extension cable goes to the ESP32 |
| Waveshare e-Paper ESP32 Driver Board | 29.46 x 48.25 | **No mounting holes.** USB on a short edge, ESP32 module at the other end, FPC connector on a long side |
| Gateron KS-33 Low Profile 2.0 key switch (no keycap) | 15 x 15 top housing, 14 x 14 plate cutout, 12.2 total height, 3.0 travel | Clips into a 1.2 mm plate; 2 pins at (-4.4, 4.7) and (2.6, 5.75) from centre. Height split above/below the plate is assumed (6.0 / 6.2 incl. pins) |

Source: Waveshare panel spec PDF (7.5inch_e-Paper_V2_Specification.pdf, p.5) and the
ESP32 driver board manual. Board sizes were measured or confirmed by the user.

## Functional requirements
1. The panel is held in a rabbet (incastro). The bezel overlaps only the inactive border.
2. The panel must be removable without tools other than a screwdriver, and nothing may be glued to it.
3. The ESP32 sits behind the panel. It must not touch the panel or be stuck to it.
4. The ESP32 is held without mounting holes (clamped, not screwed).
5. USB power must be reachable from outside.
6. Wall mounting: keyhole slots.
7. Desk use: removable wedge feet screwed to the back, with nothing sticking out in front of the frame.

## Manufacturing constraints
- FDM, PLA, 220 x 220 mm bed. Every part prints flat without supports.
- Panel pocket (iteration 5): 1.5 mm bigger than the panel + clearance on every side, so the
  panel's sharp corners and edges touch nothing (a printer always rounds inside corners a little).
  The panel is located by 8 teeth, two per side at 1/4 and 3/4 of each edge, 8 mm wide, with
  0.45 mm clearance to the panel (0.3 mm printed too tight) and a 0.6 mm lead-in chamfer at the back.
- Fasteners: M3 button-head screws driven straight into the plastic, into Ø2.7 mm pilot holes
  (the first tightening cuts the thread). Every screw gets at least 4 mm of thread in plastic.
  Each hole has a 0.5 mm 45° chamfer at its mouth (Ø3.7 at the surface) to guide the screw in.

## Design decisions (implemented in cad/epaper_frame.py)
- Orientation: landscape, with the FPC edge at the bottom (the wide 9.78 mm border hides there).
- Bezel window: active area + 0.5 mm per side, offset to match the asymmetric border.
  The visible bezel is 17.4 mm on the sides and top and 23.7 mm at the bottom: wider at the bottom
  because the pixels sit off-centre on the glass (kept on purpose).
- The panel is pressed from behind by two vertical **panel straps** (14 x 132 x 4 mm, iteration 5),
  with 0.5 mm foam tape between straps and panel. Each strap is screwed to the bezel at both ends
  (4x M3 in total). They replace the full backer plate of iteration 4, which used ~5x more plastic.
- The bezel's back face has a 0.5 mm relief over the driver-chip strip, so nothing presses on the chip.
- A 50 mm wide relief at the bottom edge leaves room for the FPC tail to fold behind the panel.
- The adapter board lies on the back of the panel between the two straps, held by its two cables.
  There is 6 mm of free space either side of it, because the tail position depends on which end
  the 78 mm is measured from.
- The ESP32 sits on the back cover on 4 support pads. Corner locators hold it in place sideways,
  and a screwed strap with a foam pad presses on the module can.
- The ESP32 lies with its long edge horizontal and its USB end against the right-hand short wall
  (seen from the back). A 14 x 9 mm slot in that wall, centred on the board, lets the plug go in from outside.
- 2 keyholes, 100 mm apart, on the back cover (screw head up to 8 mm, shank up to 4 mm).
- 2 removable wedge feet (20 x 34 x 45 mm), each held by 2 screws straight into the back cover.
  The frame stands on its rear bottom edge plus the wedges, leaning back 20°. With no front
  support, 15° would leave the centre of mass only ~5 mm behind the tipping edge; 20° gives
  ~12 mm. The script checks this margin on every build.
- Overall size: 199.1 x 140.1 x 23.5 mm.
- Softened edges (iteration 3): the four vertical corners are rounded R4 on both the frame and
  the cover, so the side profile runs continuously across the joint. Edges that print on the bed
  get 45° chamfers: bezel front 1.5 mm, a 1 mm bevel round the viewing window, back cover 1 mm.
  The joint between frame and cover is left sharp so the two parts meet flush.
- Key switch (iteration 4): on the back cover, top centre, in line with the keyholes. It clips from
  outside into a 14 x 14 cutout in a 1.2 mm floor at the bottom of an 18 x 18 mm well, 6.5 mm deep,
  with a 1 mm chamfer round the rim. The bare stem stays 0.5 mm below the back surface, so the
  frame still sits flat on a wall. The cup sits 0.8 mm clear of the panel-strap level, allowing for the pins
  and soldered wires.
- Previous iterations are kept untouched in cad/archive/: iteration2/ (sharp edges), iteration3/
  (softened edges, no key switch), iteration4_heatset/ (heat-set inserts) and iteration4/ (full
  backer plate with adapter recess).

## Open items to verify on the real parts
1. The FPC tail is on the long edge with the wider (9.78 mm) border. If the window ends up
   off-centre, swap `AA_BORDER_TOP` and `AA_BORDER_FPC` in the script.
2. The ESP32 USB connector is assumed to be centred on its short edge, about 1.6 mm above the PCB.
3. The module can is assumed to be centred 15.5 mm from the board end opposite the USB.
   The strap must land on the metal can, not on the antenna.
4. Pilot hole size (`PILOT_D` = 2.7 mm): print a test piece. Go 2.5 if the screws feel loose,
   2.8 if the plastic cracks. Holes in the feet wear fastest, since they are removed most.
5. Key switch heights: measure the height above the plate (housing top to stem tip) and below it
   (to the pin tips); `KS_ABOVE` and `KS_BELOW` in the script assume 6.0 and 6.2 mm.
