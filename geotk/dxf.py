# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import math
import logging

from geotk.common import format_whitespace, format_float



LOG = logging.getLogger("dxf")



def add(p1, p2):
    return [
        p1[0] + p2[0],
        p1[1] + p2[1],
    ]



def sub(p1, p2):
    return [
        p1[0] - p2[0],
        p1[1] - p2[1],
    ]



def mult(p, g):
    return [
        p[0] * g,
        p[1] * g,
    ]



def tang(v):
    return [
        v[1],
        -v[0],
    ]



def mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])



def dist(p1, p2):
    return mag(sub(p2, p1))



def norm(v):
    g = mag(v)
    if not g:
        return v
    return [
        v[0] / g,
        v[1] / g,
    ]



def angle(v):
    return math.atan2(v[1], v[0])



def dxf2lines(dxf_file, invert_y=True):
    LOG.info("Converting %s", dxf_file.name)

    dxf_text = dxf_file.read()

    codes = {
        10: "startX",
        20: "startY",
        11: "endX",
        21: "endY",
    }

    lines = []

    for match in re.compile(r"LINE[^A-Z]*").finditer(dxf_text):
        line_text = match.group(0)
        line = {}
        for i, match in enumerate(
                re.compile(r"\n *([-0-9]+)\n([-0-9.]+)").finditer(line_text)):
            code = int(match.group(1))
            value = float(match.group(2))

            if i == 0:
                assert code, value == (8, 0)
                continue

            if code not in codes:
                raise Exception(f"Unknown DXF line code `{code}`")

            key = codes[code]

            if key in line:
                raise Exception(f"Duplicate DXF line code `{code}`")

            line[key] = value

        missing_keys = set(codes.values()) - set(line.keys())
        if missing_keys:
            raise Exception(
                f"DXF missing values for %s",
                ", ".join([f"`{v}`" for v in missing_keys])
            )

        if invert_y:
            line["startY"] = -line["startY"]
            line["endY"] = -line["endY"]

        lines.append([
            [line["startX"], line["startY"]],
            [line["endX"], line["endY"]],
        ])

    return lines
