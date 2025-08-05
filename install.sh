#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if command -v libtbx.python >/dev/null 2>&1; then
    exec libtbx.python "${SCRIPT_DIR}/install.py"
else
    exec python "${SCRIPT_DIR}/install.py"
fi
