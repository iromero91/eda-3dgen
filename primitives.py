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

import cadquery as cq
from cadquery import Vector as Vec
from Helpers import show
from math import *

_s = cq.selectors.StringSyntaxSelector
s_topleft = _s('|Z') & _s('<X') & _s('>Y')

def rowArray(self, e, n, offset, angle):
    wp = self.transformed(rotate=(0, 0, angle))\
             .transformed(offset=(-offset, -e*(n-1)*0.5, 0))
    return wp.pushPoints([(0, e*i) for i in range(n)])

cq.Workplane.rowArray = rowArray


def deePads(self, L, b, c=0.1):
    def _singlePad(pnt):
        P1 = pnt + Vec(-L*0.5, -b*0.5, 0)
        P2 = P1 + Vec(L-b*0.5, 0, 0)
        P3 = pnt + Vec(L*0.5, 0, 0)
        P4 = P2 + Vec(0, b, 0)
        P5 = P1 + Vec(0, b, 0)
        line = cq.Edge.makeLine
        arc = cq.Edge.makeThreePointArc
        w = cq.Wire.combine([line(P1, P2), arc(P2, P3, P4),
                             line(P4, P5), line(P5, P1)])
        return cq.Solid.extrudeLinear(w, [], Vec(0, 0, c))
    return self.eachpoint(_singlePad, True).combine(c)

cq.Workplane.deePads = deePads


def rectPads(self, D, E, c=0.1, tc=0, tr=0,):
    def _singlePad(pnt):
        pnt += Vec(-D*0.5, -E*0.5, 0)
        pad = cq.CQ(cq.Solid.makeBox(D, E, c, pnt))
        if tc > 0:
            if tr > 0:
                pad.edges(_s("|Z") - s_topleft).fillet(tr)
            pad.edges(s_topleft).chamfer(tc)
        elif tr > 0:
            pad.edges("|Z").fillet(tr)
        return pad.objects[0]
    return self.eachpoint(_singlePad, True).combine()

cq.Workplane.rectPads = rectPads


def gullPins(self, L, b, S, H, c=0.1, R=0.13):
    R2 = R + c
    
    def _singlePin(pnt):
        pnt = pnt + Vec(0, -b*0.5, 0)
        P1 = pnt + Vec(-L*0.5, 0, 0)
        P2 = P1 + Vec(L-(R+c/2), 0, 0)
        P3 = P2 + Vec(R2/sqrt(2), 0, R2-R2/sqrt(2))
        P4 = P2 + Vec(R2, 0, R2)
        P5 = Vec(P4.x, P4.y, H-(R+c*0.5))
        P6 = P5 + Vec(R-R/sqrt(2), 0, R/sqrt(2))
        P7 = P5 + Vec(R, 0, R)
        P8 = P1 + Vec(S, 0, H-c*0.5)
        
        Vo = Vec(0, 0, c)
        Ho = Vec(-c, 0, 0)
        Do = Vec(-c/sqrt(2), 0, c/sqrt(2))

        line = cq.Edge.makeLine
        arc = cq.Edge.makeThreePointArc
        w = cq.Wire.combine([
            line(P1, P2), arc(P2, P3, P4), 
            line(P4, P5), arc(P5, P6, P7),
            line(P7, P8), line(P8, P8+Vo), 
            line(P8+Vo, P7+Vo), arc(P7+Vo, P6+Do, P5+Ho),
            line(P5+Ho, P4+Ho), arc(P4+Ho, P3+Do, P2+Vo),
            line(P2+Vo, P1+Vo), line(P1+Vo, P1)
        ])
        return cq.Solid.extrudeLinear(w, [], Vec(0, b, 0))
    return self.eachpoint(_singlePin, True).combine()

cq.Workplane.gullPins = gullPins


def chipCase(self, D, E, A, A1=0.05, fp_d=0.5, fp_o=0.6, fp_z=0.1):
    case = self.workplane(offset=A1)\
               .box(D, E, A-A1, centered=(True, True, False))
    if fp_d > 0 and fp_z > 0:
        case = case.faces(">Z").workplane()\
                               .pushPoints([(-D*0.5+fp_o, E*0.5-fp_o)])\
                               .hole(fp_d, fp_z)
    return case

cq.Workplane.chipCase = chipCase

def epoxyCase(self, D, E, A, A1=0.05, fp_d=0.5, fp_o=0.7, fp_z=0.1):
    A2 = A-A1
    D2 = D-0.15*A2
    E2 = E-0.15*A2
    case = self.workplane(offset=A1).rect(D2, E2)\
               .workplane(offset=A2/2).rect(D, E)\
               .workplane(offset=A2/2).rect(D2, E2).loft(ruled=True)
    if fp_d > 0 and fp_z > 0:
        fp_d = min(fp_d, min(D,E)/4.)
        fp_o = min(fp_o, min(D,E)/3.)
        case = case.faces(">Z").workplane()\
                               .pushPoints([(-D*0.5+fp_o, -E*0.5+fp_o)])\
                               .hole(fp_d, fp_z)
    return case

cq.Workplane.epoxyCase = epoxyCase
