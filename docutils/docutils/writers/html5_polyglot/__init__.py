# $Id$
# :Author: Günter Milde <milde@users.sf.net>
#          Based on the html4css1 writer by David Goodger.
# :Maintainer: docutils-develop@lists.sourceforge.net
# :Copyright: © 2005, 2009, 2015 Günter Milde,
#             portions from html4css1 © David Goodger.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: https://opensource.org/licenses/BSD-2-Clause

# Use "best practice" as recommended by the W3C:
# http://www.w3.org/2009/cheatsheet/

"""
Plain HyperText Markup Language document tree Writer.

The output conforms to the `HTML 5` specification.

The cascading style sheet "minimal.css" is required for proper viewing,
the style sheet "plain.css" improves reading experience.
"""
__docformat__ = 'reStructuredText'

import mimetypes
import os.path

import docutils
from docutils import frontend, nodes, writers, io
from docutils.transforms import writer_aux
from docutils.writers import _html_base

class Writer(writers._html_base.Writer):

    supported = ('html', 'html5', 'xhtml')
    """Formats this writer supports."""

    default_stylesheets = ['minimal.css', 'plain.css']
    default_stylesheet_dirs = ['.', os.path.abspath(os.path.dirname(__file__))]
    default_template = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'template.txt')

    settings_spec = frontend.filter_settings_spec(
        writers._html_base.Writer.settings_spec,
        # update specs with changed defaults or help string
        template =
         ('Template file. (UTF-8 encoded, default: "%s")' % default_template,
          ['--template'],
          {'default': default_template, 'metavar': '<file>'}),
        stylesheet_path =
         ('Comma separated list of stylesheet paths. '
          'Relative paths are expanded if a matching file is found in '
          'the --stylesheet-dirs. With --link-stylesheet, '
          'the path is rewritten relative to the output HTML file. '
          '(default: "%s")' % ','.join(default_stylesheets),
          ['--stylesheet-path'],
          {'metavar': '<file[,file,...]>', 'overrides': 'stylesheet',
           'validator': frontend.validate_comma_separated_list,
           'default': default_stylesheets}),
       stylesheet_dirs =
         ('Comma-separated list of directories where stylesheets are found. '
          'Used by --stylesheet-path when expanding relative path arguments. '
          '(default: "%s")' % ','.join(default_stylesheet_dirs),
          ['--stylesheet-dirs'],
          {'metavar': '<dir[,dir,...]>',
           'validator': frontend.validate_comma_separated_list,
           'default': default_stylesheet_dirs}),
       initial_header_level =
         ('Specify the initial header level. Does not affect document '
          'title & subtitle (see --no-doc-title). (default: 2 for "<h2>")',
          ['--initial-header-level'],
          {'choices': '1 2 3 4 5 6'.split(), 'default': '2',
           'metavar': '<level>'}),
       no_xml_declaration =
         ('Omit the XML declaration.',
          ['--no-xml-declaration'],
          {'dest': 'xml_declaration', 'action': 'store_false'}),
        )
    settings_spec = settings_spec + (
        'HTML5 Writer Options',
        '',
        ((frontend.SUPPRESS_HELP, # Obsoleted by "--image-loading"
          ['--embed-images'],
          {'action': 'store_true',
           'validator': frontend.validate_boolean}),
         (frontend.SUPPRESS_HELP, # Obsoleted by "--image-loading"
          ['--link-images'],
          {'dest': 'embed_images', 'action': 'store_false'}),
         ('Suggest at which point images should be loaded: '
          '"embed", "link" (default), or "lazy".',
          ['--image-loading'],
          {'choices': ('embed', 'link', 'lazy'),
           # 'default': 'link' # default set in _html_base.py
          }),
         ('Append a self-link to section headings.',
          ['--section-self-link'],
          {'default': 0, 'action': 'store_true'}),
         ('Do not append a self-link to section headings. (default)',
          ['--no-section-self-link'],
          {'dest': 'section_self_link', 'action': 'store_false'}),
        ))

    config_section = 'html5 writer'

    def __init__(self):
        self.parts = {}
        self.translator_class = HTMLTranslator


class HTMLTranslator(writers._html_base.HTMLTranslator):
    """
    This writer generates `polyglot markup`: HTML5 that is also valid XML.

    Safe subclassing: when overriding, treat ``visit_*`` and ``depart_*``
    methods as a unit to prevent breaks due to internal changes. See the
    docstring of docutils.writers._html_base.HTMLTranslator for details
    and examples.
    """

    # meta tag to fix rendering in mobile browsers
    viewport = ('<meta name="viewport" '
                'content="width=device-width, initial-scale=1" />\n')

    # <acronym> tag obsolete in HTML5. Use the <abbr> tag instead.
    def visit_acronym(self, node):
        # @@@ implementation incomplete ("title" attribute)
        self.body.append(self.starttag(node, 'abbr', ''))

    def depart_acronym(self, node):
        self.body.append('</abbr>')

    # no standard meta tag name in HTML5, use separate "author" meta tags
    # https://www.w3.org/TR/html5/document-metadata.html#standard-metadata-names
    def visit_authors(self, node):
        self.visit_docinfo_item(node, 'authors', meta=False)
        for subnode in node:
            self.add_meta('<meta name="author" content="%s" />\n' %
                          self.attval(subnode.astext()))

    def depart_authors(self, node):
        self.depart_docinfo_item()

    # use the <figcaption> semantic tag.
    def visit_caption(self, node):
        if isinstance(node.parent, nodes.figure):
            self.body.append('<figcaption>\n')
        self.body.append(self.starttag(node, 'p', ''))

    def depart_caption(self, node):
        self.body.append('</p>\n')
        # <figcaption> is closed in depart_figure(), as legend may follow.

    # use HTML block-level tags if matching class value found
    supported_block_tags = {'ins', 'del'}
    def visit_container(self, node):
        # If there is exactly one of the "supported block tags" in
        # the list of class values, use it as tag name:
        classes = node['classes']
        tags = [cls for cls in classes
                if cls in self.supported_block_tags]
        if len(tags) == 1:
            node.html5tagname = tags[0]
            classes.remove(tags[0])
        else:
            node.html5tagname = 'div'
        self.body.append(self.starttag(node, node.html5tagname,
                                       CLASS='docutils container'))

    def depart_container(self, node):
        self.body.append('</%s>\n' % node.html5tagname)


    # no standard meta tag name in HTML5, use dcterms.rights
    # see https://wiki.whatwg.org/wiki/MetaExtensions
    def visit_copyright(self, node):
        self.visit_docinfo_item(node, 'copyright', meta=False)
        self.add_meta('<meta name="dcterms.rights" content="%s" />\n'
                      % self.attval(node.astext()))

    def depart_copyright(self, node):
        self.depart_docinfo_item()

    # no standard meta tag name in HTML5, use dcterms.date
    def visit_date(self, node):
        self.visit_docinfo_item(node, 'date', meta=False)
        self.add_meta('<meta name="dcterms.date" content="%s" />\n'
                      % self.attval(node.astext()))

    def depart_date(self, node):
        self.depart_docinfo_item()

    def visit_document(self, node):
        title = (node.get('title', '') or os.path.basename(node['source'])
                 or 'untitled Docutils document')
        self.head.append('<title>%s</title>\n' % self.encode(title))

    def depart_document(self, node):
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template %
                                 {'lang': self.settings.language_code}])
        self.html_prolog.append(self.doctype)
        self.meta.insert(0, self.viewport)
        self.head.insert(0, self.viewport)
        self.meta.insert(0, self.content_type % self.settings.output_encoding)
        self.head.insert(0, self.content_type % self.settings.output_encoding)
        if 'name="dcterms.' in ''.join(self.meta):
            self.head.append(
             '<link rel="schema.dcterms" href="http://purl.org/dc/terms/"/>')
        if self.math_header:
            if self.math_output == 'mathjax':
                self.head.extend(self.math_header)
            else:
                self.stylesheet.extend(self.math_header)
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.body_prefix.append(self.starttag(node, 'main'))
        self.body_suffix.insert(0, '</main>\n')
        self.fragment.extend(self.body) # self.fragment is the "naked" body
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        assert not self.context, 'len(context) = %s' % len(self.context)

    # use new HTML5 <figure> and <figcaption> elements
    def visit_figure(self, node):
        atts = {}
        if node.get('width'):
            atts['style'] = 'width: %s' % node['width']
        if node.get('align'):
            atts['class'] = "align-" + node['align']
        self.body.append(self.starttag(node, 'figure', **atts))

    def depart_figure(self, node):
        if len(node) > 1:
            self.body.append('</figcaption>\n')
        self.body.append('</figure>\n')

    # use HTML5 <footer> element
    def visit_footer(self, node):
        self.context.append(len(self.body))

    def depart_footer(self, node):
        start = self.context.pop()
        footer = [self.starttag(node, 'footer')]
        footer.extend(self.body[start:])
        footer.append('\n</footer>\n')
        self.footer.extend(footer)
        self.body_suffix[:0] = footer
        del self.body[start:]

    # use HTML5 <header> element
    def visit_header(self, node):
        self.context.append(len(self.body))

    def depart_header(self, node):
        start = self.context.pop()
        header = [self.starttag(node, 'header')]
        header.extend(self.body[start:])
        header.append('</header>\n')
        self.body_prefix.extend(header)
        self.header.extend(header)
        del self.body[start:]

    # MIME types supported by the HTML5 <video> element
    videotypes = ('video/mp4', 'video/webm', 'video/ogg')

    def visit_image(self, node):
        atts = {}
        uri = node['uri']
        mimetype = mimetypes.guess_type(uri)[0]
        if mimetype not in self.videotypes:
            return super().visit_image(node)
        # image size
        if 'width' in node:
            atts['width'] = node['width'].replace('px', '')
        if 'height' in node:
            atts['height'] = node['height'].replace('px', '')
        if 'align' in node:
            atts['class'] = 'align-%s' % node['align']
        if 'controls' in node['classes']:
            atts['controls'] = 'controls'
        atts['title'] = node.get('alt', uri)
        if getattr(self.settings, 'image_loading', None) == 'lazy':
            atts['loading'] = 'lazy'
        # No newline in inline context or if surrounded by <a>...</a>.
        if (isinstance(node.parent, nodes.TextElement) or
            (isinstance(node.parent, nodes.reference) and
             not isinstance(node.parent.parent, nodes.TextElement))):
            suffix = ''
        else:
            suffix = '\n'
        self.body.append('%s<a href="%s">%s</a>%s</video>%s'
            % (self.starttag(node, 'video', suffix, src=uri, **atts),
               uri, node.get('alt', uri), suffix, suffix))

    def depart_image(self, node):
        pass

    # use HTML text-level tags if matching class value found
    supported_inline_tags = {'code', 'kbd', 'dfn', 'samp', 'var',
                             'bdi', 'del', 'ins', 'mark', 'small',
                             'b', 'i', 'q', 's', 'u'}
    def visit_inline(self, node):
        # Use `supported_inline_tags` if found in class values
        classes = node['classes']
        tags = [cls for cls in self.supported_inline_tags
                if cls in classes]
        if len(tags):
            node.html5tagname = tags[0]
            classes.remove(tags[0])
        elif (classes == ['ln'] and isinstance(node.parent, nodes.literal_block)
            and 'code' in node.parent.get('classes')):
            if self.body[-1] == '<code>':
                del(self.body[-1])
            else:
                self.body.append('</code>')
            node.html5tagname = 'small'
        else:
            node.html5tagname = 'span'
        self.body.append(self.starttag(node, node.html5tagname, ''))

    def depart_inline(self, node):
        self.body.append('</%s>' % node.html5tagname)
        if (node.html5tagname == 'small' and node.get('classes') == ['ln']
            and isinstance(node.parent, nodes.literal_block)):
            self.body.append('<code data-lineno="%s">' % node.astext())
        del node.html5tagname

    # place inside HTML5 <figcaption> element (together with caption)
    def visit_legend(self, node):
        if not isinstance(node.parent[1], nodes.caption):
            self.body.append('<figcaption>\n')
        self.body.append(self.starttag(node, 'div', CLASS='legend'))

    def depart_legend(self, node):
        self.body.append('</div>\n')
        # <figcaption> closed in visit_figure()

    # use HTML text-level tags if matching class value found
    def visit_literal(self, node):
        classes = node['classes']
        tags = [cls for cls in self.supported_inline_tags
                if cls in classes]
        if len(tags):
            tagname = tags[0]
            classes.remove(tags[0])
        else:
            tagname = 'span'
        if tagname == 'code':
            self.body.append(self.starttag(node, 'code', ''))
            return
        self.body.append(
            self.starttag(node, tagname, '', CLASS='docutils literal'))
        text = node.astext()
        # remove hard line breaks (except if in a parsed-literal block)
        if not isinstance(node.parent, nodes.literal_block):
            text = text.replace('\n', ' ')
        # Protect text like ``--an-option`` and the regular expression
        # ``[+]?(\d+(\.\d*)?|\.\d+)`` from bad line wrapping
        for token in self.words_and_spaces.findall(text):
            if token.strip() and self.in_word_wrap_point.search(token):
                self.body.append('<span class="pre">%s</span>'
                                    % self.encode(token))
            else:
                self.body.append(self.encode(token))
        self.body.append('</%s>' % tagname)
        # Content already processed:
        raise nodes.SkipNode

    def depart_literal(self, node):
        # skipped unless literal element is from "code" role:
        self.body.append('</code>')

    # Meta tags: 'lang' attribute replaced by 'xml:lang' in XHTML 1.1
    # HTML5/polyglot recommends using both
    def visit_meta(self, node):
        if node.hasattr('lang'):
            node['xml:lang'] = node['lang']
        meta = self.emptytag(node, 'meta', **node.non_default_attributes())
        self.add_meta(meta)
    def depart_meta(self, node):
        pass

    # no standard meta tag name in HTML5
    def visit_organization(self, node):
        self.visit_docinfo_item(node, 'organization', meta=False)
    def depart_organization(self, node):
        self.depart_docinfo_item()

    # use the new HTML5 element <section>
    def visit_section(self, node):
        self.section_level += 1
        self.body.append(
            self.starttag(node, 'section'))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append('</section>\n')

    # use the new HTML5 element <aside>
    def visit_sidebar(self, node):
        self.body.append(
            self.starttag(node, 'aside', CLASS='sidebar'))
        self.in_sidebar = True

    def depart_sidebar(self, node):
        self.body.append('</aside>\n')
        self.in_sidebar = False

    # Use new HTML5 element <aside> or <nav>
    # Add class value to <body>, if there is a ToC in the document
    # (see responsive.css how this is used for a navigation sidebar).
    def visit_topic(self, node):
        atts = {'classes': ['topic']}
        if 'contents' in node['classes']:
            node.html_tagname = 'nav'
            del(atts['classes'])
            if isinstance(node.parent, nodes.document):
                atts['role'] = 'doc-toc'
                self.body_prefix[0] = '</head>\n<body class="with-toc">\n'
        elif 'abstract' in node['classes']:
            node.html_tagname = 'div'
            atts['role'] = 'doc-abstract'
        elif 'dedication' in node['classes']:
            node.html_tagname = 'div'
            atts['role'] = 'doc-dedication'
        else:
            node.html_tagname = 'aside'
        self.body.append(self.starttag(node, node.html_tagname, **atts))

    def depart_topic(self, node):
        self.body.append('</%s>\n'%node.html_tagname)
        del node.html_tagname

    # append self-link
    def section_title_tags(self, node):
        start_tag, close_tag = super().section_title_tags(node)
        ids = node.parent['ids']
        if (ids and getattr(self.settings, 'section_self_link', None)
            and not isinstance(node.parent, nodes.document)):
            self_link = ('<a class="self-link" title="link to this section"'
                        ' href="#%s"></a>' % ids[0])
            close_tag = close_tag.replace('</h', self_link + '</h')
        return start_tag, close_tag
