import sys
import os
import tifffile
import numpy as np
import json
from dials.util.options import ArgumentParser, flatten_experiments
import libtbx.phil
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, shift

"""
Module to shift TIFF images by whole pixels in X and Y based on a JSON
per-image beam centre results file created by dials.search_beam_position

This module provides functions to split the wide pixels at the edge of each
Timepix chip in a quad into duplicated pixels of the normal width. The value
of pixels in the central cross are also set to a maximum value to allow
for masking. The main function processes TIFF images provided as command-line
arguments.

Usage:
    python shift_images.py imported.expt beam_positions=beam_positions.json
"""

# Define the master PHIL scope for this program.
phil_scope = libtbx.phil.parse(
    """
    input {
        beam_positions = beam_positions.json
            .type = path
            .help = "A JSON file containing a beam position per image"
                    "as output by dials.search_beam_position method=midpoint"
    }
    """
)


def calculate_shift(i, centres, axis):

    smoothed = gaussian_filter1d(centres, sigma=3)
    whole_pixel = np.rint(smoothed)
    plt.plot(i, centres, label="raw")
    plt.plot(i, smoothed, label="smoothed", color="red")
    plt.plot(i, whole_pixel, label="integer", color="green")
    plt.legend()
    plt.title(f"Beam centre along the {axis} axis")
    plt.savefig(f"shift_images_{axis}.png")
    plt.close()
    return whole_pixel


def main():
    """
    Main function to shift TIFF images to a common beam centre.
    """
    usage = "shift-images.py imported.expt beam_positions=beam_positions.json"
    parser = ArgumentParser(
        usage=usage,
        phil=phil_scope,
        read_experiments=True,
        read_reflections=False,
        check_format=False,
    )

    params, options = parser.parse_args(None)
    experiments = flatten_experiments(params.input.experiments)
    if len(experiments) != 1:
        sys.exit("Exactly one experiment list required.")

    if len(experiments[0].detector) != 1:
        sys.exit("Only a sigle panel detector is supported.")

    beam = experiments[0].beam
    panel = experiments[0].detector[0]
    iset = experiments[0].imageset

    try:
        with open(params.input.beam_positions, "r") as f:
            beam_positions = json.load(f)
    except Exception:
        sys.exit(f"Cannot load {params.input.beam_positions} as a beam position JSON")

    _, i, bc_fast, bc_slow = zip(*beam_positions)

    # Smooth out the beam centre drift and convert to integer shifts
    bc_fast = calculate_shift(i, bc_fast, "fast")
    bc_slow = calculate_shift(i, bc_slow, "slow")

    # Get current beam centre from the experiment
    bc = panel.get_ray_intersection_px(beam.get_s0())

    # Get shift from the current beam centre to the new beam centre
    shift_fast = (bc_fast - bc[0]).astype(int)
    shift_slow = (bc_slow - bc[1]).astype(int)

    for i in range(len(iset)):
        # Check if the file exists before processing
        input_path = iset.get_image_identifier(i)
        if not os.path.exists(input_path):
            print(f"\nSkipping '{input_path}': File not found.")
            continue

        try:
            print(f"\nProcessing '{input_path}'...")

            image = tifffile.imread(input_path)
            print(f"  -> Image loaded. Shape: {image.shape}, Data type: {image.dtype}")
            if image.shape != (516, 516):
                print(f"\nSkipping '{input_path}': Wrong shape.")
                continue

            image_shifted = shift(image, shift=(-shift_slow[i], -shift_fast[i]), cval=0)

            basename = os.path.basename(input_path)
            output_path = f"shifted_{basename}"
            tifffile.imwrite(output_path, image_shifted, software="expand-and-shift")
            print(f"  -> Shifted image successfully saved as '{output_path}'")

        except Exception as e:
            print(f"  -> An error occurred while processing '{input_path}': {e}")

    print("\nAll tasks complete. ✨")


if __name__ == "__main__":
    main()
