# split_and_shift
Process TIFF images from a 512x512 Timepix or Medipix camera to handle wide pixels and shift to a consistent beam centre.

## Installation

After downloading the package, run the shell script `install.sh` within a terminal emulator that is set up with the DIALS environment. This requires a BASH interpreter, and has only been tested on Linux. This script will install the `split-and-shift` package, and a format class plugin that will allow DIALS to read the TIFF images produced by this package.

## Usage

This package is designed to work with 512×512 pixel TIFF images from a CheeTah M3 detector, consisting of a quad arrangement of Medipix sensors. Each Medipix sensor has an outer border of pixels that are twice as wide as a normal (55 micron) pixel. This is not corrected in the raw data, so there is a central cross of bright pixels (bright because they are wider than a normal pixel and therefore collect more electrons). This cross appears to be two pixels wide in the raw data, but in real space it should be 4 pixels wide.

The first job for this package is to split the wide pixels into two pixels each, so correcting the detector geometry, and then to mask these pixels from data processing. This is achieved using the `split-wide-pixels` command:

```
split-wide-pixels /path/to/data/*.tif
```

This script will write new images into the working directory with the prefix `split_`. We can now import these images into DIALS using the format class plugin installed by this package:

```
dials.import split_*.tif\
  distance=780\
  geometry.goniometer.axis=1,0,0\
  oscillation=0,0.3
```

Viewing the images using the command `dials.image_viewer imported.expt` shows the masked cross, now of size 4 pixels width:

<img width="531" height="531" alt="image-viewer" src="https://github.com/user-attachments/assets/6397b953-dcd4-4ede-a336-04b284de2243" />

The next job is to determine the beam centre that occurs during data collection. We will use `dials.search_beam_position` for that. These options have proved to work quite well for these images:

```
dials.search_beam_position imported.expt\
  method=midpoint\
  color_cutoff=5000\
  per_image=True\
  midpoint.convolution_width=2\
  dead_pixel_range_x=252,263\
  dead_pixel_range_y=252,263\
  plot=False
```

This command writes a file, `beam_positions.json`, containing the per-image beam centre calculations. We now use another script from this package to apply the beam centre shifts in order to align all images with the same beam centre:

```
shift-images imported.expt beam_positions=beam_positions.json
```

The result of this script is a new set of TIFF images, now with an additional prefix, `shifted_`. The program also creates a pair of plots to show the beam centre shift in fast (X) and slow (Y) directions.

<img width="640" height="480" alt="shift_images_fast" src="https://github.com/user-attachments/assets/e805707a-21d1-41aa-bf21-4d1853208038" />
<img width="640" height="480" alt="shift_images_slow" src="https://github.com/user-attachments/assets/603b0e9b-e630-497a-814c-7320cc9d34d3" />

The blue line on these plots shows the raw per-image beam centre calculation from `dials.search_beam_position`. We expect a gradual drift, so we smooth this line out to remove noise, producing the red line. Finally, we only want to shift images by whole pixels, so we then round the red line to the nearest integer shift, to produce the green plot. The values from the green line determine the shifts we will apply to each image to approximately align their beam centres.

We now import the new data set with DIALS:

```
dials.import shifted_expanded_*.tif\
  distance=780\
  geometry.goniometer.axis=1,0,0\
  oscillation=0,0.3
```

and we can continue processing from this point as normal.
