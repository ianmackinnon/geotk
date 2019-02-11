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



LOG = logging.getLogger("svg2obj")



def write_obj(out, paths):
    """
    Vertex numbers start from 1.
    """

    vertex_list = []
    face_list = []

    for path in paths:
        face = []
        for vertex in path:
            vertex_list.append(vertex)
            v = len(vertex_list)
            face.append(v)
        face_list.append(face)

    out.write("g\n")
    for vertex in vertex_list:
        out.write(f"v {format_float(vertex[0])} {format_float(vertex[1])} 0\n")
    for face in face_list:
        out.write("f ")
        out.write(" ".join([str(v) for v in face]))
        out.write("\n")
    LOG.info("Wrote %d vertices and %d faces.",
             len(vertex_list), len(face_list))



def svg2obj(
        out, svg_file,
        step_dist=None, step_angle=None
):
    """
    Write paths in OBJ format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(
        svg_file,
        step_dist=step_dist, step_angle=step_angle
    )
    write_obj(out, paths)
