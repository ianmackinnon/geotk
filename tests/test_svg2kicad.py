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

from geotk.svg2kicad import svg2kicad

from conftest import get_test_case



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



def test_api(svg2kicad_case_name):
    (svg_path, kicad_src_path, kicad_known_path) = get_test_case(
        "svg2kicad", svg2kicad_case_name)

    with open(kicad_known_path) as fp:
        kicad_known_text = fp.read()

    out = io.StringIO()
    with open(svg_path) as svg_file, \
         open(kicad_src_path) as kicad_src_file:
        svg2kicad(out, svg_file, kicad_src_file)

    kicad_result_text = out.getvalue()

    assert kicad_result_text == kicad_known_text



def test_cli(svg2kicad_case_name):
    (svg_path, kicad_src_path, kicad_known_path) = get_test_case(
        "svg2kicad", svg2kicad_case_name)
    kicad_result_path = f"/tmp/geotk-test-svg2kicad-{svg2kicad_case_name}.kicad_pcb"

    try:
        os.remove(kicad_result_path)
    except FileNotFoundError:
        pass

    with open(kicad_known_path) as fp:
        kicad_known_text = fp.read()

    cmd = [
        "svg2kicad",
        svg_path,
        kicad_src_path,
        kicad_result_path,
    ]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status

    cmd = [
        "diff", "-q",
        kicad_known_path,
        kicad_result_path,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status
