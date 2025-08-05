"""Install script for the package that performs various additional setup tasks,
allowing install on release builds of DIALS and installing a format class
plugin."""

import os
import sys
import subprocess
import shutil


def write_dispatchers():
    """Write dispatchers for the command line tools if they are not available,
    such as after pip install into a release build of DIALS."""

    bin_dir = os.path.dirname(shutil.which("dials.version"))
    this_dir = os.path.dirname(os.path.abspath(__file__))

    conda_base_bin = os.path.dirname(sys.executable)

    for file_name in ["shift-images", "split-wide-pixels"]:
        shutil.copy(os.path.join(conda_base_bin, file_name), bin_dir)
        with open(os.path.join(bin_dir, file_name), "r") as f:
            lines = f.readlines()
        with open(os.path.join(bin_dir, file_name), "w") as f:
            lines[0] = f"#!/usr/bin/env libtbx.python\n"
            f.writelines(lines)

    return


if __name__ == "__main__":

    # Current Python interpreter
    print(sys.executable)

    this_dir = os.path.dirname(os.path.abspath(__file__))

    # pip install package
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", this_dir, "--force-reinstall"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {e}")
        sys.exit(1)

    # check if the entry points are set up correctly - if not, we're probably in
    # a release build, so rewrite them
    if not shutil.which("shift-images") or not shutil.which("split-wide-pixels"):
        write_dispatchers()

    # install the format class plugin
    try:
        subprocess.run(
            [
                "dxtbx.install_format",
                "-u",
                os.path.join(
                    this_dir, "src", "expand_and_shift", "FormatTIFFgeneric.py"
                ),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing format class plugin: {e}")
        sys.exit(1)
