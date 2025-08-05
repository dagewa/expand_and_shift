#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if command -v libtbx.python >/dev/null 2>&1; then
    exec libtbx.python "${SCRIPT_DIR}/install.py"
else
    # Check if plain "python" is a DIALS installation
    if python -c "from dials import util"; then
        exec python "${SCRIPT_DIR}/install.py"
    else
        echo "A DIALS installation is required."
        exit 1
    fi
fi
