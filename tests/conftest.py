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

import logging
import warnings
from pathlib import Path
from collections import defaultdict, namedtuple



TEST_PATH = Path(__file__).parent.resolve()

TEST_CASE_PATTERNS = {
    "svg2gcode": ("conf_json", "svg", "gcode"),
    "svg2obj": ("svg", "obj"),
    "obj2svg": ("obj", "svg"),
}


LOG = logging.getLogger("conftest")



class GenerateError(Exception):
    pass



def get_case_names(func_name, suffix_list):
    """
    Get file stems for test cases.
    Raise a warning if only some of the files for a test case are present,
    or if an unexpected file with the same name is found.
    """

    case_path = TEST_PATH / "cases" / func_name
    name_dict = defaultdict(set)

    suffix_required = {v.replace("_", ".") for v in suffix_list}

    for base in case_path.iterdir():
        # Split on first dot, rather than splitting
        # before last dot like pathlib.
        (stem, suffix) = str(base).split(".", 1)
        if suffix not in suffix_required:
            warnings.warn(
                f"File '{base}' with unexpected suffix `{base.suffix}` "
                f"in test case directory `{case_path}`")
        name_dict[stem].add(suffix)

    name_list = []
    for stem, suffix_set in name_dict.items():
        if suffix_set != suffix_required:
            warnings.warn(f"Unexpected suffix in file suffixes {suffix_set} "
                          f"for test case `{stem}` in directory `{case_path}`")
            continue
        name_list.append(stem)

    return [Path(name).name for name in sorted(name_list)]



def get_test_case(func_name, case_name):
    """
    Return a named tuple of paths for test case files.
    """

    case_path = TEST_PATH / "cases" / func_name
    suffix_list = TEST_CASE_PATTERNS[func_name]
    return namedtuple(f"{func_name}Case", suffix_list)(
        *[case_path / f"{case_name}.{v.replace('_', '.')}"
          for v in suffix_list])



def pytest_generate_tests(metafunc):
    for func_name, suffix_list in TEST_CASE_PATTERNS.items():
        fixture_name = f"{func_name}_case_name"
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(
                fixture_name, get_case_names(func_name, suffix_list))
