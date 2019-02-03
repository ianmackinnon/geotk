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

import os
import io
import sys
from subprocess import Popen, PIPE

sys.path.append("../")

from geotk.kicad2svg import kicad2svg

from conftest import get_test_case



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



def test_api(kicad2svg_case_name):
    (kicad_path, svg_pcb_known_path) = get_test_case(
        "kicad2svg", kicad2svg_case_name)

    with open(svg_pcb_known_path) as fp:
        svg_pcb_known_text = fp.read()

    kwargs = {}
    if "bcu" in kicad2svg_case_name:
        kwargs["layer"] = "B.Cu"
    if "n0" in kicad2svg_case_name:
        kwargs["net"] = 0

    out = io.StringIO()
    with open(kicad_path) as fp:
        kicad2svg(out, fp, **kwargs)

    svg_pcb_result_text = out.getvalue()

    assert svg_pcb_result_text == svg_pcb_known_text



def test_cli(kicad2svg_case_name):
    (kicad_path, svg_pcb_known_path) = get_test_case(
        "kicad2svg", kicad2svg_case_name)
    svg_pcb_result_path = f"/tmp/geotk-test-kicad2svg-{kicad2svg_case_name}.svg"

    try:
        os.remove(svg_pcb_result_path)
    except FileNotFoundError:
        pass

    with open(svg_pcb_known_path) as fp:
        svg_pcb_known_text = fp.read()

    cmd = [
        "kicad2svg",
        kicad_path,
        svg_pcb_result_path,
    ]

    if "bcu" in kicad2svg_case_name:
        cmd += ["-l", "B.Cu"]
    if "n0" in kicad2svg_case_name:
        cmd += ["-n", "0"]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status

    cmd = [
        "diff", "-q",
        svg_pcb_known_path,
        svg_pcb_result_path,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status
