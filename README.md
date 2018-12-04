# geotk

Conversion tools for geometry file formats.


## `svg2obj`

Convert SVG files to Wavefront OBJ format.

SVG paths are converted to OBJ polygon faces parallel to the Z-plane at the specified distance. Bézier curves are sampled at intervals.


## Caveats:

-   Only supports path commands `MmLlHhVvCcZz`.


## Usage:
    
    ./svg2obj.py in.svg > out.obj
    ./svg2obj.py in.svg out.obj
