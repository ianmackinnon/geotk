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

import io
import os
import logging
import warnings
from pathlib import Path
from subprocess import Popen, PIPE
from collections import defaultdict, namedtuple



TEST_PATH = Path(__file__).parent.resolve()

TEST_CASE_PATTERNS = {
    "svg2gcode": {
        "required": ("conf.json", "svg", "gcode"),
    },
    "svg2obj": {
        "required": ("svg", "obj"),
    },
    "obj2svg": {
        "required": ("obj", "svg"),
    },
    "svg2kicad": {
        "required": ("svg", "src.kicad_pcb", "dst.kicad_pcb"),
        "remove": ("pro", ),
    },
    "kicad2svg": {
        "required": ("kicad_pcb", "svg"),
        "remove": ("pro", ),
    },
}


LOG = logging.getLogger("conftest")



class GenerateError(Exception):
    pass



def get_case_names(func_name, case):
    """
    Get file stems for test cases.
    Raise a warning if only some of the files for a test case are present,
    or if an unexpected file with the same name is found.
    """

    case_path = TEST_PATH / "cases" / func_name
    name_dict = defaultdict(set)

    suffix_required = set(case["required"])

    if case.get("remove", None):
        for base in case_path.iterdir():
            (stem, suffix) = str(base).split(".", 1)
            if suffix in case["remove"]:
                base.unlink()

    for base in case_path.iterdir():
        # Split on first dot, rather than splitting
        # before last dot like pathlib.
        (stem, suffix) = str(base).split(".", 1)
        if suffix not in case["required"]:
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
    suffix_list = TEST_CASE_PATTERNS[func_name]["required"]
    properties = [v.replace(".", "_") for v in suffix_list]
    values = [case_path / f"{case_name}.{v}" for v in suffix_list]
    return namedtuple(f"{func_name}Case", properties)(*values)



def pytest_generate_tests(metafunc):
    for func_name, case in TEST_CASE_PATTERNS.items():
        fixture_name = f"{func_name}_case_name"
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(
                fixture_name, get_case_names(func_name, case))



def proc_command(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode

    if out:
        LOG.error(out.decode("utf-8"))

    if err:
        LOG.error(err.decode("utf-8"))

    assert not out
    assert not err
    assert not status



def proc_diff(path1, path2):
    cmd = [
        "diff", "-q",
        path1,
        path2,
    ]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = process.communicate()
    status = process.returncode

    if out:
        LOG.error(out)

    if err:
        LOG.error(err)

    assert not out
    assert not err
    assert not status



def api_compare(known_path, f):
    with open(known_path) as fp:
        known_text = fp.read()

    out = io.StringIO()
    f(out)
    result_text = out.getvalue()

    assert result_text == known_text



def cli_compare(known_path, name, case, cmd):
    result_path = f"/tmp/geotk-test-{name}-{case}.obj"

    try:
        os.remove(result_path)
    except FileNotFoundError:
        pass

    proc_command([result_path if v == "__result_path__" else v for v in cmd])
    proc_diff(
        known_path,
        result_path,
    )
