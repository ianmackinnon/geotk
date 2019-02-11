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
import shutil
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

PROJECT_PATH = Path(__file__).parent.resolve()

sys.path.append(PROJECT_PATH)

from geotk.svg import header, footer, linear_path_d, style, path_to_poly_list



LOG = logging.getLogger("test_unit_svg")



PATH_CASES = {
    "arc-direct": {
        "d": "M 0,10 A 10,10 0 0 0 10,0",
        "result": (
            (0, 10),
            (10, 0),
        ),
    },

    "arc-dist": {
        "d": "M 0,10 A 10,10 0 0 0 10,0",
        "step_dist": 5,
        "result": (
            (0, 10),
            (5, 8.66),
            (8.66, 5),
            (10, 0),
        ),
    },

    "arc-a45": {
        "d": "M 0,10 A 10,10 0 0 0 10,0",
        "step_angle": 45,
        "result": (
            (0, 10),
            (7.07, 7.07),
            (10, 0),
        ),
    },

    "arc-a30": {
        "d": "M 0,10 A 10,10 0 0 0 10,0",
        "step_angle": 30,
        "result": (
            (0, 10),
            (5, 8.66),
            (8.66, 5),
            (10, 0),
        ),
    },

    "arc-sweep": {
        "d": "M 0,10 A 10,10 0 0 1 10,0",
        "step_dist": 5,
        "result": (
            (0, 10.0),
            (1.34, 5),
            (5, 1.34),
            (10, 0),
        ),
    },

    "arc-large": {
        "d": "M 0,10 A 10,10 0 1 0 10,0",
        "step_angle": 60,
        "result": (
            (0, 10),
            (6.17, 19.24),
            (17.07, 17.07),
            (19.24, 6.17),
            (10, 0),
        ),
    },

    "arc-large-sweep": {
        "d": "M 0,10 A 10,10 0 1 1 10,0",
        "step_angle": 60,
        "result": (
            (0, 10),
            (-9.24, 3.83),
            (-7.07, -7.07),
            (3.83, -9.24),
            (10, 0),
        ),
    },

    "cubic-sine": {
        "d": "M 0,5 C 5,10 10,0 15,5",
        "result": (
            (0, 5),
            (15, 5),
        ),
    },

    "cubic-sine-d3": {
        "d": "M 0,5 C 5,10 10,0 15,5",
        "step_dist": 3,
        "result": (
            (0.00, 5.00),
            (3.75, 6.41),
            (7.50, 5.00),
            (11.25, 3.59),
            (15.00, 5.00),
        ),
    },

    "cubic-sine-a5": {
        "d": "M 0,5 C 5,10 10,0 15,5",
        "step_angle": 20,
        "result": (
            (0.00, 5.00),
            (1.88, 6.23),
            (3.75, 6.41),
            (7.50, 5.00),
            (11.25, 3.59),
            (13.12, 3.77),
            (15.00, 5.00),
        ),
    },

    "cubic-sine-cont-c-d3": {
        "d": "M 0,5  C 5,10 10,0 15,5  20,10 25,0 30,5",
        "step_dist": 3,
        "result": (
            (0.00, 5.00),
            (3.75, 6.41),
            (7.50, 5.00),
            (11.25, 3.59),
            (15.00, 5.00),
            (18.75, 6.41),
            (22.50, 5.00),
            (26.25, 3.59),
            (30.00, 5.00),
        ),
    },

    "quadratic-1": {
        "d": "M 0,10  Q 5,15 10,5",
        "step_dist": 3,
        "result": (
            (0.00, 10.00),
            (2.50, 11.56),
            (5.00, 11.25),
            (7.50, 9.06),
            (8.75, 7.27),
            (10.00, 5.00),
        ),
    },

    "quadratic-cont-1": {
        "d": "M 0,10  Q 5,15 10,5  15,20 20,0",
        "step_angle": 15,
        "result": (
            (0.00, 10.00),
            (1.25, 11.02),
            (2.50, 11.56),
            (3.75, 11.64),
            (4.38, 11.50),
            (5.00, 11.25),
            (6.25, 10.39),
            (7.50, 9.06),
            (10.00, 5.00),
            (11.25, 8.20),
            (11.88, 9.39),
            (12.50, 10.31),
            (12.81, 10.67),
            (13.12, 10.96),
            (13.44, 11.18),
            (13.75, 11.33),
            (14.06, 11.41),
            (14.38, 11.43),
            (15.00, 11.25),
            (17.50, 7.81),
            (20.00, 0.00),
        ),
    },

}



@pytest.mark.parametrize("case_name", PATH_CASES)
def test_poly_points(case_name):
    case = PATH_CASES[case_name]

    result = path_to_poly_list(
        case["d"],
        step_dist=case.get("step_dist", None),
        step_angle=case.get("step_angle", None),
    )[0]

    out_path = Path(f"/tmp/geotk-test-unit-svg-poly-points-{case_name}.svg")
    with NamedTemporaryFile("w", encoding="utf=8", delete=False) as out:
        out.write(header(50, 50, "mm", 50, 12, 23))
        path_style = style({
            "fill": "none",
            "stroke": "#000088",
            "stroke-width": "0.1",
        })
        expected_style = style({
            "fill": "none",
            "stroke": "#008800",
            "stroke-width": "0.1",
        })
        computed_style = style({
            "fill": "none",
            "stroke": "#880000",
            "stroke-width": "0.1",
        })
        out.write(f"""\
  <path style="{path_style}" d="{case['d']}" />
""")
        out.write(f"""\
  <path style="{expected_style}" d="{linear_path_d(case['result'])}" />
""")
        out.write(f"""\
  <path style="{computed_style}" d="{linear_path_d(result)}" />
""")

        out.write(footer())

    shutil.move(out.name, out_path)
    LOG.info("Saved case case to `%s`.", out_path)

    try:
        assert len(result) == len(case["result"])
        for i, result_item in enumerate(result):
            assert result_item == pytest.approx(case["result"][i], 0.01)

    except AssertionError:
        path_text = "\n"
        for result_item in result:
            path_text += "            (%.2f, %.2f),\n" % (
                result_item[0], result_item[1])
        LOG.error(path_text)
        raise
