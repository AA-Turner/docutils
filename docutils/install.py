#!/usr/bin/env python3
# $Id$
# Copyright: This file has been placed in the public domain.

"""
This is a quick & dirty installation shortcut. It is equivalent to the
command::

    python -m pip install .

However, the shortcut lacks error checking and command-line option
processing.  If you need any kind of customisation or help, please use::

    python -m pip install --help
"""

from pathlib import Path
import subprocess
import sys

DEPRECATION = """\
Installing Docutils through "install.py" is deprecated. \
Use "python -m pip install ." instead. install.py will be removed in the next \
release."""

if __name__ == '__main__':
    print(DEPRECATION, file=sys.stderr)
    print(__doc__)
    subprocess.run([sys.executable, "-m", "pip", "install", Path(__file__, "..").resolve()])
    # print twice as the message will be hidden by pip's output.
    print(DEPRECATION, file=sys.stderr)
