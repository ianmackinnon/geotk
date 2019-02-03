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

-   Geometric shapes like circles and rectangles are not converted to paths.
-   Only supports path commands `MmLlHhVvCcAaZz`.
-   Arcs with different X and Y radii are simplied as straight lines.


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

-   Geometric shapes like circles and rectangles are not converted to paths.
-   Only supports path commands `MmLlHhVvCcAaZz`.
-   Arcs with different X and Y radii are simplied as straight lines.


## Usage:
    
    ./svg2gcode.py conf.json in.svg > out.gcode
    ./svg2gcode.py conf.json in.svg out.gcode


## `kicad2svg`

Extract traces from a KiCad PCB file as paths in an Inkscape-compatible SVG.

Each PCB layer is represented as a layer, and each net is represented as a sublayer.


## Caveats:

-   Does not read page size from KiCad file; always exports an A4 SVG.


## `svg2kicad`

Replace a net's traces in a KiCad PCB file with paths from an SVG.

Paths must be stored exactly two layers deep. The first layer should have a name that matches the target PCB layer and the sublayer should have a name that matches the target net number of the path.


## Caveats:

-   Geometric shapes like circles and rectangles are not converted to paths.
-   Only supports path commands `MmLlHhVvCcAaZz`.
-   Arcs with different X and Y radii are simplied as straight lines.




