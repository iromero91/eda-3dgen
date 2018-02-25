#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of 3dgen, a free 3d model generator for EDA
#
# Copyright (C) 2016-2017 José I. Romero <jir@exp1.com.ar>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License (GPL)
# as published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
# for detail see the LICENCE text file.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
# This project is based on the work of Maurice (easyw) and
# Hasan Yavuz ÖZDERYA (hyOzd) you can find the original files at:
# https://github.com/easyw/kicad-3d-models-in-freecad


from collections import namedtuple

import sys, os

import FreeCAD, Draft
from FreeCAD import Vector

# Ugly hack: This is necessary because CadQuery does not initialize in CLI mode
Gui.activateWorkbench("CadQueryWorkbench")
import FreeCADGui as Gui
#

def exportSTEP(doc, outdir, name):
    filename = os.path.join(outdir, name + '.step')
    import ImportGui
    ImportGui.export(doc.Objects, filename)

def fuseAllObjects(doc, name):
    objs = doc.Objects
    f = doc.addObject("Part::MultiFuse", "Fusion")
    doc.Fusion.Shapes = objs
    doc.recompute()
    s = doc.addObject("Part::Feature", name) 
    s.Shape = f.Shape
    s.ViewObject.ShapeColor = f.ViewObject.ShapeColor
    s.ViewObject.LineColor = f.ViewObject.LineColor
    s.ViewObject.PointColor = f.ViewObject.PointColor
    s.ViewObject.DiffuseColor = f.ViewObject.DiffuseColor
    doc.recompute()
    for o in objs:
        doc.removeObject(o.Name)
    doc.removeObject(f.Name)
    
import libraries

if __name__ == "__main__":
    script_dir=os.path.dirname(os.path.realpath(__file__))
    db_dir = os.path.join("database")
    doc = FreeCAD.newDocument("3DPartGen")

    for library in libraries.__all__:
        FreeCAD.Console.PrintMessage("Processing Library '"+ library +"'\n")
        libmod = vars(libraries)[library]
        libmod.read_params(os.path.join(db_dir, library + ".csv"))
        out_dir=os.path.join(script_dir, library + ".3dshapes")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        FreeCAD.Console.PrintMessage(str(len(libmod.all_params)) +" parts found!\n")
        for part in libmod.all_params.keys():
            for o in doc.Objects:
                doc.removeObject(o.Name)
            FreeCAD.Console.PrintMessage("Generating part '"+ part +"'\n")
            libmod.make(libmod.all_params[part])
            
            fuseAllObjects(doc, part)
            
            exportSTEP(doc, out_dir, part)
            FreeCAD.Console.PrintMessage("Exported STEP!\n")
    FreeCAD.closeDocument(doc.Name)
    exit()
