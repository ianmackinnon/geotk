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

import math
import logging

from geotk.common import format_float
from geotk.dxf import dxf2lines



LOG = logging.getLogger("dxf2kicad")



def write_kicad(out, lines):
    """
    """

    x_min = None
    x_max = None
    y_min = None
    y_max = None
    path_length = 0

    def stat_point(x, y):
        nonlocal x_min, x_max, y_min, y_max
        if x_min is None or x < x_min:
            x_min = x
        if x_max is None or x > x_max:
            x_max = x
        if y_min is None or y < y_min:
            y_min = y
        if y_max is None or y > y_max:
            y_max = y


    for line in lines:
        stat_point(*line[0])
        stat_point(*line[1])
        path_length += math.sqrt(
            pow(line[0][0] - line[1][0], 2) + pow(line[0][1] - line[1][1], 2)
        )
        out.write(f"""\
  (gr_line \
(start {line[0][0]} {line[0][1]}) \
(end {line[1][0]} {line[1][1]}) \
(layer Edge.Cuts) (width 0.2))
""")

    LOG.debug(f"Size: {x_max - x_min:0.2f} x {y_max - y_min:0.2f}")
    LOG.debug(f"Path length: {path_length:0.2f}")
    LOG.info("Wrote %d lines.", len(lines))



def dxf2kicad(
        out, dxf_file,
):
    """
    Write paths in KICAD format.

    out:  Stream kicadect to write to.

    Use millimeters for output unit.
    """

    lines = dxf2lines(dxf_file)
    write_kicad(out, lines)
