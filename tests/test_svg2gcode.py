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
import json
from pathlib import Path
from subprocess import Popen, PIPE

sys.path.append("../")

from geotk.svg2gcode import svg2gcode

from conftest import get_test_case



TEST_PATH = Path(__file__).parent.resolve()



def test_api(svg2gcode_case_name):
    (conf_path, svg_path, gcode_known_path) = get_test_case(
        "svg2gcode", svg2gcode_case_name)

    with open(gcode_known_path) as fp:
        gcode_known_text = fp.read()

    out = io.StringIO()

    with open(conf_path) as fp:
        conf = json.load(fp)

    with open(svg_path) as fp:
        svg2gcode(out, fp, conf, step_dist=30, step_angle=15)

    gcode_result_text = out.getvalue()

    assert gcode_result_text == gcode_known_text



def test_cli(svg2gcode_case_name):
    (conf_path, svg_path, gcode_known_path) = get_test_case(
        "svg2gcode", svg2gcode_case_name)
    gcode_result_path = f"/tmp/geotk-test-svg2gcode-{svg2gcode_case_name}.gcode"

    try:
        os.remove(gcode_result_path)
    except FileNotFoundError:
        pass

    with open(gcode_known_path) as fp:
        gcode_known_text = fp.read()

    cmd = [
        "svg2gcode",
        conf_path,
        svg_path,
        gcode_result_path,
        "--distance-step", "30",
        "--angle-step", "15",
    ]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status

    cmd = [
        "diff", "-q",
        gcode_known_path,
        gcode_result_path,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status
