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

from geotk.common import clean_whitespace



LOG = logging.getLogger("obj2svg")


Z_WARN_NON_ZERO = False



def write_svg(out, face_list, vert_list, width, height, unit):
    out.write('''<svg
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns="http://www.w3.org/2000/svg"
  width="%f%s"
  height="%f%s"
  viewBox="%f %f %f %f"
>
''' % (width, unit, height, unit, 0, 0, width, height))

    if unit:
        out.write('''<sodipodi:namedview
     inkscape:document-units="%s"
     units="%s"
/>
''' % (unit, unit))


    for face in face_list:
        out.write('  <path style="fill:none;stroke:#000000;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none" d=\"')
        for i, v in enumerate(face):
            vert = vert_list[v - 1]
            out.write(" %s%f %f" % (
                "M" if i == 0 else "L",
                vert[0],
                vert[1],
            ))
        out.write(' Z"/>\n')
    out.write('</svg>')

    LOG.info("%s faces.", len(face_list))



def remove_backtracks(face_list):
    line_dict = defaultdict(int)

    for face in face_list:
        if not face:
            continue
        cursor = face[0]
        for vert in face[1:]:
            if cursor == vert:
                continue
            pair = tuple(sorted([cursor, vert]))
            line_dict[pair] += 1 if vert > cursor else -1
            LOG.info(pair)
            cursor = vert

    line_dict = dict(line_dict)
    LOG.info(sorted(line_dict.items()))
    LOG.info("")

    line_soup = defaultdict(list)
    for key, value in line_dict.items():
        if value > 0:
            line_soup[key[0]] += [key[1]] * value
        elif value < 0:
            line_soup[key[1]] += [key[0]] * -value

    line_soup = dict(line_soup)
    LOG.info(repr(line_soup))
    LOG.info("")

    poly_list = [[]]
    while line_soup:
        if poly_list[-1]:
            s1 = poly_list[-1][0]
        else:
            s1 = list(line_soup.keys())[0]
            poly_list[-1].append(s1)

        if len(poly_list[-1]) > 1:
            e1 = poly_list[-1][-1]
            if s1 == e1:
                poly_list.append([])
                continue
        else:
            e1 = line_soup[s1].pop(0)
            if not line_soup[s1]:
                del line_soup[s1]
            poly_list[-1].append(e1)

        try:
            e2 = line_soup[e1].pop(0)
        except:
            poly_list.append([])
            continue

        if not line_soup[e1]:
            del line_soup[e1]
        poly_list[-1].append(e2)

    LOG.info(repr(poly_list))
    LOG.info("")

    return poly_list



def obj2svg(out, obj_file, unit=""):
    LOG.info(obj_file.name)

    obj_text = obj_file.read()

    vert_list = []
    face_list = []

    obj_text = re.compile(r"\s*\\\n\s*").sub(" ", obj_text)

    x_min = None
    y_min = None
    x_max = None
    y_max = None

    for line in obj_text.splitlines():
        line = re.sub("#.*$", "", line)
        line = line.strip()
        if not line:
            continue

        g_match = re.match("g", line)
        if g_match:
            continue

        vn_match = re.match("vn ([-0-9e.]+) ([-0-9e.]+) ([-0-9e.]+)", line)
        if vn_match:
            continue

        v_match = re.match("v ([-0-9e.]+) ([-0-9e.]+) ([-0-9e.]+)", line)
        if v_match:
            point = [float(v) for v in v_match.groups()]
            (x, y, z) = point
            x_min = x if x_min is None else min(x_min, x)
            y_min = y if y_min is None else min(y_min, y)
            x_max = x if x_max is None else max(x_max, x)
            y_max = y if y_max is None else max(y_max, y)
            if Z_WARN_NON_ZERO and z != 0:
                LOG.warning("Point is not in z-plane")
                sys.exit(1)
            vert_list.append(point)
            continue

        f_match = re.match("f( [-0-9e./]+)+$", line)
        if f_match:
            face = [int(v.split("/")[0]) for v in line.split()[1:]]
            LOG.debug("Face %d: %s", len(face_list), repr(face))
            face_list.append(face)
            continue

        LOG.error(line)
        sys.exit(1)

    width = x_max - x_min
    height = y_max - y_min

    write_svg(out, face_list, vert_list, width, height, unit)
