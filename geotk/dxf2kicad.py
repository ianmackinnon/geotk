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
from geotk.dxf import dxf2lines



LOG = logging.getLogger("dxf2kicad")



def write_kicad(out, lines):
    """
    """

    for line in lines:
        out.write(f"""\
  (gr_line \
(start {line[0][0]} {line[0][1]}) \
(end {line[1][0]} {line[1][1]}) \
(layer Edge.Cuts) (width 0.2))
""")

    LOG.info("Wrote %d lines.", len(lines))



def dxf2kicad(
        out, dxf_file,
):
    """
    Write paths in KICAD format.

    out:  Stream kicadect to write to.

    Use millimeters for output unit.
    """

    lines = dxf2lines(dxf_file)
    write_kicad(out, lines)
