import sys
import os
import tifffile
import numpy as np

"""
Module for processing TIFF images by duplicating specific pixels and setting a
central cross to a mask value.

This module provides functions to split the wide pixels at the edge of each
Timepix chip in a quad into duplicated pixels of the normal width. The value
of pixels in the central cross are also set to a maximum value to allow
for masking. The main function processes TIFF images provided as command-line
arguments.

Functions:
    duplicate_pixels(image_array): Duplicates specific columns and rows in a
        NumPy array.
    set_cross_to_mask(image_array): Sets the values of pixels in the central
        cross to a maximum value for masking.
    main(): Processes TIFF images provided as command-line arguments.

Usage:
    python split_wide_pixels.py <file1.tif> <file2.tif> ...
"""


def duplicate_pixels(image_array: np.ndarray) -> np.ndarray:
    """
    Duplicates specific columns and then rows in a NumPy array.

    The function first duplicates columns with original indices 0, 255, 256,
    and 511, resulting in a 512x516 array. It then duplicates the rows
    with the same original indices, resulting in a final 516x516 array.

    Args:
        image_array: The input 2D NumPy array, expected to be 512x512.

    Returns:
        The modified 2D NumPy array with a shape of 516x516.
    """
    if image_array.shape != (512, 512):
        raise ValueError("Input array must be of size 512x512 for this operation.")

    # Define the indices to duplicate.
    # We process them in descending order to prevent insertions from
    # shifting the positions of subsequent indices we need to access.
    indices_to_duplicate = [511, 256, 255, 0]

    # --- Step 1: Duplicate Columns ---
    processed_array = image_array
    for col_idx in indices_to_duplicate:
        # Extract the column to be duplicated
        column_to_add = processed_array[:, col_idx]
        # Insert the column immediately after the original
        processed_array = np.insert(
            arr=processed_array,
            obj=col_idx + 1,
            values=column_to_add,
            axis=1,  # axis=1 for column operations
        )

    # --- Step 2: Duplicate Rows ---
    for row_idx in indices_to_duplicate:
        # Extract the row to be duplicated
        row_to_add = processed_array[row_idx, :]
        # Insert the row immediately after the original
        processed_array = np.insert(
            arr=processed_array,
            obj=row_idx + 1,
            values=row_to_add,
            axis=0,  # axis=0 for row operations
        )

    return processed_array


def set_cross_to_mask(image_array: np.ndarray) -> np.ndarray:
    """
    Sets the values of pixels in the central cross to maximum value, for masking

    The function takes a 516x516 array and sets the values of the four
    pixel wide central cross to the
    Args:
        image_array: The input 2D NumPy array

    Returns:
        The modified 2D NumPy with central cross pixels set to the array
        type's maximum value.
    """

    if image_array.shape != (516, 516):
        raise ValueError("Input array must be of size 516x516 for this operation.")

    max_val = np.iinfo(image_array.dtype).max

    image_array[256:260, :] = max_val
    image_array[:, 256:260] = max_val

    return image_array


def main():
    """
    Main function to process TIFF images provided as command-line arguments.
    """
    # Get the list of file paths from command-line arguments
    input_files = sys.argv[1:]

    # Check if any files were provided
    if not input_files:
        print("Error: No input files provided.")
        print("Usage: split-wide-pixels.py <file1.tif> <file2.tif> ...")
        sys.exit(1)

    print(f"Found {len(input_files)} image(s) to process. 🚀")

    for input_path in input_files:
        # Check if the file exists before processing
        if not os.path.exists(input_path):
            print(f"\nSkipping '{input_path}': File not found.")
            continue

        try:
            print(f"\nProcessing '{input_path}'...")

            # 1. Load the TIFF image into a NumPy array
            image = tifffile.imread(input_path)
            print(f"  -> Image loaded. Shape: {image.shape}, Data type: {image.dtype}")
            if image.shape != (512, 512):
                print(f"\nSkipping '{input_path}': Wrong shape.")
                continue

            # 2. Perform the operations on the image
            modified_image = duplicate_pixels(image)
            modified_image = set_cross_to_mask(modified_image)

            # 3. Construct the output filename
            basename = os.path.basename(input_path)
            output_path = f"expanded_{basename}"

            # 4. Write the modified NumPy array to a new TIFF file
            tifffile.imwrite(output_path, modified_image, software="expand-and-shift")
            print(f"  -> Modified image successfully saved as '{output_path}'")

        except Exception as e:
            print(f"  -> An error occurred while processing '{input_path}': {e}")

    print("\nAll tasks complete. ✨")


if __name__ == "__main__":
    main()
