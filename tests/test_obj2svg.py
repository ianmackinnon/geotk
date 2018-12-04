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

from geotk.obj2svg import obj2svg



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



def test_cone_api():
    name = "cone"
    obj_path = os.path.join(TEST_PATH, "cases/obj2svg/{name}.obj".format(name=name))
    svg_known_path = os.path.join(TEST_PATH, "cases/obj2svg/{name}.svg".format(name=name))

    with open(svg_known_path) as fp:
        svg_known_text = fp.read()

    out = io.StringIO()
    with open(obj_path) as fp:
        obj2svg(out, fp, unit="mm")

    svg_result_text = out.getvalue()

    assert svg_result_text == svg_known_text



def test_cone_cli():
    name = "cone"
    obj_path = os.path.join(TEST_PATH, "cases/obj2svg/{name}.obj".format(name=name))
    svg_known_path = os.path.join(TEST_PATH, "cases/obj2svg/{name}.svg".format(name=name))
    svg_result_path = "/tmp/{name}.svg".format(name=name)

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
