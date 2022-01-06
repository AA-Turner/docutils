#!/usr/bin/env python3

# $Id$
# Author: Dave Kuhlman <dkuhlman@rexx.com>
# Copyright: This module has been placed in the public domain.

"""
Fix a word-processor-generated styles.odt for odtwriter use: Drop page size
specifications from styles.xml in STYLE_FILE.odt.
"""

# Author: Michael Schutte <michi@uiae.at>

from lxml import etree
import sys
import zipfile
from tempfile import mkstemp
import shutil
import os

try:
    from lxml import etree
except ImportError:
    raise ImportError(
        "The lxml is needed for rst2odt_prepstyles, but was not found. "
        "Install it with 'python -m pip install lxml'."
    )

NAMESPACES = {
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
}

ODT_PREP_STYLES_HELP = """Fix word-processor-generated STYLES.odt files.
Removes page size data from styles.xml in STYLES.odt, enabling odtwriter use.

Usage: %s STYLES.odt
""" % sys.argv[0]


def _odt_prep_style(filename):
    with zipfile.ZipFile(filename) as zin:
        root = etree.fromstring(zin.read("styles.xml"))
        for el in root.xpath("//style:page-layout-properties",
                             namespaces=NAMESPACES):
            for attr in el.attrib:
                if attr.startswith("{%s}" % NAMESPACES["fo"]):
                    del el.attrib[attr]
        styles_updated = etree.tostring(root)

        temp_file = tempfile.NamedTemporaryFile("w")
        with zipfile.ZipFile(temp_file, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "styles.xml":
                    zout.writestr(item, styles_updated)
                else:
                    zout.writestr(item, zin.read(item.filename))
    shutil.move(temp_file.name, filename)


if len(sys.argv[1:]) != 1 or args[0] in ('-h', '--help'):
    raise SystemExit(ODT_PREP_STYLES_HELP)
_odt_prep_style(sys.argv[1])
