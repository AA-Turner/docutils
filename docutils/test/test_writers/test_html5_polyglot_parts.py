#! /usr/bin/env python3

# $Id$
# Author: reggie dugard <reggie@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Test for fragment code in HTML writer.

Note: the 'body' and 'whole' entries have been removed from the parts
dictionaries (redundant), along with 'meta' and 'stylesheet' entries with
standard values, and any entries with empty values.
"""

from pathlib import Path
import sys
import unittest

if __name__ == '__main__':
    # prepend the "docutils root" to the Python library path
    # so we import the local `docutils` package.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import docutils
import docutils.core

# TEST_ROOT is ./test/ from the docutils root
TEST_ROOT = Path(__file__).parents[1]
DATA_ROOT = (TEST_ROOT / 'data').as_posix()

def test_sm():
    writer = 'html5'
    parts = docutils.core.publish_parts(
        source=sm_input,
        writer=writer,
        settings_overrides={
            '_disable_config': True,
            'strict_visitor': True,
            'stylesheet': '',
            'section_self_link': True,
            **sm_override,
        }
    )
    formatted = format_output(parts)
    assert len(formatted) == 1
    sm_output = formatted['fragment']
    assert sm_expected == sm_output


def test_nsm():
    writer = 'html5'
    parts = docutils.core.publish_parts(
        source=nsm_input,
        writer=writer,
        settings_overrides={
            '_disable_config': True,
            'strict_visitor': True,
            'stylesheet': '',
            'section_self_link': True,
            **nsm_override,
        }
    )
    formatted = format_output(parts)
    assert len(formatted) == 1
    nsm_output = formatted['fragment']
    assert nsm_expected == nsm_output


standard_content_type_template = '<meta charset="%s" />\n'
standard_generator_template = (
    '<meta name="generator"'
    f' content="Docutils {docutils.__version__}: '
    'https://docutils.sourceforge.io/" />\n')
standard_viewport_value = (
    '<meta name="viewport"'
    ' content="width=device-width, initial-scale=1" />\n')
standard_html_meta_value = (standard_content_type_template
                            + standard_generator_template
                            + standard_viewport_value)
standard_meta_value = standard_html_meta_value % 'utf-8'
standard_html_prolog = '<!DOCTYPE html>\n'
standard_html_body_template = '<main>\n%s</main>\n'

def format_output(parts):
    """Minimize & standardize the output."""
    # remove redundant parts & uninteresting parts:
    del parts['whole']
    assert parts['body'] == parts['fragment']
    del parts['body']
    del parts['body_pre_docinfo']
    del parts['body_prefix']
    del parts['body_suffix']
    del parts['head']
    del parts['head_prefix']
    del parts['encoding']
    del parts['errors']
    del parts['version']
    # remove standard portions:
    parts['meta'] = parts['meta'].replace(standard_meta_value, '')
    parts['html_head'] = parts['html_head'].replace(
        standard_html_meta_value, '...')
    parts['html_head'] = parts['html_head'].replace(
        '...<title>&lt;string&gt;</title>\n', '')
    parts['html_prolog'] = parts['html_prolog'].replace(
        standard_html_prolog, '')
    parts['html_body'] = parts['html_body'].replace(
        standard_html_body_template % parts['fragment'], '')
    # remove empty keys and return
    return {k: v for k, v in parts.items() if v}


opts = {
    'stylesheet_path': '',
    'embed_stylesheet': False,
    'math_output': 'mathml',
    'warning_stream': '',
}

totest = {}

sm_override = opts | {}
sm_input = f"""\
.. image:: {DATA_ROOT}/circle-broken.svg
   :loading: embed
"""
sm_expected = f"""\
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 10 10">
  <circle cx="5" cy="5" r="4" fill="lightblue" x/>
</svg>

<aside class="system-message">
<p class="system-message-title">System Message: ERROR/3 (<span class="docutils literal">&lt;string&gt;</span>, line 1)</p>
<p>Cannot parse SVG image &quot;{DATA_ROOT}/circle-broken.svg&quot;:
  not well-formed (invalid token): line 3, column 48</p>
</aside>
"""


nsm_override = opts | {'report_level': 4}
nsm_input = f"""\
.. image:: {DATA_ROOT}/circle-broken.svg
   :loading: embed
"""
nsm_expected = """\
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 10 10">
  <circle cx="5" cy="5" r="4" fill="lightblue" x/>
</svg>

"""
