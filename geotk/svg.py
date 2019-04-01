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
import math
import logging

import numpy as np
from bs4 import BeautifulSoup

from geotk.common import format_whitespace, format_float



LOG = logging.getLogger("svg")



# Formatting functions



def header(width, height, unit, grid_spacing=None, grid_x=None, grid_y=None):
    width = format_float(width)
    height = format_float(height)

    out = f"""\
<svg
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
    xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
    width="{width}{unit}"
    height="{height}{unit}"
    viewBox="0 0 {width} {height}"
    >
"""
    if grid_spacing:
        out += f"""\
  <sodipodi:namedview
     inkscape:document-units="mm"
     units="mm"
     id="namedview1582"
     showgrid="true"
     inkscape:zoom="3.0030208"
     inkscape:cx="170.40971"
     inkscape:cy="-40.677854"
     inkscape:current-layer="svg1592">
    <inkscape:grid
       type="xygrid"
       id="grid1598"
       originx="{grid_x or 0}"
       originy="{grid_y or 0}"
       spacingx="{grid_spacing}"
       spacingy="{grid_spacing}"
       units="mm" />
  </sodipodi:namedview>
"""
    else:
        out += f"""\
  <sodipodi:namedview
      inkscape:document-units="{unit}"
      units="{unit}"
      />
"""

    return out



def footer():
    return """\
</svg>
"""



def style(d):
    """Return an SVG style attribute from a dict."""

    return " ".join([f"{key}: {value};" for key, value in d.items()])



def linear_path_d(path):
    if not path or len(path) == 1:
        return None

    path = path[:]

    closed = len(path) > 3 and path[0] == path[-1]
    if closed:
        path = path[:-1]

    d = ""
    for v, vert in enumerate(path):
        command = "L" if v else "M"
        if d:
            d += " "
        d += f"{command} {format_float(vert[0])} {format_float(vert[1])}"
    if closed:
        d += " Z"

    return d



# Parsing functions



def text_to_mm(text):
    text = text.strip().lower()

    match = re.compile(r"^([0-9.]+)\s*mm$", re.U).match(text)
    if match:
        return float(match.group(1))

    match = re.compile(r"^([0-9.]+)\s*cm$", re.U).match(text)
    if match:
        return float(match.group(1)) * 10

    match = re.compile(r"^([0-9.]+)\s*in$", re.U).match(text)
    if match:
        return float(match.group(1)) * 25.4

    LOG.error(
        "No conversion to millimeters found for '%s'.",
        text
    )

    return None



def transform_poly(poly, xform):
    poly2 = []
    for vertex in poly:
        v1 = np.array([[vertex[0]], [vertex[1]], [1]])
        v2 = xform @ v1
        poly2.append([v2[0, 0], v2[1, 0]])
    return poly2



def angle_difference_radians(a1, a2):
    diff = a2 - a1
    if diff > math.pi:
        diff -= 2 * math.pi
    elif diff < -math.pi:
        diff += 2 * math.pi
    return diff



def split_bezier(
        point_f, tangent_f, pa, pb, ta, tb,
        min_dist=None, max_dist=None, max_angle=None,
        depth=None, parent_angle=None
):
    """Split `path` in place as necessary according to dist and angle"""

    if depth is None:
        depth = 0

    def point_2d(t):
        return (point_f(t, 0), point_f(t, 1),)

    def tangent_2d(t):
        return (tangent_f(t, 0), tangent_f(t, 1),)

    do_split = False
    this_angle = None

    section_dist = dist(pa, pb)

    if min_dist is None or section_dist > min_dist:
        if max_dist:
            do_split = section_dist > max_dist

        if not do_split and max_angle:
            tm = (ta + tb) / 2

            da = tangent_2d(ta)
            dm = tangent_2d(tm)
            db = tangent_2d(tb)
            aa = angle(da)
            am = angle(dm)
            ab = angle(db)

            section_angle = max(
                abs(angle_difference_radians(aa, am)),
                abs(angle_difference_radians(aa, ab))
            ) * 180 / math.pi

            if depth < 2 or parent_angle is None or section_angle < parent_angle:
                # Do not split if angle is increasing (near to touching points)
                # except for the first and second split (where curve may be
                # changing direction)
                if section_angle > max_angle:
                    do_split = True
                    this_angle = section_angle

    if not do_split:
        return [pb]

    tm = (ta + tb) / 2
    pm = point_2d(tm)

    def split(pa, pb, ta, tb):
        return split_bezier(
            point_f, tangent_f,
            pa, pb, ta, tb,
            min_dist=min_dist, max_dist=max_dist, max_angle=max_angle,
            depth=depth + 1,
            parent_angle=this_angle,
        )

    return split(pa, pm, ta, tm) + split(pm, pb, tm, tb)



def poly_points_quadratic(
        command, cursor, segment, absolute,
        step_dist=None, step_angle=None, step_min=None
):
    """
    Quadratic Bézier spline.

    Return absolute points
    """

    vertex_list = [tuple(cursor)]
    while segment:
        vertex = tuple(segment[:2])
        segment = segment[2:]

        if absolute:
            vertex_list.append(tuple(vertex))
        else:
            vertex_list.append((
                cursor[0] + vertex[0],
                cursor[1] + vertex[1]
            ))

    p = vertex_list

    def point_f(t, c):
        pc = [v[c] for v in p]
        u = 1 - t
        return (
            pc[0] * pow(u, 2) +
            pc[1] * 2 * u * t +
            pc[2] * pow(t, 2)
        )

    def tangent_f(t, c):
        pc = [v[c] for v in p]
        u = 1 - t
        pc = [v[c] for v in p]
        return (
            pc[0] * -2 * u +
            pc[2] * 2 * t
        )

    max_dist = None if step_dist is None else abs(step_dist) * math.sqrt(2)
    max_angle = None if step_angle is None else abs(step_angle) * math.sqrt(2)

    return split_bezier(
        point_f, tangent_f, cursor, p[2], 0, 1,
        min_dist=step_min, max_dist=max_dist, max_angle=max_angle
    )



def poly_points_cubic(
        command, cursor, segment, absolute,
        step_dist=None, step_angle=None, step_min=None
):
    """
    Cubic Bézier spline.

    Return absolute points
    """

    vertex_list = [tuple(cursor)]
    while segment:
        vertex = tuple(segment[:2])
        segment = segment[2:]

        if absolute:
            vertex_list.append(tuple(vertex))
        else:
            vertex_list.append((
                cursor[0] + vertex[0],
                cursor[1] + vertex[1]
            ))

    p = vertex_list

    def point_f(t, c):
        pc = [v[c] for v in p]
        return (
            pc[0] * pow((1 - t), 3) +
            pc[1] * 3 * pow((1 - t), 2) * t +
            pc[2] * 3 * (1 - t) * pow(t, 2) +
            pc[3] * pow(t, 3)
        )

    def tangent_f(t, c):
        pc = [v[c] for v in p]
        u = 1 - t
        pc = [v[c] for v in p]
        return (
            pc[0] * -3 * pow(u, 2) +
            pc[1] * (3 * pow(u, 2) - 6 * t * u) +
            pc[2] * (-3 * pow(t, 2) + 6 * t * u) +
            pc[3] * 3 * pow(t, 2)
        )

    max_dist = None if step_dist is None else abs(step_dist) * math.sqrt(2)
    max_angle = None if step_angle is None else abs(step_angle) * math.sqrt(2)

    return split_bezier(
        point_f, tangent_f, cursor, p[3], 0, 1,
        min_dist=step_min, max_dist=max_dist, max_angle=max_angle
    )



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



def poly_points_arc(
        command, cursor, segment, absolute,
        step_dist=None, step_angle=None, step_min=None,
):
    """
    Return absolute points
    """

    end = [segment[5], segment[6]] if absolute else [
        cursor[0] + segment[5],
        cursor[1] + segment[6],
    ]

    rx, ry = segment[0:2]
    (_rotation, large, sweep) = segment[2:5]

    large = bool(large)
    sweep = bool(sweep)

    if rx != ry:
        LOG.warning("Simplifying arc with different radii.")
        return [end]

    if cursor == end:
        return []

    ce_dist = dist(cursor, end)
    r = rx

    if r * 2 < ce_dist:
        raise ValueError(
            "Arc diameter is greater than distance between points.")

    c2e = sub(end, cursor)
    mid = add(cursor, mult(c2e, .5))
    dmid = mag(c2e) * .5
    unit = norm(c2e)
    out = tang(unit)

    if (sweep + large) % 2:
        out = mult(out, -1)

    out_dist = math.sqrt((r * r) - (dmid * dmid))

    center = add(mid, mult(out, out_dist))

    a1 = angle(sub(cursor, center))
    a2 = angle(sub(end, center))
    at = a2 - a1

    if (
            (not large and abs(at) > math.pi) or
            (large and abs(at) < math.pi)
    ):
        if at > 0:
            a2 -= 2 * math.pi
        else:
            a2 += 2 * math.pi
        at = a2 - a1

    n = 1

    gain = math.sqrt(2)

    if step_dist:
        n = max(n, math.ceil(abs(at) * r / abs(step_dist * gain)))

    if step_angle:
        n = max(n, math.ceil(
            abs(at) * 180 / math.pi / abs(step_angle * gain)))

    if step_min:
        n = min(n, math.ceil(abs(at) * r / abs(step_min)))


    p_list = []
    for i in range(1, n + 1):
        a = a1 + at * i / n
        v = mult((math.cos(a), math.sin(a)), r)
        p = add(center, v)
        p_list.append(p)

    if not (
            abs(p[0] - end[0]) < 0.01 and
            abs(p[1] - end[1]) < 0.01
    ):
        p_list.append(end)

    return p_list



def poly_points_linear(command, cursor, segment, absolute, **kwargs):
    """
    Return absolute points
    """

    if command.upper() == "H":
        segment.insert(1, cursor[1] if absolute else 0)
    if command.upper() == "V":
        segment.insert(0, cursor[0] if absolute else 0)

    if absolute:
        return [list(segment)]

    return [[
        cursor[0] + segment[0],
        cursor[1] + segment[1],
    ]]



def path_to_poly_list(attrs, step_dist=None, step_angle=None, step_min=None):
    path = attrs["d"]
    path = " " + format_whitespace(path)
    path = re.compile(" ([mlhvzcsqta])([0-9-])", re.I).sub(r"\1 \2", path)
    path = re.sub(",", " ", path)

    handlers = {
        "M": {
            "length": 2,
            "draw": False,
            "path": poly_points_linear,
        },
        "L": {
            "length": 2,
            "path": poly_points_linear,
        },
        "H": {
            "length": 1,
            "path": poly_points_linear,
        },
        "V": {
            "length": 1,
            "path": poly_points_linear,
        },
        "Z": {
            "length": 0,
        },
        "C": {
            "length": 6,
            "path": poly_points_cubic,
        },
        # "S": {
        #     "length": 4,
        #     "path": poly_points_cubic,
        # },
        "Q": {
            "length": 4,
            "path": poly_points_quadratic,
        },
        # "T": {
        #     "length": 2,
        #     "path": poly_points_quadratic,
        # },
        "A": {
            "length": 7,
            "path": poly_points_arc,
        },
    }


    poly_list = [[]]
    cursor = [0, 0]
    command_list = re.compile(" ([mlhvzcsqta])", re.I).split(path)[1:]
    step_options = {
        "step_dist": step_dist,
        "step_angle": step_angle,
        "step_min": step_min,
    }

    for i in range(0, len(command_list), 2):
        command = command_list[i]
        absolute = command == command.upper()
        values = format_whitespace(command_list[i + 1]).split()

        try:
            handler = handlers[command.upper()]
        except KeyError:
            LOG.error("No handler for path segment: %s %s",
                      command, values)
            break

        try:
            values = [float(v) for v in values]
        except ValueError:
            LOG.error("Could not convert all values to float: %s",
                      values)
            break

        if handler.get("draw", True) is False:
            if poly_list[-1]:
                poly_list.append([])

        while values:
            segment = values[:handler["length"]]
            values = values[handler["length"]:]
            if "value" in handler:
                segment = handler["value"](segment)

            if not "path" in handler:
                break

            vertex_list = handler["path"](
                command, cursor, segment, absolute, **step_options)

            for vertex in vertex_list:
                cursor = list(vertex)
                poly_list[-1].append(cursor)

        if command.upper() == "Z":
            cursor = poly_list[-1][0]
            poly_list[-1].append(cursor)


    poly_list = [[(v[0], v[1]) for v in poly] for poly in poly_list]

    return poly_list



def circle_to_poly_list(attrs, step_dist=None, step_angle=None, step_min=None):
    r = float(attrs["r"])
    x = float(attrs["cx"])
    y = float(attrs["cy"])

    path = [[x + r, y]]
    segments = [
        [r, r, 0, 0, 0, x, y - r],
        [r, r, 0, 0, 0, x - r, y],
        [r, r, 0, 0, 0, x, y + r],
        [r, r, 0, 0, 0, x + r, y],
    ]
    for segment in segments:
        path += poly_points_arc(
            "A", path[-1], segment, absolute=True,
            step_dist=step_dist, step_angle=step_angle, step_min=step_min
        )
    return [path]



def parse_transform(text):
    text = format_whitespace(text)

    arrmat = np.array

    match = re.compile(r"""
matrix\(
([0-9.e-]+),
([0-9.e-]+),
([0-9.e-]+),
([0-9.e-]+),
([0-9.e-]+),
([0-9.e-]+)
\)""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        return arrmat((
            [xform[0], xform[2], xform[4]],
            [xform[1], xform[3], xform[5]],
            [0, 0, 1]
        ))

    match = re.compile(r"""
translate\(
([0-9.e-]+),
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        return arrmat((
            [1, 0, xform[0]],
            [0, 1, xform[1]],
            [0, 0, 1]
        ))

    match = re.compile(r"""
translate\(
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        return arrmat((
            [1, 0, xform[0]],
            [0, 1, 0],
            [0, 0, 1]
        ))

    match = re.compile(r"""
rotate\(
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        theta = math.radians(xform[0])
        matrix = arrmat((
            [math.cos(theta), -math.sin(theta), 0],
            [math.sin(theta), math.cos(theta), 0],
            [0, 0, 1]
        ))
        LOG.debug("matrix: %s", matrix)
        return matrix

    match = re.compile(r"""
rotate\(
([0-9.e-]+),
([0-9.e-]+),
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        theta = math.radians(xform[0])
        matrix = arrmat((
            [1, 0, xform[1]],
            [0, 1, xform[2]],
            [0, 0, 1]
        )) @ arrmat((
            [math.cos(theta), -math.sin(theta), 0],
            [math.sin(theta), math.cos(theta), 0],
            [0, 0, 1]
        )) @ arrmat((
            [1, 0, -xform[1]],
            [0, 1, -xform[2]],
            [0, 0, 1]
        ))
        LOG.debug("matrix: %s", matrix)
        return matrix

    match = re.compile(r"""
scale\(
([0-9.e-]+),
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        return arrmat((
            [xform[0], 0, 0],
            [0, xform[1], 0],
            [0, 0, 1]
        ))

    match = re.compile(r"""
scale\(
([0-9.e-]+)
\)
""", re.X).match(text)
    if match:
        LOG.debug("transform: %s", match.group(0))
        xform = [float(v) for v in match.groups()]
        return arrmat((
            [xform[0], 0, 0],
            [0, xform[0], 0],
            [0, 0, 1]
        ))

    LOG.warning(
        "No transform procedure defined for '%s'", text)

    return None



def extract_paths(
        node,
        xform=None, with_layers=None,
        step_dist=None, step_angle=None, step_min=None,
        depth=None,
):
    if xform is None:
        xform = np.identity(3)
    if depth is None:
        depth = 0

    if not hasattr(node, "name") or node.name is None:
        return []

    paths = []

    path_handlers = {
        "path": path_to_poly_list,
        "circle": circle_to_poly_list,
    }

    if hasattr(node, "attrs") and "transform" in node.attrs:
        LOG.debug("transform raw: %s %s", node.name, node["transform"])
        xform_ = parse_transform(node["transform"])
        if xform_ is not None:
            xform = xform @ xform_

    if node.name in path_handlers:
        poly_list = path_handlers[node.name](
            node.attrs, step_dist=step_dist, step_angle=step_angle, step_min=step_min)
        poly_list = [transform_poly(poly, xform) for poly in poly_list]
        paths += poly_list

    elif node.name in ["svg", "g"]:
        label = node.get("inkscape:label", None)
        groupmode = node.get("inkscape:groupmode", None)
        style = node.get("style", "")

        sub_paths = []

        if "display:none" not in style:
            if label:
                LOG.info(label)
            for child in node:
                sub_paths += extract_paths(
                    child, xform=np.copy(xform),
                    with_layers=with_layers,
                    step_dist=step_dist, step_angle=step_angle,
                    step_min=step_min,
                    depth=depth + 1)
        else:
            if label:
                LOG.debug(label)

        if with_layers and groupmode == "layer":
            layer = {
                "label": label,
                "paths": sub_paths,
            }
            paths.append(layer)
        else:
            paths += sub_paths

    elif node.name.startswith("sodipodi"):
        pass

    elif node.name in ["metadata", "defs"]:
        pass

    else:
        LOG.warning("Ignoring node: %s", node.name)

    return paths



def svg2paths(
        svg_file,
        invert_y=True, with_layers=None,
        step_dist=None, step_angle=None, step_min=None
):
    LOG.info("Converting %s", svg_file.name)

    svg_text = svg_file.read()

    soup = BeautifulSoup(svg_text, "lxml")

    svg = soup.find("svg")
    xform = None

    width = svg.get("width", None)
    height = svg.get("height", None)
    viewbox = svg.get("viewbox", None)

    if width and height and viewbox:
        width = text_to_mm(width)
        height = text_to_mm(height)
        viewbox = [float(v) for v in viewbox.split()]
        unit_scale = [
            width / viewbox[2],
            height / viewbox[3]
        ]

        LOG.info("Page size (mm): %0.3f x %0.3f", width, height)
        LOG.info("View box: %0.3f %0.3f %0.3f %0.3f", *viewbox)
        LOG.info("Unit scale: %0.3f, %0.3f", *unit_scale)

        if invert_y:
            xform = np.array([
                [unit_scale[0], 0, 0],
                [0, -unit_scale[1], height],
                [0, 0, 1]
            ])
        else:
            xform = np.array([
                [unit_scale[0], 0, 0],
                [0, unit_scale[1], 0],
                [0, 0, 1]
            ])

    paths = extract_paths(
        svg,
        xform=xform, with_layers=with_layers,
        step_dist=step_dist, step_angle=step_angle, step_min=step_min
    )

    return paths
