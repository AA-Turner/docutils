#! /usr/bin/env python3
# $Id$
# Author: engelbert gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

import os
from pathlib import Path
import string
import sys
import unittest

if __name__ == '__main__':
    # prepend the "docutils root" to the Python library path
    # so we import the local `docutils` package.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from docutils.core import publish_string
from docutils.writers import latex2e

# DATA_ROOT is ./test/data from the docutils root
DATA_ROOT = Path(__file__).resolve().parents[1] / 'data'

ham = os.path.relpath(DATA_ROOT/'ham.tex').replace('\\', '/')
spam = os.path.relpath(DATA_ROOT/'spam').replace('\\', '/')
# workaround for PyPy (cf. https://sourceforge.net/p/docutils/bugs/471/)
if sys.implementation.name == "pypy" and sys.version_info < (3, 10):
    spampath = f"PosixPath('{spam}.sty')"
else:
    spampath = f"'{spam}.sty'"


class WriterPublishTestCase(unittest.TestCase):

    maxDiff = None
    settings = {
        '_disable_config': True,
        'strict_visitor': True,
        'output_encoding': 'unicode',
        # avoid latex writer future warnings:
        'use_latex_citations': False,
        'legacy_column_widths': True,
        }

    def test_publish(self):
        for name, (settings_overrides, cases) in samples.items():
            for casenum, (rst_input, expected) in enumerate(cases):
                with self.subTest(id=f'samples[{name!r}][{casenum}]'):
                    output = publish_string(
                        source=rst_input,
                        writer=latex2e.Writer(),
                        settings_overrides=self.settings|settings_overrides)
                    self.assertEqual(expected, output)


head_template = string.Template(
r"""$head_prefix% generated by Docutils <https://docutils.sourceforge.io/>
\usepackage{cmap} % fix search and cut-and-paste in Acrobat
$requirements
%%% Custom LaTeX preamble
$latex_preamble
%%% User specified packages and stylesheets
$stylesheet
%%% Fallback definitions for Docutils-specific commands
$fallbacks$pdfsetup
%%% Body
\begin{document}
$titledata""")

parts = {
'head_prefix': r"""\documentclass[a4paper]{article}
""",
'requirements': r"""\usepackage[T1]{fontenc}
""",
'latex_preamble': r"""% PDF Standard Fonts
\usepackage{mathptmx} % Times
\usepackage[scaled=.90]{helvet}
\usepackage{courier}
""",
'longtable': r"""\usepackage{longtable,ltcaption,array}
\setlength{\extrarowheight}{2pt}
\newlength{\DUtablewidth} % internal use in tables
""",
'stylesheet': '',
'fallbacks': '',
'fallbacks_highlight': r"""
% basic code highlight:
\providecommand*\DUrolecomment[1]{\textcolor[rgb]{0.40,0.40,0.40}{#1}}
\providecommand*\DUroledeleted[1]{\textcolor[rgb]{0.40,0.40,0.40}{#1}}
\providecommand*\DUrolekeyword[1]{\textbf{#1}}
\providecommand*\DUrolestring[1]{\textit{#1}}

% custom inline roles: \DUrole{#1}{#2} tries \DUrole#1{#2}
\providecommand*{\DUrole}[2]{%
  \ifcsname DUrole#1\endcsname%
    \csname DUrole#1\endcsname{#2}%
  \else%
    #2%
  \fi%
}
""",
'pdfsetup': r"""
% hyperlinks:
\ifdefined\hypersetup
\else
  \usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
  \usepackage{bookmark}
  \urlstyle{same} % normal text font (alternatives: tt, rm, sf)
\fi
""",
'titledata': ''}

head = head_template.substitute(parts)

head_table = head_template.substitute(
    dict(parts, requirements=parts['requirements'] + parts['longtable']))

head_booktabs = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '\\usepackage{booktabs}\n' + parts['longtable']))

head_image = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '\\usepackage{graphicx}\n'))

head_minitoc = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '%% local table of contents\n'
           '\\usepackage{minitoc}\n'
           '\\dosecttoc\n'
           '\\mtcsetdepth{secttoc}{5}\n'
           '\\setcounter{secnumdepth}{0}\n'))

head_textcomp = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '\\usepackage{textcomp} % text symbol macros\n'))

head_alltt = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '\\usepackage{alltt}\n'))


samples = {}

samples['url_chars'] = ({}, [
["http://nowhere/url_with%28parens%29",
head + r"""
\url{http://nowhere/url_with\%28parens\%29}

\end{document}
"""],
])

samples['textcomp'] = ({}, [
["2 µm is just 2/1000000 m",
head_textcomp + r"""
2 \textmu{}m is just 2/1000000 m

\end{document}
"""],
])

samples['images'] = ({}, [
["""
.. image:: blue%20square.png
.. image:: vectors.svg
""",
head_image + r"""
\includegraphics{blue square.png}

\includegraphics{vectors.svg}

\end{document}
"""],
])

samples['svg-image'] = ({'stylesheet': 'svg'}, [
["""
.. image:: pixels.png
.. image:: vectors.svg
""",
head_template.substitute(dict(parts,
requirements=r"""\usepackage[T1]{fontenc}
\usepackage{graphicx}
""",
stylesheet=r"""\usepackage{svg}
""")) + r"""
\includegraphics{pixels.png}

\includesvg{vectors.svg}

\end{document}
"""],
])

samples['spanish_quote'] = ({}, [
[".. role:: language-es\n\nUnd damit :language-es:`basta`!",
head_template.substitute(dict(parts,
requirements=r"""\usepackage[T1]{fontenc}
\usepackage[spanish,main=english]{babel}
\AtBeginDocument{\shorthandoff{.<>}}
""")) + r"""
Und damit \foreignlanguage{spanish}{basta}!

\end{document}
"""],
])

samples['code_role'] = ({}, [
[':code:`x=1`',
head_template.substitute(dict(parts, requirements=parts['requirements']
                              + '\\usepackage{color}\n',
                              fallbacks=parts['fallbacks_highlight']))
+ r"""
\texttt{\DUrole{code}{x=1}}

\end{document}
"""],
])

samples['minitoc'] = ({}, [
# local toc reqires the minitoc package
# and either \tableofcontents or \faketableofcontents
["""\
section with local ToC
======================

.. contents::
   :local:

section not in local toc
========================
""",
head_minitoc + r"""

\section{section with local ToC%
  \label{section-with-local-toc}%
}

\phantomsection\label{contents}
\mtcsettitle{secttoc}{}
\secttoc


\section{section not in local toc%
  \label{section-not-in-local-toc}%
}

\faketableofcontents % for local ToCs

\end{document}
"""],
])

samples['table_of_contents'] = ({'use_latex_toc': False}, [
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
# expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n',
    fallbacks=r"""
% class handling for environments (block-level elements)
% \begin{DUclass}{spam} tries \DUCLASSspam and
% \end{DUclass}{spam} tries \endDUCLASSspam
\ifdefined\DUclass
\else % poor man's "provideenvironment"
  \newenvironment{DUclass}[1]%
    {% "#1" does not work in end-part of environment.
     \def\DocutilsClassFunctionName{DUCLASS#1}
     \csname \DocutilsClassFunctionName \endcsname}%
    {\csname end\DocutilsClassFunctionName \endcsname}%
\fi

% title for topics, admonitions, unsupported section levels, and sidebar
\providecommand*{\DUtitle}[1]{%
  \smallskip\noindent\textbf{#1}\smallskip}

\providecommand*{\DUCLASScontents}{%
  \renewenvironment{itemize}%
    {\begin{list}{}{\setlength{\partopsep}{0pt}
                    \setlength{\parsep}{0pt}}
                   }%
    {\end{list}}%
}
""")) + r"""
\phantomsection\label{table-of-contents}
\pdfbookmark[1]{Table of Contents}{table-of-contents}

\begin{DUclass}{contents}

\DUtitle{Table of Contents}

\begin{itemize}
\item \hyperref[title-1]{Title 1}

\begin{itemize}
\item \hyperref[title-2]{Title 2}
\end{itemize}
\end{itemize}
\end{DUclass}


\section{Title 1%
  \label{title-1}%
}

Paragraph 1.


\subsection{Title 2%
  \label{title-2}%
}

Paragraph 2.

\end{document}
"""],
])


samples['footnote_text'] = ({}, [
["""\
.. [1] paragraph

.. [2] 1. enumeration
""",
# expected output
head_template.substitute(dict(parts,
    fallbacks=r"""
% numerical or symbol footnotes with hyperlinks and backlinks
\providecommand*{\DUfootnotemark}[3]{%
  \raisebox{1em}{\hypertarget{#1}{}}%
  \hyperlink{#2}{\textsuperscript{#3}}%
}
\providecommand{\DUfootnotetext}[4]{%
  \begingroup%
  \renewcommand{\thefootnote}{%
    \protect\raisebox{1em}{\protect\hypertarget{#1}{}}%
    \protect\hyperlink{#2}{#3}}%
  \footnotetext{#4}%
  \endgroup%
}
""")) + r"""%
\DUfootnotetext{footnote-1}{footnote-1}{1}{%
paragraph
}
%
\DUfootnotetext{footnote-2}{footnote-2}{2}{
\begin{enumerate}
\item enumeration
\end{enumerate}
}

\end{document}
"""],
])

samples['no_sectnum'] = ({}, [
["""\
.. contents::

unnumbered section
------------------
""",
# expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents


\section{unnumbered section%
  \label{unnumbered-section}%
}

\end{document}
"""],
])

samples['sectnum'] = ({}, [
["""\
.. contents::
.. sectnum::

first section
-------------
""",
# expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents


\section{1~~~first section%
  \label{first-section}%
}

\end{document}
"""],
])

samples['depth'] = ({}, [
["""\
.. contents::
    :depth: 1

first section
-------------
""",
# expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\setcounter{tocdepth}{1}
\tableofcontents


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
])

samples['book'] = ({'documentclass': 'book'}, [
["""\
.. contents::
    :depth: 1

first chapter
-------------
""",
# expected output
head_template.substitute(dict(parts,
    head_prefix=r"""\documentclass[a4paper]{book}
""",
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\setcounter{tocdepth}{0}
\tableofcontents


\chapter{first chapter%
  \label{first-chapter}%
}

\end{document}
"""],
])


samples['no_sectnum'] = ({'use_latex_toc': False,
                          'sectnum_xform': False}, [
["""\
some text

first section
-------------
""",
# expected output
head_template.substitute(dict(parts, requirements=parts['requirements']
                              + '\\setcounter{secnumdepth}{0}\n')) + r"""
some text


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
])

samples['latex_sectnum'] = ({'use_latex_toc': False,
                             'sectnum_xform': False}, [
["""\
.. sectnum::

some text

first section
-------------
""",
# expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
some text


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
])


samples['latex_citations'] = ({'use_latex_citations': True}, [
["""\
Just a test citation [my_cite2006]_.

.. [my_cite2006]
   The underscore is mishandled.
""",
# expected output
head + r"""
Just a test citation \cite{my_cite2006}.

\begin{thebibliography}{my\_cite2006}
\bibitem[my\_cite2006]{my_cite2006}{
The underscore is mishandled.
}
\end{thebibliography}

\end{document}
"""],
["""\
Two non-citations: [MeYou2007]_[YouMe2007]_.

Need to be separated for grouping: [MeYou2007]_ [YouMe2007]_.

Two spaces (or anything else) for no grouping: [MeYou2007]_  [YouMe2007]_.

But a line break should work: [MeYou2007]_
[YouMe2007]_.

.. [MeYou2007] not.
.. [YouMe2007] important.
""",
# expected output
head + r"""
Two non-citations: {[}MeYou2007{]}\_{[}YouMe2007{]}\_.

Need to be separated for grouping: \cite{MeYou2007,YouMe2007}.

Two spaces (or anything else) for no grouping: \cite{MeYou2007}  \cite{YouMe2007}.

But a line break should work: \cite{MeYou2007,YouMe2007}.

\begin{thebibliography}{MeYou2007}
\bibitem[MeYou2007]{MeYou2007}{
not.
}
\bibitem[YouMe2007]{YouMe2007}{
important.
}
\end{thebibliography}

\end{document}
"""],
])


samples['enumerated_lists'] = ({}, [
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
head + r"""
\begin{enumerate}
\item Item 1.

\item Second to the previous item this one will explain
\end{enumerate}

\begin{quote}
\begin{enumerate}
\renewcommand{\labelenumi}{\alph{enumi})}
\item nothing.

\item or some other.
\end{enumerate}
\end{quote}

\begin{enumerate}
\setcounter{enumi}{2}
\item Third is
\end{enumerate}

\begin{quote}
\begin{enumerate}
\renewcommand{\labelenumi}{(\Roman{enumi})}
\item having pre and postfixes

\item in roman numerals.
\end{enumerate}
\end{quote}

\end{document}
"""],
])

# TODO: need to test for quote replacing if the language uses "ASCII-quotes"
# as active character (e.g. de (ngerman)).


samples['tables'] = ({}, [
["""\
.. table:: Foo

   +-----+-----+
   |     |     |
   +-----+-----+
   |     |     |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}%
\begin{longtable}{|p{0.075\DUtablewidth}|p{0.075\DUtablewidth}|}
\caption{Foo}\\
\hline
 &  \\
\hline
 &  \\
\hline
\end{longtable}

\end{document}
"""],
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{p{0.075\\DUtablewidth}p{0.075\\DUtablewidth}}

1
 & \n\
2
 \\\\

3
 & \n\
4
 \\\\
\\end{longtable*}

\\end{document}
"""],
["""\
.. table::
   :class: booktabs

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{p{0.075\\DUtablewidth}p{0.028\\DUtablewidth}}
\\toprule

1
 & \n\
2
 \\\\
\\bottomrule
\\end{longtable*}

\\end{document}
"""],
["""\
.. table::
   :class: colwidths-auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_table + r"""
\begin{longtable*}{|l|l|}
\hline
1 & 2 \\
\hline
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_table + r"""
\begin{longtable*}{|l|l|}
\hline
1 & 2 \\
\hline
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{|p{0.191\\DUtablewidth}|p{0.365\\DUtablewidth}|}
\\hline

1
 & \n\
2
 \\\\
\\hline
\\end{longtable*}

\\end{document}
"""],
])


samples['booktabs'] = ({'table_style': ['booktabs']}, [
# borderless overrides "booktabs" table_style
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{p{0.075\\DUtablewidth}p{0.075\\DUtablewidth}}

1
 & \n\
2
 \\\\

3
 & \n\
4
 \\\\
\\end{longtable*}

\\end{document}
"""],
["""\
.. table::
   :widths: auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + r"""
\begin{longtable*}{ll}
\toprule
1 & 2 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_booktabs + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{p{0.191\\DUtablewidth}p{0.365\\DUtablewidth}}
\\toprule

1
 & \n\
2
 \\\\
\\bottomrule
\\end{longtable*}

\\end{document}
"""],
])


samples['colwidths_auto'] = ({'table_style': ['colwidths-auto']}, [
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + r"""
\begin{longtable*}{ll}
1 & 2 \\
3 & 4 \\
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :class: booktabs

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + r"""
\begin{longtable*}{ll}
\toprule
1 & 2 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
# given width overrides "colwidth-auto"
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{|p{0.191\\DUtablewidth}|p{0.365\\DUtablewidth}|}
\\hline

1
 & \n\
2
 \\\\
\\hline
\\end{longtable*}

\\end{document}
"""],
])

samples['table_align'] = ({}, [
["""\
.. table::
   :align: right

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}[r]{|p{0.075\\DUtablewidth}|p{0.075\\DUtablewidth}|}
\\hline

1
 & \n\
2
 \\\\
\\hline
\\end{longtable*}

\\end{document}
"""],
])

samples['table_empty_cells'] = ({}, [
["""\
===== ======
Title
===== ======
entry value1
===== ======
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{|p{0.075\\DUtablewidth}|p{0.086\\DUtablewidth}|}
\\hline
\\textbf{%
Title
} &  \\\\
\\hline
\\endfirsthead
\\hline
\\textbf{%
Title
} &  \\\\
\\hline
\\endhead
\\multicolumn{2}{p{0.16\\DUtablewidth}}{\\raggedleft\\ldots continued on next page}\\\\
\\endfoot
\\endlastfoot

entry
 & \n\
value1
 \\\\
\\hline
\\end{longtable*}

\\end{document}
"""],
["""\
+----+----+
| c3 | c4 |
+----+----+
|         |
+---------+
""",
head_table + """
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{|p{0.063\\DUtablewidth}|p{0.063\\DUtablewidth}|}
\\hline

c3
 & \n\
c4
 \\\\
\\hline
\\multicolumn{2}{|p{0.13\\DUtablewidth}|}{} \\\\
\\hline
\\end{longtable*}

\\end{document}
"""],
])

samples['table_nonstandard_class'] = ({}, [
["""\
.. table::
   :class: my-class

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_template.substitute(
    dict(
        parts,
        requirements=parts['requirements'] + parts['longtable'],
        fallbacks=r"""
% class handling for environments (block-level elements)
% \begin{DUclass}{spam} tries \DUCLASSspam and
% \end{DUclass}{spam} tries \endDUCLASSspam
\ifdefined\DUclass
\else % poor man's "provideenvironment"
  \newenvironment{DUclass}[1]%
    {% "#1" does not work in end-part of environment.
     \def\DocutilsClassFunctionName{DUCLASS#1}
     \csname \DocutilsClassFunctionName \endcsname}%
    {\csname end\DocutilsClassFunctionName \endcsname}%
\fi
"""
    )
) + """
\\begin{DUclass}{my-class}
\\setlength{\\DUtablewidth}{\\linewidth}%
\\begin{longtable*}{|p{0.075\\DUtablewidth}|p{0.075\\DUtablewidth}|}
\\hline

1
 & \n\
2
 \\\\
\\hline

3
 & \n\
4
 \\\\
\\hline
\\end{longtable*}
\\end{DUclass}

\\end{document}
"""],
])

# The "[" needs to be protected (otherwise it will be seen as an
# option to "\\", "\item", etc. ).
samples['bracket_protection'] = ({}, [
["""
* [no option] to this item
""",
head + r"""
\begin{itemize}
\item {[}no option{]} to this item
\end{itemize}

\end{document}
"""],
])

samples['literal_block'] = ({}, [
["""\
Test special characters { [ \\\\ ] } in literal block::

  { [ ( \\macro

  } ] )
""",
head_alltt + r"""
Test special characters \{ {[} \textbackslash{} {]} \} in literal block:

\begin{quote}
\begin{alltt}
\{ [ ( \textbackslash{}macro

\} ] )
\end{alltt}
\end{quote}

\end{document}
"""],
])

samples['raw'] = ({}, [
[r""".. raw:: latex

   $E=mc^2$

A paragraph.

.. |sub| raw:: latex

   (some raw text)

Foo |sub|
same paragraph.
""",
head + r"""
$E=mc^2$

A paragraph.

Foo (some raw text)
same paragraph.

\end{document}
"""],
[r""".. compound::

  Compound paragraph

  .. raw:: LaTeX

     raw LaTeX block

  compound paragraph continuation.
""",
head_template.substitute(
    dict(parts,
         fallbacks=r"""
% class handling for environments (block-level elements)
% \begin{DUclass}{spam} tries \DUCLASSspam and
% \end{DUclass}{spam} tries \endDUCLASSspam
\ifdefined\DUclass
\else % poor man's "provideenvironment"
  \newenvironment{DUclass}[1]%
    {% "#1" does not work in end-part of environment.
     \def\DocutilsClassFunctionName{DUCLASS#1}
     \csname \DocutilsClassFunctionName \endcsname}%
    {\csname end\DocutilsClassFunctionName \endcsname}%
\fi
""")
) + r"""
\begin{DUclass}{compound}
Compound paragraph
raw LaTeX block
compound paragraph continuation.
\end{DUclass}

\end{document}
"""],
])

samples['title_with_inline_markup'] = ({}, [
["""\
This is the *Title*
===================

This is the *Subtitle*
----------------------

This is a *section title*
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the *document*.
""",
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n',
    fallbacks=r"""
% subtitle (in document title)
\providecommand*{\DUdocumentsubtitle}[1]{{\large #1}}
""",
    pdfsetup=parts['pdfsetup'] + r"""\hypersetup{
  pdftitle={This is the Title},
}
""", titledata=r"""\title{This is the \emph{Title}%
  \label{this-is-the-title}%
  \\%
  \DUdocumentsubtitle{This is the \emph{Subtitle}}%
  \label{this-is-the-subtitle}}
\author{}
\date{}
""")) + r"""\maketitle


\section{This is a \emph{section title}%
  \label{this-is-a-section-title}%
}

This is the \emph{document}.

\end{document}
"""],
])


samples['stylesheet_path'] = ({'stylesheet_path': f'{spam},{ham}'}, [
["""two stylesheet links in the header""",
head_template.substitute(dict(parts,
stylesheet=r"""\usepackage{%s}
\input{%s}
""" % (spam, ham))) + r"""
two stylesheet links in the header

\end{document}
"""],
])

samples['embed_stylesheet'] = ({'stylesheet_path': f'{spam},{ham}',
                                'embed_stylesheet': True,
                                'warning_stream': ''}, [
["""two stylesheets embedded in the header""",
head_template.substitute(dict(parts,
stylesheet=f"""\
% Cannot embed stylesheet:
%  [Errno 2] No such file or directory: {spampath}
% embedded stylesheet: {ham}
\\newcommand{{\\ham}}{{wonderful ham}}

""")) + r"""
two stylesheets embedded in the header

\end{document}
"""],
])

samples['bibtex'] = ({'use_bibtex': ['alpha', 'xampl']}, [
["""\
Just a test citation [book-full]_.
""",
head + r"""
Just a test citation \cite{book-full}.

\bibliographystyle{alpha}
\bibliography{xampl}

\end{document}
"""],
["""\
No bibliography if there is no citation.
""",
head + r"""
No bibliography if there is no citation.

\end{document}
"""],
])


if __name__ == '__main__':
    unittest.main()
