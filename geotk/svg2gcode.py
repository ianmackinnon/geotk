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

import logging

from geotk.common import format_float
from geotk.svg import svg2paths



LOG = logging.getLogger("svg2gcode")



def write_gcode(out, paths, conf):
    """
    Vertex numbers start from 1.
    """

    out.write("G90\n")
    out.write(f"F{format_float(conf['feedrate'])}\n")

    out.write(f"G0 Z{format_float(conf['z-safety'])}\n")
    for path in paths:
        if not path:
            continue

        out.write(f"G0 X{format_float(path[0][0])} Y{format_float(path[0][1])}\n")
        out.write(f"G1 Z{format_float(conf['z-mill'])}\n")
        for vertex in path[1:]:
            out.write(f"G1 X{format_float(vertex[0])} Y{format_float(vertex[1])}\n")
        out.write(f"G1 Z{format_float(conf['z-safety'])}\n")



def svg2gcode(out, svg_file, conf):
    """
    Write paths in GCODE format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(svg_file)
    write_gcode(out, paths, conf)
