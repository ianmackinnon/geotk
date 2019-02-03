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
from geotk.kicad2svg import REGEX, parse_trace



LOG = logging.getLogger("svg2kicad")

DEFAULT_WIDTH = 0.25



def replace_kicad_traces(
        out, kicad_src_file, layers_paths, width=None, layer=None, net=None):
    """
    Vertex numbers start from 1.
    """

    if width is None:
        width = DEFAULT_WIDTH

    layer_net_path = defaultdict(lambda: defaultdict(list))

    for layer_item in layers_paths:
        if isinstance(layer_item, list):
            LOG.warning("Ignoring path in SVG root.")
            continue
        if not isinstance(layer_item, dict):
            continue

        for net_item in layer_item["paths"]:
            if isinstance(net_item, list):
                LOG.warning("Ignoring path outside of net layer.")
                continue
            if not isinstance(net_item, dict):
                continue

            for path in net_item["paths"]:
                if not isinstance(path, list):
                    LOG.warning("Ignoring non-path inside net layer.")
                    continue
                layer_net_path[layer_item["label"]][net_item["label"]].append(
                    path)


    def write_segments():
        written_layers_nets = []
        for layer_name, net_list in layer_net_path.items():
            if layer is not None and layer_name != layer:
                continue

            for net_name, path_list in net_list.items():
                if net is not None and net_name != str(net):
                    continue

                for path in path_list:
                    last = []
                    for vertex in path:
                        if last:
                            out.write(f"""\
        (segment (start {vertex[0]:0.3f} {vertex[1]:0.3f}) \
        (end {last[0]:0.3f} {last[1]:0.3f}) \
        (width {width}) (layer {layer_name}) (net {net_name}))\n""")
                        last = vertex

                if path_list:
                    written_layers_nets.append((layer_name, net_name))

        return written_layers_nets


    written_layers_nets = None
    for line in kicad_src_file.read().split("\n"):
        match_trace = REGEX["trace"].match(line)

        if match_trace:
            if written_layers_nets is None:
                written_layers_nets = write_segments()

            trace = parse_trace(line)

            if (trace["layer"], str(trace["net"])) in written_layers_nets:
                continue

        out.write(line + "\n")



def svg2kicad(out, svg_file, kicad_src_file, width=None, layer=None, net=None):
    """
    Replace traces in KiCad source file with paths from SVG file.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    layers_paths = svg2paths(svg_file, invert_y=False, with_layers=True)
    replace_kicad_traces(
        out, kicad_src_file, layers_paths, width=width, layer=layer, net=net)
