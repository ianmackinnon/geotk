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
from collections import defaultdict

from geotk.svg import svg2paths



LOG = logging.getLogger("svg2scad")

DEFAULT_WIDTH = 0.25



def write_scad(out, paths):
    """
    Vertex numbers start from 1.
    """

    path_list = []
    point_list = []
    path = []
    for path_data in paths:
        path = []
        for (x, y) in path_data:
            point = [x, y]
            path.append(len(point_list))
            point_list.append(point)
        if path:
            path_list.append(path)

    out.write("polygon(points=[")
    for i, (x, y) in enumerate(point_list):
        if i:
            out.write(", ")
        out.write(f"[{x}, {y}]")
    out.write("], paths=[")
    for i, path in enumerate(path_list):
        if i:
            out.write(", ")
        out.write("[")
        for j, n in enumerate(path):
            if j:
                out.write(", ")
            out.write(f"{n}")
        out.write("]")
    out.write("]);\n")



def svg2scad(
        out, svg_file,
        step_dist=None, step_angle=None, step_min=None
):
    """
    Replace traces in Scad source file with paths from SVG file.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(
        svg_file,
        invert_y=False,
        step_dist=step_dist, step_angle=step_angle,
        step_min=step_min
    )
    write_scad(out, paths)
