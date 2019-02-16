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

from geotk.svg2obj import svg2obj

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(svg2obj_case_name):
    (svg_path, obj_known_path) = get_test_case(
        "svg2obj", svg2obj_case_name)

    def f(out):
        with open(svg_path) as fp:
            svg2obj(out, fp, step_dist=30, step_angle=15)

    api_compare(obj_known_path, f)



def test_cli(svg2obj_case_name):
    (svg_path, obj_known_path) = get_test_case(
        "svg2obj", svg2obj_case_name)

    cli_compare(obj_known_path, "svg2obj", svg2obj_case_name, [
        "svg2obj",
        svg_path,
        "__result_path__",
        "--distance-step", "30",
        "--angle-step", "15",
    ])
