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
