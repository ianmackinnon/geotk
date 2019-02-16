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

import jsonschema

from geotk.common import format_float
from geotk.svg import svg2paths



LOG = logging.getLogger("svg2gcode")

DEFAULTS = {
    "linearization-target-angle": 5,
}

CONF_SCHEMA = {
    "type": "object",
    "required": [
        "unit",
        "feedrate",
        "z-safety-direction",
        "z-safety-distance",
    ],
    "properties": {
        "unit": {
            "type": "string",
            "value": "mm",
        },
        "feedrate": {
            "type": "number",
            "minimum": 0,
            "exclusiveMinimum": True,
        },
        "linearization-target-angle": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
            "exclusiveMinimum": True,
        },
        "linearization-target-distance": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
            "exclusiveMinimum": True,
        },
        "z-safety-direction": {
            "type": "integer",
            "value": [
                -1,
                1
            ]
        },
        "z-base-coordinate": {
            "type": "number",
        },
        "x-offset": {
            "type": "number",
        },
        "y-offset": {
            "type": "number",
        },
        "z-safety-distance": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
        },
        "z-layer-depth": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
            "exclusiveMinimum": True,
        },
        "z-material-thickness": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
        },
        "z-mill-wasteboard-distance": {
            "type": [
                "number",
                "null",
            ],
            "minimum": 0,
        },
    }
}



def format_gcode(d):
    command = []
    for k, v in d.items():
        param = k
        if v is not None:
            param += format_float(v)
        command.append(param)
    return " ".join(command)



def write_gcode(out, d):
    out.write(format_gcode(d) + "\n")



def sign(v):
    if v < 0:
        return -1
    if v > 0:
        return 1
    return 0



def write_paths_gcode(out, paths, conf):
    """
    Vertex numbers start from 1.
    """

    jsonschema.validate(conf, CONF_SCHEMA)

    z_dir = conf.get("z-safety-direction", None)
    z_layer = conf.get("z-layer-depth", None)
    z_base = conf.get("z-base-coordinate", 0)
    z_thickness = (conf.get("z-material-thickness", 0) +
                   conf.get("z-mill-wasteboard-distance", 0))

    z_start = z_base + conf.get("z-material-thickness", 0) * z_dir
    z_safe = z_start + conf.get("z-safety-distance", 0) * z_dir

    x_offset = conf.get("x-offset", 0)
    y_offset = conf.get("y-offset", 0)

    write_gcode(out, {
        "G90": None
    })
    write_gcode(out, {
        "F": conf["feedrate"]
    })
    write_gcode(out, {
        "G0": None,
        "Z": z_safe
    })

    z_target = z_start
    max_depth = 0
    while True:
        if z_layer is not None:
            max_depth += z_layer
            z_target = z_start - min(z_thickness, max_depth) * z_dir

        for path in paths:
            if not path:
                continue


            for v, vertex in enumerate(path):
                if v == 1:
                    write_gcode(out, {
                        "G1": None,
                        "Z": z_target,
                    })

                cmd = "G1" if v else "G0"
                write_gcode(out, {
                    cmd: None,
                    "X": vertex[0] + x_offset,
                    "Y": vertex[1] + y_offset,
                })

            write_gcode(out, {
                "G1": None,
                "Z": z_safe,
            })

        if z_layer is None or max_depth >= z_thickness:
            break



def svg2gcode(
        out, svg_file, conf,
        step_dist=None, step_angle=None, step_min=None
):
    """
    Write paths in GCODE format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    if step_dist is None:
        step_dist = conf.get("linearization-target-angle", None)

    if step_angle is None:
        step_angle = conf.get("linearization-target-angle",
                              DEFAULTS["linearization-target-angle"])

    if step_min is None:
        step_min = conf.get("linearization-min-dist", None)

    paths = svg2paths(
        svg_file,
        step_dist=step_dist, step_angle=step_angle, step_min=step_min,
    )
    write_paths_gcode(out, paths, conf)
