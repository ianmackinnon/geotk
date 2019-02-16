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

from geotk.kicad2svg import kicad2svg

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(kicad2svg_case_name):
    (kicad_path, svg_pcb_known_path) = get_test_case(
        "kicad2svg", kicad2svg_case_name)

    kwargs = {}
    if "bcu" in kicad2svg_case_name:
        kwargs["layer"] = "B.Cu"
    if "n0" in kicad2svg_case_name:
        kwargs["net"] = 0

    kwargs["grid_spacing"] = 0.127

    def f(out):
        with open(kicad_path) as fp:
            kicad2svg(out, fp, **kwargs)

    api_compare(svg_pcb_known_path, f)




def test_cli(kicad2svg_case_name):
    (kicad_path, svg_pcb_known_path) = get_test_case(
        "kicad2svg", kicad2svg_case_name)

    cmd = [
        "kicad2svg",
        kicad_path,
        "__result_path__",
        "-g", "0.127",
    ]

    if "bcu" in kicad2svg_case_name:
        cmd += ["-l", "B.Cu"]
    if "n0" in kicad2svg_case_name:
        cmd += ["-n", "0"]

    cli_compare(svg_pcb_known_path, "kicad2svg", kicad2svg_case_name, cmd)
