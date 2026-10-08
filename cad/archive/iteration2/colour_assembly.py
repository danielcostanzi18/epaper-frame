"""
Applies the part colours (out/colours.json) to the assembly .FCStd files.
Colours are GUI data, so this must run in the FreeCAD GUI; offscreen is fine:

    QT_QPA_PLATFORM=offscreen freecad colour_assembly.py
"""
import json
import os
import FreeCAD as App
import FreeCADGui as Gui

OUT = "/home/danielcostanzi/epaper-frame/cad/out"
colours = json.load(open(f"{OUT}/colours.json"))
log = []
for fname in ("assembly.FCStd", "assembly_exploded.FCStd"):
    doc = App.openDocument(f"{OUT}/{fname}")
    for obj in doc.Objects:
        r, g, b = colours[obj.Name]
        obj.ViewObject.ShapeColor = (r / 255.0, g / 255.0, b / 255.0)
        obj.ViewObject.Visibility = True
    try:
        view = Gui.getDocument(doc.Name).activeView()
        view.viewIsometric()
        view.fitAll()
    except Exception as e:
        log.append(f"{fname}: could not set camera ({e})")
    doc.save()
    hidden = [o.Name for o in doc.Objects if not o.ViewObject.Visibility]
    log.append(f"{fname}: {len(doc.Objects)} parts coloured, hidden: {hidden}")
    App.closeDocument(doc.Name)
with open(f"{OUT}/colour_log.txt", "w") as f:
    f.write("\n".join(log) + "\n")
for p in os.listdir(OUT):
    if p.endswith(".FCStd1"):
        os.remove(f"{OUT}/{p}")
os._exit(0)
