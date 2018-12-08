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
import sys
import warnings
from collections import defaultdict



TEST_PATH = os.path.abspath(os.path.dirname(__file__))



class GenerateError(Exception):
    pass



def blah():
    return 5



def get_case_names(test_name, src_ext, dst_ext):
    case_path = os.path.join(TEST_PATH, "cases", test_name)
    name_dict = defaultdict(set)
    for base in os.listdir(case_path):
        name, ext = base.split(".", 1)
        print(name, ext)
        if ext not in {src_ext, dst_ext}:
            warnings.warn(
                "File '%s' with unexpected extension '%s' in test case directory '%s'" % (
                    base, ext, case_path))
        name_dict[name].add(ext)

    name_list = []
    for name, ext_set in name_dict.items():
        if len(ext_set) != 2:
            warnings.warn(
                "Ignoring solitary file '%s.%s' in test case directory '%s'" % (
                    name, ext_set.pop(), case_path))
            continue
        name_list.append(name)
    return sorted(name_list)



def pytest_generate_tests(metafunc):
    if "svg2obj_test_name" in metafunc.fixturenames:
        name_list = get_case_names("svg2obj", "svg", "obj")
        metafunc.parametrize("svg2obj_test_name", name_list)
    if "obj2svg_test_name" in metafunc.fixturenames:
        name_list = get_case_names("obj2svg", "obj", "svg")
        metafunc.parametrize("obj2svg_test_name", ["cone"])
