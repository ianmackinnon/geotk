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

}



@pytest.mark.parametrize("case_name", PATH_CASES)
def test_poly_points(case_name):
    case = PATH_CASES[case_name]

    result = path_to_poly_list(
        case["d"],
        step_dist=case.get("step_dist", None),
        step_angle=case.get("step_angle", None),
    )[0]

    try:
        assert len(result) == len(case["result"])
        for i, result_item in enumerate(result):
            assert result_item == pytest.approx(case["result"][i], 0.01)
    except AssertionError:

        out_path = Path(f"/tmp/geotk-test-unit-svg-poly-points-{case_name}.svg")
        with NamedTemporaryFile("w", encoding="utf=8", delete=False) as out:
            out.write(header(50, 50, "mm"))
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
        LOG.warning("Saved failing case to `%s`.", out_path)

        raise
