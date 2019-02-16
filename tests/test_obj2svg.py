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

from geotk.obj2svg import obj2svg

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(obj2svg_case_name):
    (obj_path, svg_known_path) = get_test_case(
        "obj2svg", obj2svg_case_name)

    def f(out):
        with open(obj_path) as fp:
            obj2svg(out, fp, unit="mm")

    api_compare(svg_known_path, f)



def test_cli(obj2svg_case_name):
    (obj_path, svg_known_path) = get_test_case(
        "obj2svg", obj2svg_case_name)

    cli_compare(svg_known_path, "obj2svg", obj2svg_case_name, [
        "obj2svg",
        "--unit=mm",
        obj_path,
        "__result_path__",
    ])
