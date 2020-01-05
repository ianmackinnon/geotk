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

import sys
from pathlib import Path

sys.path.append("../")

from geotk.dxf2kicad import dxf2kicad

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(dxf2kicad_case_name):
    (dxf_path, kicad_known_path) = get_test_case(
        "dxf2kicad", dxf2kicad_case_name)

    def f(out):
        with open(dxf_path) as fp:
            dxf2kicad(out, fp)

    api_compare(kicad_known_path, f)



def test_cli(dxf2kicad_case_name):
    (dxf_path, kicad_known_path) = get_test_case(
        "dxf2kicad", dxf2kicad_case_name)

    cli_compare(kicad_known_path, "dxf2kicad", dxf2kicad_case_name, [
        "dxf2kicad",
        dxf_path,
        "__result_path__",
    ])
