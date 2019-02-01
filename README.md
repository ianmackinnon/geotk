# geotk

Conversion tools for geometry file formats.


## `obj2svg`

Convert polygons in a Wavefront OBJ file to paths in SVG format.

OBJ polygon faces are converted to closed paths, compressed in the Z-axis.


### Usage

    ./obj2svg.py in.obj > out.svg
    ./obj2svg.py in.obj out.svg


## `svg2obj`

Convert paths in an SVG file to polygons in Wavefront OBJ format.

SVG paths are converted to OBJ polygon faces parallel to the Z-plane at the specified distance. Bézier curves are sampled at intervals.


## Caveats:

-   Only supports path commands `MmLlHhVvCcZz`.


## Usage:
    
    ./svg2obj.py in.svg > out.obj
    ./svg2obj.py in.svg out.obj


## `svg2gcode`

Convert paths in an SVG file to G-code for a Grbl-compatible CNC router.

SVG paths are converted to linear movements parallel to the Z-plane at the specified distance. Bézier curves are sampled at intervals.

A JSON configuration file in the following format is also required:

```
{
  "z-safety": <Z safety height in mm>,
  "z-mill": <maxiumum distance to mill, eg. the depth of the wasteboard, in mm>,
  "feedrate": <milling feedrate in mm/s>
}
```


## Caveats:

-   Only supports path commands `MmLlHhVvCcZz`.


## Usage:
    
    ./svg2gcode.py conf.json in.svg > out.gcode
    ./svg2gcode.py conf.json in.svg out.gcode
