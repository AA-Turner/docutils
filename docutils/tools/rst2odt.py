#!/usr/bin/env python3

# $Id$
# Author: Dave Kuhlman <dkuhlman@rexx.com>
# Copyright: This module has been placed in the public domain.

"""
A front end to the Docutils Publisher, producing OpenOffice documents.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline_to_binary, default_description


description = ('Generates OpenDocument/OpenOffice/ODF documents from '
               'standalone reStructuredText sources.  ' + default_description)

publish_cmdline_to_binary(
    reader="odf_odt", writer="odf_odt",
    description='Generates OpenDocument/OpenOffice/ODF documents from '
                'standalone reStructuredText sources.  ' + default_description)
