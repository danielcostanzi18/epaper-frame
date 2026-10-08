# Assembly

## Look at it first
- `cad/out/assembly.FCStd` (assembled) and `cad/out/assembly_exploded.FCStd` open in FreeCAD with
  one colour per part. `assembly*.obj` are the same models for any other 3D viewer.
- Colours: frame dark grey, panel off-white, backer light grey, adapter board red, strap orange,
  ESP32 purple, back cover blue, feet green. The panel and the two boards are stand-in blocks.
- To regenerate everything: `freecadcmd epaper_frame.py`, then
  `QT_QPA_PLATFORM=offscreen freecad colour_assembly.py`.

## Print (PLA, no supports)
| Part | Qty | Orientation |
|---|---|---|
| frame.stl | 1 | front face down |
| backer.stl | 1 | flat back face down (adapter recess on the bed) |
| back_cover.stl | 1 | outer face down (the key switch floor is a 2 mm overhang round the cutout: no supports needed) |
| esp32_strap.stl | 1 | flat |
| foot.stl | 2 | flat face (the one that screws to the cover) down |

## Hardware
- M3 button-head screws, driven straight into Ø2.7 mm pilot holes in the plastic:
  8x M3x10 (4 cover corners, 4 feet), 4x M3x6 (backer), 2x M3x8 (strap).
  The first tightening cuts the thread: go in slowly and stop as soon as the head seats.
- 1x Gateron KS-33 Low Profile 2.0 switch
- 0.5 mm foam tape (backer → panel), a 1 mm foam pad (strap → ESP32 module)

## Steps (looking at the back)
1. Lay the frame face down. Drop the panel into the pocket with the FPC tail at the **bottom** edge.
2. Stick strips of 0.5 mm foam tape around the edge of the backer's flat side.
   Lay the backer on the panel and fix it with 4x M3x6.
3. Fold the FPC tail gently (don't crease it) round the backer's bottom edge, through the gap
   at the bottom of the pocket. Plug it into the adapter board, then seat the adapter in the
   backer's recess. Slide it sideways until the tail lies flat. A small piece of tape onto the
   backer is fine; never tape anything to the panel.
4. Connect the FFC extension cable to the adapter board.
5. Place the ESP32 on the back cover's 4 pads inside the corner locators, USB end towards the
   right-hand short side (seen from the back). Put the 1 mm foam pad on the module can and
   screw the strap down (2x M3x8).
6. Plug the FFC cable into the ESP32 and tuck the spare length away from the strap.
7. Key switch: push it into the well on the outside of the back cover until its clips snap under
   the 1.2 mm floor. Solder two wires to its pins and connect them to a free ESP32 GPIO and GND
   (enable the internal pull-up). Keep the wires flat against the cover.
8. Close the back cover. Its lip goes inside the walls. Fix it with 4x M3x10.
9. Plug USB-C in through the slot in the short side wall.

## Wall or desk
- **Wall:** two screws in the wall, 100 mm apart and level, sticking out about 5 mm (head up to 8 mm,
  shank up to 4 mm). Push the heads through the round holes of the keyholes, then let the frame
  drop so the shanks slide into the slots. The heads catch on the inside of the cover.
- **Desk:** screw the two wedges onto the back cover, thin end up (2x M3x10 each, through the
  counterbores). The frame stands on its bottom back edge and the wedges, leaning back 20°.
