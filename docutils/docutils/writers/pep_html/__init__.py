# $Id$
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
PEP HTML Writer.
"""

__docformat__ = 'reStructuredText'


import os
import os.path
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import html4css1


class Writer(html4css1.Writer):

    default_stylesheet = 'pep.css'

    default_stylesheet_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_stylesheet))

    default_template = 'template.txt'

    default_template_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_template))

    arguments_spec = html4css1.Writer.arguments_spec + (
        {"title": 'PEP/HTML Writer Options',
         "description": (
             "For the PEP/HTML writer, the default value for the "
             f'--stylesheet-path option is "{default_stylesheet_path}", and '
             f'the default value for --template is "{default_template_path}". '
             "See HTML Writer Options above."),
         "arguments": (
             {"flags": ("--python-home",),
              "help": "Python's home URL.  Default is 'https://www.python.org'",
              "dest": "python_home",
              "default": "http://www.python.org",
              "metavar": "<URL>"},
             {"flags": ("--pep-home",),
              "help": "Home URL prefix for PEPs.  Default is '.' (current directory).",
              "dest": "pep_home",
              "default": ".",
              "metavar": "<URL>"},
             # For testing.
             {"flags": ("--no-random",),
              "help": None,
              "dest": "no_random",
              "default": None,
              "action": "store_true"},
         )},
    )

    settings_default_overrides = {'stylesheet_path': default_stylesheet_path,
                                  'template': default_template_path,}

    relative_path_settings = ('template',)

    config_section = 'pep_html writer'
    config_section_dependencies = ('writers', 'html writers',
                                   'html4css1 writer')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

    def interpolation_dict(self):
        subs = html4css1.Writer.interpolation_dict(self)
        settings = self.document.settings
        pyhome = settings.python_home
        subs['pyhome'] = pyhome
        subs['pephome'] = settings.pep_home
        if pyhome == '..':
            subs['pepindex'] = '.'
        else:
            subs['pepindex'] = pyhome + '/dev/peps'
        index = self.document.first_child_matching_class(nodes.field_list)
        header = self.document[index]
        self.pepnum = header[0][1].astext()
        subs['pep'] = self.pepnum
        if settings.no_random:
            subs['banner'] = 0
        else:
            import random
            subs['banner'] = random.randrange(64)
        try:
            subs['pepnum'] = '%04i' % int(self.pepnum)
        except ValueError:
            subs['pepnum'] = self.pepnum
        self.title = header[1][1].astext()
        subs['title'] = self.title
        subs['body'] = ''.join(
            self.body_pre_docinfo + self.docinfo + self.body)
        return subs

    def assemble_parts(self):
        html4css1.Writer.assemble_parts(self)
        self.parts['title'] = [self.title]
        self.parts['pepnum'] = self.pepnum


class HTMLTranslator(html4css1.HTMLTranslator):

    def depart_field_list(self, node):
        html4css1.HTMLTranslator.depart_field_list(self, node)
        if 'rfc2822' in node['classes']:
            self.body.append('<hr />\n')
