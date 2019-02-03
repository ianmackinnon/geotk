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
import logging
from collections import defaultdict

from geotk.svg import header as svg_header, footer as svg_footer, \
    linear_path_d



LOG = logging.getLogger("kicad2svg")

DEFAULT_WIDTH = 0.25

REGEX = {
    "trace": re.compile(r"^\s*\(segment "),
}


def write_svg(out, layer_net_path, width, height, unit):
    out.write(svg_header(width, height, unit))

    path_style = ("fill:none;stroke:#000000;stroke-width:0.1;"
                  "stroke-miterlimit:4;stroke-dasharray:none")

    for l, (layer_name, net_dict) in enumerate(layer_net_path.items()):
        out.write("\n")
        out.write(f"""\
  <g
      inkscape:label="{layer_name}"
      inkscape:groupmode="layer"
      id="layer-{l}"
      style="display:inline"
      >
""")
        for n, (net, path_list) in enumerate(net_dict.items()):
            if n:
                out.write("\n")

            out.write(f"""\
    <g
        inkscape:label="{net:d}"
        inkscape:groupmode="layer"
        id="layer-{l}-{n}"
        style="display:inline"
        >
""")
            for path in path_list:
                d = linear_path_d(path)
                if d:
                    out.write(f"""\
      <path style="{path_style}" d="{d}"/>
""")

            out.write(f"""\
    </g>
""")
        out.write(f"""\
  </g>
""")

    out.write(svg_footer())



def parse_sexp(text):
    """\
Parse an S-expression and return a nested structure.
Currently does not handle string quoting.
"""

    def parse(text):
        "Return value and number of characters parsed"

        if not text:
            return (None, 0)

        c = 0
        out = []
        token = ""

        def add_token(new_token):
            nonlocal out, token

            if new_token:
                if isinstance(new_token, str):
                    if new_token == "0":
                        new_token = 0
                    elif re.match(r"^-?[1-9][0-9]*$", new_token):
                        new_token = int(new_token)
                    elif re.match(r"^-?[0-9]+\.[0-9]*$", new_token):
                        new_token = float(new_token)
                    elif re.match(r"^-?[0-9]*\.[0-9]+$", new_token):
                        new_token = float(new_token)

                out.append(new_token)

            token = ""


        while c < len(text):
            char = text[c]

            if char in " ":
                add_token(token)
                c += 1
                continue

            if char == "(":
                add_token(token)
                (token, n) = parse(text[c + 1:])
                add_token(token)
                c += 1 + n
                continue

            if char == ")":
                add_token(token)
                c += 1
                break

            token += char
            c += 1

        if out and isinstance(out, list) and len(out) == 1:
            out = out[0]

        if isinstance(out, list):
            out = tuple(out)

        return out, c

    (out, length) = parse(text)

    assert length == len(text)

    return out



def parse_trace(text):
    sexp = parse_sexp(text)
    trace = {}
    for part in sexp:
        if part == "segment":
            continue

        part = list(part)

        key = part.pop(0)
        if not part:
            part = None
        elif len(part) == 1:
            part = part[0]
        else:
            part = tuple(part)
        trace[key] = part

    return trace



def join_segment_list(segment_list):
    nodes = defaultdict(list)

    segment_list = [(v["start"], v["end"]) for v in segment_list]
    for s, segment in enumerate(segment_list):
        nodes[segment[0]].append(s)
        nodes[segment[1]].append(s)

    nodes = dict(nodes)

    path_list = []
    path = None
    while nodes:
        if not path:
            path = [next(iter(nodes))]

        start = path[0]
        end = path[-1]

        if len(path) > 1 and start == end:
            path_list.append(path)
            path = None
            continue

        if end in nodes:
            end_segment_index = nodes[end].pop(0)
            if not nodes[end]:
                del nodes[end]

            segment = segment_list[end_segment_index]
            if segment[0] == end:
                onward_point = segment[1]
            else:
                assert segment[1] == end
                onward_point = segment[0]
            assert onward_point in nodes

            nodes[onward_point].remove(end_segment_index)
            if not nodes[onward_point]:
                del nodes[onward_point]
            path.append(onward_point)
            continue

        if start in nodes:
            start_segment_index = nodes[start].pop(0)
            if not nodes[start]:
                del nodes[start]

            segment = segment_list[start_segment_index]
            if segment[0] == start:
                onward_point = segment[1]
            else:
                assert segment[1] == start
                onward_point = segment[0]
            assert onward_point in nodes

            nodes[onward_point].remove(start_segment_index)
            if not nodes[onward_point]:
                del nodes[onward_point]

            path.insert(0, onward_point)
            continue

        path_list.append(path)
        path = None

    if path:
        path_list.append(path)

    return path_list



def kicad_extract_layer_net_path(kicad_file, layer=None, net=None):
    kicad_text = kicad_file.read()

    layer_net_segment = defaultdict(lambda : defaultdict(list))

    for line in kicad_text.split("\n"):
        match_trace = REGEX["trace"].match(line)

        if match_trace:
            trace = parse_trace(line)

            if layer is not None and trace["layer"] != layer:
                continue

            if net is not None and trace["net"] != net:
                continue

            layer_net_segment[trace["layer"]][trace["net"]].append(trace)

    layer_net_path = {}

    for layer_name, net_dict in layer_net_segment.items():
        layer_net_path[layer_name] = {}
        for net_name, segment_list in net_dict.items():
            layer_net_path[layer_name][net_name] = \
                join_segment_list(segment_list)

    return layer_net_path



def kicad2svg(out, kicad_file, layer=None, net=None):
    """
    Extract traces from KiCad PCB files and save as SVG paths.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    layer_net_path = kicad_extract_layer_net_path(
        kicad_file, layer=layer, net=net)

    write_svg(out, layer_net_path, width=297, height=210, unit="mm")
