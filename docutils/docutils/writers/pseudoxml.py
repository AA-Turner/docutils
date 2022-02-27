# $Id$
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Simple internal document tree Writer, writes indented pseudo-XML.
"""

__docformat__ = 'reStructuredText'


from docutils import writers, frontend


class Writer(writers.Writer):

    supported = ('pprint', 'pformat', 'pseudoxml')
    """Formats this writer supports."""

    arguments_spec = (
        {"title": '"Docutils pseudo-XML" Writer Options',
         "description": None,
         "arguments": (
             {"flags": ("--detailed",),
              "help": "Pretty-print <#text> nodes.",
              "dest": "detailed",
              "default": None,
              "action": "store_true"},
         )},
    )

    config_section = 'pseudoxml writer'
    config_section_dependencies = ('writers',)

    output = None
    """Final translated form of `document`."""

    def translate(self):
        self.output = self.document.pformat()

    def supports(self, format):
        """This writer supports all format-specific elements."""
        return True
