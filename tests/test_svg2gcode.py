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
from subprocess import Popen, PIPE

sys.path.append("../")

from geotk.svg2gcode import svg2gcode



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



def test_api(svg2gcode_test_name):
    name = svg2gcode_test_name

    conf_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.conf.json".format(name=name))
    svg_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.svg".format(name=name))
    gcode_known_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.gcode".format(name=name))

    with open(gcode_known_path) as fp:
        gcode_known_text = fp.read()

    out = io.StringIO()

    with open(conf_path) as fp:
        conf = json.load(fp)

    with open(svg_path) as fp:
        svg2gcode(out, fp, conf)

    gcode_result_text = out.getvalue()

    assert gcode_result_text == gcode_known_text



def test_cli(svg2gcode_test_name):
    name = svg2gcode_test_name

    conf_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.conf.json".format(name=name))
    svg_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.svg".format(name=name))
    gcode_known_path = os.path.join(TEST_PATH, "cases/svg2gcode/{name}.gcode".format(name=name))
    gcode_result_path = "/tmp/{name}.gcode".format(name=name)

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
