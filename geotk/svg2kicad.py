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
from geotk.kicad2svg import REGEX, parse_trace



LOG = logging.getLogger("svg2kicad")

DEFAULT_WIDTH = 0.25
DEFAULT_LAYER = "F.Cu"
DEFAULT_NET = 0



def replace_kicad_traces(out, kicad_src_file, paths, width=None, layer=None, net=None):
    """
    Vertex numbers start from 1.
    """

    if width is None:
        width = DEFAULT_WIDTH

    if layer is None:
        layer = DEFAULT_LAYER

    if net is None:
        net = DEFAULT_NET

    def write_segments():
        for path in paths:
            last = None
            for vertex in path:
                if last:
                    out.write(f"""\
(segment (start {vertex[0]:0.3f} {vertex[1]:0.3f}) \
(end {last[0]:0.3f} {last[1]:0.3f}) \
(width {width}) (layer {layer}) (net {net}))\n""")
                last = vertex



    written_segments = False
    for line in kicad_src_file.read().split("\n"):
        match_trace = REGEX["trace"].match(line)

        if match_trace:
            if not written_segments:
                write_segments()
                written_segments = True

            trace = parse_trace(line)

            if trace["layer"] == layer and trace["net"] == net:
                continue

        out.write(line + "\n")



def svg2kicad(out, svg_file, kicad_src_file, width=None, layer=None, net=None):
    """
    Replace traces in KiCad source file with paths from SVG file.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(svg_file, invert_y=False)
    replace_kicad_traces(
        out, kicad_src_file, paths, width=width, layer=layer, net=net)
