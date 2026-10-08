# E-paper frame

3D-printed enclosure for a Waveshare 7.5" e-paper panel (800x480) driven by the Waveshare
e-Paper ESP32 Driver Board. It hangs on a wall (keyholes) or stands on a desk (removable
wedge feet), and has a Gateron low-profile key switch on the back.

- `docs/REQUIREMENTS.md` – hardware specs and design decisions
- `docs/ASSEMBLY.md` – print settings and assembly steps
- `docs/BOM.md` / `docs/bom.csv` – bill of materials
- `cad/epaper_frame.py` – parametric FreeCAD model (all parts); STL/STEP files and the coloured
  assembly are in `cad/out/`, earlier iterations in `cad/archive/`

Rebuild (FreeCAD 0.19):

```
cd cad
freecadcmd epaper_frame.py
QT_QPA_PLATFORM=offscreen freecad colour_assembly.py
```
