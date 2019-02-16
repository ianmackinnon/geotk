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
import json
from pathlib import Path

sys.path.append("../")

from geotk.svg2gcode import svg2gcode

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(svg2gcode_case_name):
    (conf_path, svg_path, gcode_known_path) = get_test_case(
        "svg2gcode", svg2gcode_case_name)

    with open(conf_path) as fp:
        conf = json.load(fp)

    def f(out):
        with open(svg_path) as fp:
            svg2gcode(out, fp, conf)

    api_compare(gcode_known_path, f)



def test_cli(svg2gcode_case_name):
    (conf_path, svg_path, gcode_known_path) = get_test_case(
        "svg2gcode", svg2gcode_case_name)


    cli_compare(gcode_known_path, "svg2gcode", svg2gcode_case_name, [
        "svg2gcode",
        conf_path,
        svg_path,
        "__result_path__",
    ])
