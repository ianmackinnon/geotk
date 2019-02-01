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
from pathlib import Path
from subprocess import Popen, PIPE

sys.path.append("../")

from geotk.obj2svg import obj2svg

from conftest import get_test_case



TEST_PATH = Path(__file__).parent.resolve()



def test_api(obj2svg_case_name):
    (obj_path, svg_known_path) = get_test_case(
        "obj2svg", obj2svg_case_name)

    with open(svg_known_path) as fp:
        svg_known_text = fp.read()

    out = io.StringIO()
    with open(obj_path) as fp:
        obj2svg(out, fp, unit="mm")

    svg_result_text = out.getvalue()

    assert svg_result_text == svg_known_text



def test_cli(obj2svg_case_name):
    (obj_path, svg_known_path) = get_test_case(
        "obj2svg", obj2svg_case_name)

    svg_result_path = f"/tmp/{obj2svg_case_name}.svg"

    try:
        os.remove(svg_result_path)
    except FileNotFoundError:
        pass

    with open(svg_known_path) as fp:
        svg_known_text = fp.read()

    cmd = [
        "obj2svg",
        "--unit=mm",
        obj_path,
        svg_result_path,
    ]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status

    cmd = [
        "diff", "-q",
        svg_known_path,
        svg_result_path,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status
