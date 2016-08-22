# -*- coding: utf-8 -*-

# This file is part of 3dgen, a free 3d model generator for EDA
#
# Copyright (C) 2016 José I. Romero <jir@exp1.com.ar>
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
import csv

COLOR_PEACH = (139, 119, 101, 0)
COLOR_BLACK = (25, 25, 25, 0)
COLOR_DARK_GREY = (80, 80, 80, 0)
COLOR_WHITE = (255, 255, 255, 0)
COLOR_SILVER = (230, 230, 230, 0)

default_case_color = {
    'resistor': COLOR_WHITE,
    'capacitor': COLOR_PEACH,
    'inductor': COLOR_DARK_GREY
}

Params = namedtuple("Params", [
    'D',   # package length
    'E',   # package width
    'A',   # package height
    'L',   # pin length
    'family',
    'modelName', # modelName
    'rotation' # rotation if required
])

all_params = {}

def read_params(filename):
    with open(filename) as csvfile:
        db = csv.DictReader(csvfile)
        for row in db:
            all_params[row["case_code"]] = Params(
                D = float(row['D']),
                E = float(row['E']),
                A = float(row['A']),
                L = float(row['L']),
                family = row['family'].lower(),
                modelName = row["case_code"],
                rotation = 0
            )

def make(params, top_color=None, case_color=None, pins_color=None):
    import cadquery as cq
    from Helpers import show

    pt = min(0.025, params.A/10) # Plating thickness
    ef = min(0.020, params.A/20) # Edge fillet

    wp = cq.Workplane("XY")

    pin1 = wp.box(params.L, params.E, params.A)\
             .translate((-params.D/2 + params.L/2, 0, params.A/2))
    pin1.edges("|Y").fillet(ef)
    pin2 = wp.box(params.L, params.E, params.A)\
             .translate((params.D/2 - params.L/2, 0, params.A/2))
    pin2.edges("|Y").fillet(ef)
    pins = pin1.union(pin2)

    if params.family == "resistor":
        case = wp.box(params.D - 2*pt, params.E, params.A - 2*pt)\
                 .translate((0, 0, params.A/2))
        top = wp.box(params.D - 2*params.L, params.E, pt)\
                .translate((0, 0, params.A - pt/2))
        pins = pins.cut(case)
        show(top, top_color or COLOR_BLACK)
    elif params.family in ["capacitor", "inductor"]:
        case = wp.box(params.D - 2*params.L, params.E - 2*pt, params.A - 2*pt)\
                 .translate((0, 0, params.A/2))
        case.edges("|X").fillet(ef)
        pins.edges("|X").fillet(ef)
        case = case.cut(pins)
    else:
        raise ValueError("Unknown family")

    show(case, case_color or default_case_color[params.family])
    show(pins, pins_color or COLOR_SILVER)
