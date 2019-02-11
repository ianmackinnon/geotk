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

from geotk.common import format_float
from geotk.svg import svg2paths



LOG = logging.getLogger("svg2gcode")



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

    assert conf["z-mill"] is not None
    assert conf["z-safety"] is not None

    z_layer_depth = conf.get("z-layer-depth", None)
    z_material = conf.get("z-material", None)
    material_depth = 0

    if z_material is None:
        z_material = conf["z-mill"]

    material_depth = conf["z-mill"] - z_material
    material_sign = sign(material_depth)
    material_depth = abs(material_depth)

    if z_layer_depth is None:
        z_layer_depth = material_depth

    write_gcode(out, {
        "G90": None
    })
    write_gcode(out, {
        "F": conf['feedrate']
    })
    write_gcode(out, {
        "G0": None,
        "Z": conf['z-safety']
    })

    layer_depth = 0
    while True:
        layer_depth += z_layer_depth

        LOG.info("zm %s", z_material)
        LOG.info("layer depth %s", layer_depth)
        LOG.info("material depth %s", material_depth)

        cut_depth = min(material_depth, layer_depth)
        target_depth = z_material + material_sign * cut_depth

        LOG.info("cut depth %s", cut_depth)
        LOG.info("target depth %s", target_depth)

        for path in paths:
            if not path:
                continue

            write_gcode(out, {
                "G0": None,
                "X": path[0][0],
                "Y": path[0][1],
            })
            write_gcode(out, {
                "G1": None,
                "Z": target_depth,
            })

            for vertex in path[1:]:
                write_gcode(out, {
                    "G1": None,
                    "X": vertex[0],
                    "Y": vertex[1],
                })

            write_gcode(out, {
                "G1": None,
                "Z": conf['z-safety'],
            })

        if not layer_depth < material_depth:
            break



def svg2gcode(
        out, svg_file, conf,
        step_dist=None, step_angle=None
):
    """
    Write paths in GCODE format.

    out:  Stream object to write to.

    Use millimeters for output unit.
    """

    paths = svg2paths(
        svg_file,
        step_dist=step_dist, step_angle=step_angle
    )
    write_paths_gcode(out, paths, conf)
