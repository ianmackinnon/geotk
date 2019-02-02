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

from geotk.common import format_float



def header(width, height, unit):
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
