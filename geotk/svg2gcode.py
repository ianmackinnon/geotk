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



def format_gcode(d):
    command = []
    for k, v in d.items():
        param = k
        if v is not None:
            param += format_float(v)
        command.append(param)
    return " ".join(command)



def write_gcode(out, d):
    out.write(format_gcode(d) + "\n")



def write_paths_gcode(out, paths, conf):
    """
    Vertex numbers start from 1.
    """

    out.write("G90\n")
    out.write(f"F{format_float(conf['feedrate'])}\n")

    out.write(f"G0 Z{format_float(conf['z-safety'])}\n")
    for path in paths:
        if not path:
            continue

        write_gcode(out, {
            "G0": None,
            "X": path[0][0],
            "Y": path[0][1],
        })
        write_gcode(out, {
            "G1": None,
            "Z": conf['z-mill'],
        })

        for vertex in path[1:]:
            write_gcode(out, {
                "G1": None,
                "X": vertex[0],
                "Y": vertex[1],
            })

        write_gcode(out, {
            "G1": None,
            "Z": conf['z-safety'],
        })



def svg2gcode(
        out, svg_file, conf,
        step_dist=None, step_angle=None
):
    """
    Write paths in GCODE format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(
        svg_file,
        step_dist=step_dist, step_angle=step_angle
    )
    write_paths_gcode(out, paths, conf)
