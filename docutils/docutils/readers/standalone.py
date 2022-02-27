# $Id$
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Standalone file Reader for the reStructuredText markup syntax.
"""

__docformat__ = 'reStructuredText'


from docutils import frontend, readers
from docutils.transforms import frontmatter, references, misc


class Reader(readers.Reader):

    supported = ('standalone',)
    """Contexts this reader supports."""

    document = None
    """A single document tree."""

    arguments_spec = (
        {"title": "Standalone Reader Options",
         "description": None,
         "arguments": (
             {"flags": ("--no-doc-title",),
              "help": "Disable the promotion of a lone top-level section title "
                      "to document title (and subsequent section title to "
                      "document subtitle promotion; enabled by default).",
              "dest": "doctitle_xform",
              "default": True,
              "action": "store_true"},
             {"flags": ("--no-doc-info",),
              "help": "Disable the bibliographic field list transform (enabled "
                      "by default).",
              "dest": "docinfo_xform",
              "default": True,
              "action": "store_false"},
             {"flags": ("--section-subtitles",),
              "help": "Activate the promotion of lone subsection titles to "
                      "section subtitles (disabled by default).",
              "dest": "sectsubtitle_xform",
              "default": False,
              "action": frontend._BooleanOptionalAction},
         )},
    )

    config_section = 'standalone reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        return readers.Reader.get_transforms(self) + [
            references.Substitutions,
            references.PropagateTargets,
            frontmatter.DocTitle,
            frontmatter.SectionSubTitle,
            frontmatter.DocInfo,
            references.AnonymousHyperlinks,
            references.IndirectHyperlinks,
            references.Footnotes,
            references.ExternalTargets,
            references.InternalTargets,
            references.DanglingReferences,
            misc.Transitions,
            ]
