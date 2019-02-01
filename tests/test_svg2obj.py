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

from geotk.svg2obj import svg2obj

from conftest import get_test_case



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



def test_api(svg2obj_case_name):
    (svg_path, obj_known_path) = get_test_case(
        "svg2obj", svg2obj_case_name)

    with open(obj_known_path) as fp:
        obj_known_text = fp.read()

    out = io.StringIO()
    with open(svg_path) as fp:
        svg2obj(out, fp)

    obj_result_text = out.getvalue()

    assert obj_result_text == obj_known_text



def test_cli(svg2obj_case_name):
    (svg_path, obj_known_path) = get_test_case(
        "svg2obj", svg2obj_case_name)

    obj_result_path = f"/tmp/{svg2obj_case_name}.obj"

    try:
        os.remove(obj_result_path)
    except FileNotFoundError:
        pass

    with open(obj_known_path) as fp:
        obj_known_text = fp.read()

    cmd = [
        "svg2obj",
        svg_path,
        obj_result_path,
    ]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status

    cmd = [
        "diff", "-q",
        obj_known_path,
        obj_result_path,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode
    assert not out
    assert not err
    assert not status
