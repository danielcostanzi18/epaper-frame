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
- Fasteners: M3 heat-set inserts (M3 x 4 mm long, hole Ø4.0) with M3 button-head screws.

## Design decisions (implemented in cad/epaper_frame.py)
- Orientation: landscape, with the FPC edge at the bottom (the wide 9.78 mm border hides there).
- Bezel window: active area + 0.5 mm per side, offset to match the asymmetric border.
  The visible bezel is 17.3 mm on the sides and top and 23.6 mm at the bottom.
- The panel is pressed from behind by a 4 mm **backer** plate, with 0.5 mm foam tape between them.
  The backer is screwed to the bezel (4x M3).
- The bezel's back face has a 0.5 mm relief over the driver-chip strip, so nothing presses on the chip.
- A 50 mm wide relief at the bottom edge leaves room for the FPC tail to fold behind the backer.
- The adapter board sits in a recess on the backer's back face. The recess has 12 mm of side slack
  because the tail position depends on which end the 78 mm is measured from.
- The ESP32 sits on the back cover on 4 support pads. Corner locators hold it in place sideways,
  and a screwed strap with a foam pad presses on the module can.
- The ESP32 lies with its long edge horizontal and its USB end against the right-hand short wall
  (seen from the back). A 14 x 9 mm slot in that wall, centred on the board, lets the plug go in from outside.
- 2 keyholes, 100 mm apart, on the back cover (screw head up to 8 mm, shank up to 4 mm).
- 2 removable wedge feet (20 x 34 x 45 mm), each held by 2 screws into inserts in the back cover.
  The frame stands on its rear bottom edge plus the wedges, leaning back 20°. With no front
  support, 15° would leave the centre of mass only ~5 mm behind the tipping edge; 20° gives
  ~12 mm. The script checks this margin on every build.
- Overall size: 198.8 x 139.8 x 23.5 mm.
- Softened edges (iteration 3): the four vertical corners are rounded R4 on both the frame and
  the cover, so the side profile runs continuously across the joint. Edges that print on the bed
  get 45° chamfers: bezel front 1.5 mm, a 1 mm bevel round the viewing window, back cover 1 mm.
  The joint between frame and cover is left sharp so the two parts meet flush.
- Key switch (iteration 4): on the back cover, top centre, in line with the keyholes. It clips from
  outside into a 14 x 14 cutout in a 1.2 mm floor at the bottom of an 18 x 18 mm well, 6.5 mm deep,
  with a 1 mm chamfer round the rim. The bare stem stays 0.5 mm below the back surface, so the
  frame still sits flat on a wall. The cup sits 0.8 mm clear of the backer, allowing for the pins
  and soldered wires.
- Previous iterations are kept untouched in cad/archive/iteration2/ (sharp edges) and
  cad/archive/iteration3/ (softened edges, no key switch).

## Open items to verify on the real parts
1. The FPC tail is on the long edge with the wider (9.78 mm) border. If the window ends up
   off-centre, swap `AA_BORDER_TOP` and `AA_BORDER_FPC` in the script.
2. The ESP32 USB connector is assumed to be centred on its short edge, about 1.6 mm above the PCB.
3. The module can is assumed to be centred 15.5 mm from the board end opposite the USB.
   The strap must land on the metal can, not on the antenna.
4. Heat-set insert hole size: check it against the insert brand you buy.
5. Key switch heights: measure the height above the plate (housing top to stem tip) and below it
   (to the pin tips); `KS_ABOVE` and `KS_BELOW` in the script assume 6.0 and 6.2 mm.
