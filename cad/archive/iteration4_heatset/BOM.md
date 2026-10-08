# Bill of Materials — e-paper frame (iteration 4)

Same data as a spreadsheet: `bom.csv`. Part sizes and filament come from `cad/out/` (iteration 4).

## 1. Electronics

| # | Item | Spec | Qty | Used for | Notes |
|---|---|---|---|---|---|
| E1 | Waveshare 7.5" e-Paper raw panel V2 | 800x480, black/white, 170.2 x 111.2 x 1.18 mm | 1 | Display | |
| E2 | Waveshare e-Paper ESP32 Driver Board | 29.46 x 48.25 mm, USB-C | 1 | Controller | Ships with E3 and E4 |
| E3 | e-Paper FPC adapter board | 31.75 x 17.50 mm | 1 | Panel FPC → FFC | Included with E2 |
| E4 | FFC extension cable | 24-pin, 0.5 mm pitch | 1 | Adapter → ESP32 | Included with E2 |
| E5 | Gateron KS-33 Low Profile 2.0 switch | 3-pin, plate-mount for a 1.2 mm plate, any colour | 1 | Button on the back | Used without a keycap |
| E6 | Hook-up wire | AWG 26–28, ~2 x 25 cm | 1 set | Switch → ESP32 GPIO + GND | Solder to the switch pins |
| E7 | USB-C cable + 5 V supply | ≥ 0.5 A | 1 | Power | The plug body must pass a 14 x 9 mm slot |

## 2. Printed parts (PLA, no supports)

| # | Part | File | Qty | Size (mm) | Filament (est.) | Print orientation |
|---|---|---|---|---|---|---|
| P1 | Frame (bezel + walls) | frame.stl | 1 | 198.8 x 139.8 x 20.5 | ~80 g | Front face down |
| P2 | Backer | backer.stl | 1 | 170.4 x 131.8 x 4.0 | ~70 g | Flat back face down |
| P3 | Back cover | back_cover.stl | 1 | 198.8 x 139.8 x 9.7 | ~95 g | Outer face down |
| P4 | ESP32 strap | esp32_strap.stl | 1 | 10.0 x 47.5 x 2.5 | ~1.5 g | Flat |
| P5 | Desk wedge foot | foot.stl | 2 | 20.0 x 34.0 x 45.0 | ~10 g each | Screw face down |
| | **Total** | | | | **~265 g** | Solid parts would be ~335 g |

Filament estimates assume 3 walls, 4 top/bottom layers and 20 % infill. Every part fits a 220 x 220 mm bed.

## 3. Fasteners

| # | Item | Spec | Qty | Used for |
|---|---|---|---|---|
| F1 | Heat-set insert, brass | M3, 4 mm long, for a Ø4.0 hole (check your brand's hole size) | 14 | 4 frame corners, 4 backer, 2 strap posts, 4 feet |
| F2 | Button-head screw | M3 x 6 | 8 | 4 back cover → frame, 4 backer → frame |
| F3 | Button-head screw | M3 x 8 | 6 | 2 ESP32 strap, 4 feet (2 per foot) |
| F4 | Wall screw + plug | Head Ø ≤ 8 mm, shank Ø ≤ 4 mm | 2 | Wall mounting, 100 mm apart. Optional, wall use only |

Buy a few spares of F1–F3: inserts sometimes go in crooked.

## 4. Consumables

| # | Item | Spec | Qty | Used for |
|---|---|---|---|---|
| C1 | Foam tape | 0.5 mm thick, ~5 mm wide, ~60 cm | 1 | Between backer and panel, round the edge |
| C2 | Foam pad | 1 mm thick, ~10 x 15 mm | 1 | Between strap and ESP32 module can |
| C3 | Thin double-sided or Kapton tape | small piece | 1 | Optional: holds the adapter board in its recess (never on the panel) |

## 5. Tools
Soldering iron (inserts and switch wires), M3 hex/screwdriver, flush cutters.

## Not included / open
- No battery: the ESP32 board has a LiPo connector, but the enclosure has no battery bay yet.
- The key switch heights are assumed (6.0 mm above / 6.2 mm below the plate). Check them on the
  real switch before printing P3.
