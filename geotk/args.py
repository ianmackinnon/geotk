#!/usr/bin/env python3

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

import argparse

from geotk.version import __version__



def base_parser():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "--verbose", "-v",
        action="count", default=0,
        help="Print verbose information for debugging.")
    parser.add_argument(
        "--quiet", "-q",
        action="count", default=0,
        help="Suppress warnings.")

    parser.add_argument(
        "--version", "-V",
        action="version",
        version=__version__)

    return parser



def svg_input_parser():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "--minimum-step", "-M",
        action="store",
        type=float,
        help="Minimum segment dist for linearization of curved paths.")
    parser.add_argument(
        "--angle-step", "-A",
        action="store",
        type=float,
        help="Target segment angle for linearization of curved paths.")
    parser.add_argument(
        "--distance-step", "-D",
        action="store",
        type=float,
        help="Target segment distance for linearization of curved paths.")

    return parser
