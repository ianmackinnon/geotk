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

from geotk.geo import svg2paths



LOG = logging.getLogger("svg2gcode")



def format_float(value):
    if not value:
        return "0"

    if int(value) == value:
        return "%d" % value

    return str(value)



def write_gcode(out, paths, conf):
    """
    Vertex numbers start from 1.
    """

    out.write("G90\n")
    out.write("F%s\n" % format_float(conf["feedrate"]))

    out.write("G0 Z%s\n" % format_float(conf["z-safety"]))
    for path in paths:
        if not path:
            continue

        out.write("G0 X%s Y%s\n" % (format_float(path[0][0]), format_float(path[0][1])))
        out.write("G1 Z%s\n" % format_float(conf["z-mill"]))
        for vertex in path[1:]:
            out.write("G1 X%s Y%s\n" % (format_float(vertex[0]), format_float(vertex[1])))
        out.write("G1 Z%s\n" % format_float(conf["z-safety"]))



def svg2gcode(out, svg_file, conf):
    """
    Write paths in GCODE format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(svg_file)
    write_gcode(out, paths, conf)
