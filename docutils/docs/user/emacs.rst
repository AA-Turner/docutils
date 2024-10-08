.. -*- coding: utf-8 -*-

.. include:: ../header.rst

========================================
   Emacs Support for reStructuredText
========================================

:Authors: Stefan Merten <stefan@merten-home.de>, Martin Blais
          <blais@furius.ca>
:Version: ``rst.el`` V1.4.1
:Abstract:

    High-level description of the existing Emacs_ support for editing
    reStructuredText_ text documents. Suggested setup code and usage
    instructions are provided.

.. contents::

Introduction
============

reStructuredText_ is a syntax for simple text files that allows a
tool set - docutils_ - to extract generic document structure. For
people who use Emacs_, there is a package that adds a major mode that
supports editing the syntax of reStructuredText_: ``rst.el``. This
document describes the features it provides, and how to setup your
Emacs_ to use them and how to invoke them.

Installation
============

Emacs_ support for reStructuredText_ is implemented as an Emacs_ major
mode (``rst-mode``) provided by the ``rst.el`` Emacs_ package.

Emacs_ distributions contain ``rst.el`` since version V23.1. However,
a significantly updated version of ``rst.el`` is contained in Emacs_
V24.3. This document describes the version of ``rst.el`` contained in
Emacs_ V24.3 and later versions. This version of ``rst.el`` has the
internal version V1.4.1.

If you have Emacs_ V24.3 or later you do not need to install anything
to get reST support. If you have an Emacs_ between V23.1 and V24.2 you
may use the version of ``rst.el`` installed with Emacs_ or install a
more recent one locally_ (recommended). In other cases you need to
install ``rst.el`` locally_ to get reST support.

Checking situation
------------------

Here are some steps to check your situation:

#. In Emacs_ switch to an empty buffer and try ::

     M-x rst-mode

   If this works you have ``rst.el`` installed somewhere. You can see
   that it works if you find a string ``ReST`` in Emacs' modeline of
   the current buffer. If this doesn't work you need to install
   ``rst.el`` yourself locally_.

#. In the buffer you just switched to ``rst-mode`` try ::

     C-h v rst-version

   If this fails you have a version of ``rst.el`` older than
   V1.1.0. Either you have an old ``rst.el`` locally or you are using
   an Emacs_ between V23.1 and V24.2. In this case it is recommended
   that you install a more recent version of ``rst.el`` locally_.

   You may also try ::

     C-h v emacs-version

   to find out your Emacs_ version.

#. Check the version of ``rst.el``

   The content of ``rst-version`` gives you the internal version of
   ``rst.el``. The version contained in Emacs_ V24.3 and described here
   is V1.4.0. If you have an older version you may or may not install
   a more recent version of ``rst.el`` locally_.

.. _locally:

Local installation
------------------

If you decided to install locally please follow these steps.

#. Download ``rst.el``

   Download the most recent published version of ``rst.el`` from
   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/tools/editors/emacs/rst.el

#. Put ``rst.el`` to a directory in ``load-path``

   Use ::

     C-h v load-path

   If in the resulting list you find a directory in your home
   directory put ``rst.el`` in this directory.

   Make sure the directory is one of the first entries in
   ``load-path``. Otherwise a version of ``rst.el`` which came with
   Emacs_ may be found before your local version.

   In Emacs_ see the info node ``Init File Examples`` for more
   information on how to set up your Emacs_ initialization
   machinery. Try ::

     C-h i
     mEmacs<Return>
     sInit File Examples<Return>

#. Enable ``rst-mode``

   Add the following to your Emacs_ initialization setup ::

     (require 'rst)

   After you restarted Emacs_ ``rst.el`` is loaded and ready to be
   used.

Switching ``rst-mode`` on
-------------------------

By default ``rst-mode`` is switched on for files ending in ``.rst`` or
``.rest``. If in a buffer you want to switch ``rst-mode`` on manually
use ::

  M-x rst-mode

If you want to use ``rst-mode`` in files with other extensions modify
``auto-mode-alist`` to automatically turn it on whenever you visit
reStructuredText_ documents::

   (setq auto-mode-alist
         (append '(("\\.txt\\'" . rst-mode)
                   ("\\.rst\\'" . rst-mode)
                   ("\\.rest\\'" . rst-mode)) auto-mode-alist))

Put the extensions you want in the correct place in the example
above. Add more lines if needed.

If have local variables enabled (try ``C-h v enable-local-variables``
to find out), you can also add the following at the top of your
documents to trigger rst-mode::

   .. -*- mode: rst -*-

Or this at the end of your documents::

   ..
      Local Variables:
      mode: rst
      End:

Key bindings
============

``rst-mode`` automatically binds several keys for invoking special
functions for editing reStructuredText_. Since ``rst-mode`` contains a
lot of functionality most key bindings consist of three
keystrokes.

Following the Emacs_ conventions for major modes the key bindings of
``rst-mode`` start with ``C-c C-<letter>``. The second key stroke
selects a group of key bindings:

C-c C-a
  Commands to adjust the section headers and work with the hierarchy
  they build.

C-c C-c
  Commands to compile the current reStructuredText_ document to
  various output formats.

C-c C-l
  Commands to work with lists of various kinds.

C-c C-r
  Commands to manipulate the current region.

C-c C-t
  Commands to create and manipulate a table of contents.

At any stage of typing you may use ``C-h`` to get help on the
available key bindings. I.e. ``C-c C-h`` gives you help on all key
bindings while ``C-c C-r C-h`` gives you help on the commands for
regions. This is handy if you forgot a certain key binding.

Additional key bindings which have a certain meaning in other Emacs_
modes are reused in ``rst-mode`` so you don't have to learn a
different set of key bindings for editing reStructuredText_.

In ``rst-mode`` try ::

  C-h m

to list all mode specific key bindings. Most of the key bindings are
described in this tutorial.

.. note:: The key bindings have been completely revamped in ``rst.el``
          V1.0.0. This was necessary to make room for new
          functionality. Some of the old bindings still work but give
          a warning to use the new binding. In the output of ``C-h m``
          these bindings show up as ``rst-deprecated-...``. The old
          bindings will be removed completely in a later version.

Section Adornments
==================

``rst-mode`` recognizes the section adornments building the section
hierarchy of the document. Section adornments are the underlines or
under- and overlines used to mark a section title. There are a couple
of commands to work with section adornments. These commands are bound
to key bindings starting with ``C-c C-a``.

Adjusting a Section Title
-------------------------

There is a function that helps a great deal to maintain these
adornments: ``rst-adjust`` (bound to ``C-c C-a C-a``, ``C-c C-=``, and
``C-=``). This function is a Swiss army knife that can be invoked
repeatedly and whose behavior depends on context:

#. If there is an incomplete adornment, e.g. ::

      My Section Title
      ==

   invocation will complete the adornment. It can also be used to
   adjust the length of the existing adornment when you need to edit
   the title.

#. If there is no section adornment at all, by default an adornment of
   the same level as the last encountered section level is added. You
   can simply enter a few characters of the title and invoke the
   function to create the section adornment.

   The variable ``rst-new-adornment-down`` can be customized to create
   one level lower adornments than the previous section title instead
   of keeping the level.

#. If there is already a section adornment, it is promoted one level
   up. You can invoke it like this repeatedly to cycle the title
   through the hierarchy of existing adornments.

Invoking the function with a negative prefix argument, e.g. ``C--
C-=``, will effectively reverse the direction of adornment cycling.
To alternate between underline-only and over-and-under styles, you can
use a regular prefix argument, e.g. ``C-u C-=``. See the
documentation of ``rst-adjust`` for more description of the prefix
arguments to alter the behavior of the function.

Promoting and Demoting Many Sections
------------------------------------

When you are re-organizing the structure of a document, it can be
useful to change the level of a number of section titles. The same
key binding can be used to do that: if the region is active when the
binding is invoked, all the section titles that are within the region
are promoted accordingly (or demoted, with negative prefix argument).

Redoing All the Adornments to Your Taste
----------------------------------------

If you open someone else's file and the adornments it contains are
unfamiliar, you may want to readjust them to fit your own preferred
hierarchy of adornments. This can be difficult to perform by hand.
However, you can do this easily by invoking
``rst-straighten-adornments`` (``C-c C-a C-s``), which operates on the
entire buffer.

Customizations for Adornments
-----------------------------

You can customize the variable ``rst-preferred-adornments`` to a list
of the adornments that you like to use for documents.

If you prefer adornments according to
http://sphinx-doc.org/rest.html#sections you may customize it to end
up with a value like this::

  ((35 over-and-under 0) ; ?#
   (42 over-and-under 0) ; ?*
   (61 simple 0) ; ?=
   (45 simple 0) ; ?-
   (94 simple 0) ; ?^
   (34 simple 0)) ; ?"

This will become the default in a later version of ``rst.el``.

If you set ``rst-preferred-adornments`` to nil resembling the empty
list only the section adornment found in the buffer will be used.

Viewing the Hierarchy of Section Adornments
-------------------------------------------

You can visualize the hierarchy of the section adornments in the
current buffer by invoking ``rst-display-adornments-hierarchy``, bound
on ``C-c C-a C-d``. A temporary buffer will appear with fake section
titles rendered in the style of the current document. This can be
useful when editing other people's documents to find out which section
adornments correspond to which levels.

Movement and Selection
======================

Movement and Selection for Sections
-----------------------------------

You can move the cursor between the different section titles by using
the ``rst-backward-section`` (``C-M-a``) and ``rst-forward-section``
(``C-M-e``). To mark the section that cursor lies in, use
``rst-mark-section`` (``C-M-h``).

The key bindings are modeled after other modes with similar
functionality.

Movements and Selection for Text Blocks
---------------------------------------

The understanding of reStructuredText_ of ``rst-mode`` is used to set
all the variables influencing Emacs' understanding of paragraphs. Thus
all operations on paragraphs work as usual. For instance
``forward-paragraph`` (``M-}``) works as usual.

Indenting and Filling
=====================

Indentation of text plays a major role in the syntax of
reStructuredText_. It is tedious to maintain the indentation
manually. ``rst-mode`` understands most of the structure of
reStructuredText_ allowing for sophisticated indentation and filling
support described in this section.

Indenting Text Blocks
---------------------

``rst-mode`` supports indentation of text blocks by the command
``rst-shift-region`` (``C-c C-r TAB``). Mark a region and use ``C-c
C-r TAB`` to indent all blocks one tab to the right. Use ``M-- C-c C-r
TAB`` to indent the region one tab to the left.

You may use arbitrary prefix arguments such as ``M-2`` or ``M-- 2`` to
determine the number of tabs you want to indent. A prefix of ``M-0``
removes all indentation in the active region.

A tab is an indentation making sense for the block at hand in
reStructuredText_ syntax. In some cases the exact indentation depends
on personal taste. You may customize a couple of variables ``M-x
customize-group<RET> rst-indent<RET>`` to match your taste.

Indenting Lines While Typing
----------------------------

In Emacs_ the ``TAB`` key is often used for indenting the current
line. ``rst-mode`` implements this for the sophisticated indentation
rules of reStructuredText_. Pressing ``TAB`` cycles through the
possible tabs for the current line. In the same manner
``newline-and-indent`` (``C-j``) indents the new line properly.

This is very handy while writing lists. Consider this
reStructuredText_ bullet list with the cursor at ``@``::

  * Level 1

    * Level 2@

Type ``C-j`` twice to get this::

  * Level 1

    * Level 2

      @

Now you an enter text at this level, or start a new list item by
typing another ``*``. Or you may type ``TAB`` to reduce the
indentation once::

  * Level 1

    * Level 2

    @

Typing another ``TAB`` gets you to the first level::

  * Level 1

    * Level 2

  @

.. note:: Since Emacs_ V24.4 ``electric-indent-mode`` is globally on.
          This breaks indentation in ``rst-mode`` and renders
          ``rst-mode`` mostly useless. This is fixed in V1.4.1 of
          ``rst-mode``.

          A quick fix for older versions of ``rst.el`` is to add the
          following line at the end of the ``(define-derived-mode
          rst-mode ...`` block in your copy of ``rst.el``::

            (setq electric-indent-inhibit t)

          You may also install V1.4.1 or newer locally_.

Filling
-------

``rst-mode`` understanding the indentation rules of reStructuredText_
also supports filling paragraphs. Just use ``fill-paragraph``
(``M-q``) as you do in other modes.

Operating on Lists
==================

Lists are supported in various flavors in reStructuredText_.
``rst-mode`` understands reStructuredText_ lists and offers some
support for operating on lists. Key bindings for commands for
operating on lists start with ``C-c C-l``.

Please note that so far definition lists are not explicitly supported
by ``rst-mode``.

Bulleted and Enumerated Lists
-----------------------------

If you have a couple of plain lines you want to turn into an
enumerated list you can invoke ``rst-enumerate-region`` (``C-c C-l
C-e``). For example, the following region ::

  Apples

  Oranges

  Bananas

becomes ::

  1. Apples

  2. Oranges

  3. Bananas

``rst-bullet-list-region`` (``C-c C-l C-b``) does the same, but
results in a bullet list ::

  * Apples

  * Oranges

  * Bananas

By default, each paragraph starting on the leftmost line in the
highlighted region will be taken to be a single list or enumeration
item, for example, enumerating the following::

   An apple a day
   keeps the doctor away.

   But oranges
   are tastier than apples.

   If you preferred bananas
   you may be
   a monkey.

Will result in::

   1. An apple a day
      keeps the doctor away.

   2. But oranges
      are tastier than apples.

   3. If you preferred bananas
      you may be
      a monkey.

If you would like to enumerate each of the lines, use a prefix
argument on the preceding commands, e.g.::

  Apples
  Oranges
  Bananas

becomes::

  * Apples
  * Oranges
  * Bananas

Straightening Existing Bullet List Hierarchies
----------------------------------------------

If you invoke ``rst-straighten-bullets-region`` (``C-c C-l C-s``), the
existing bullets in the active region will be replaced to reflect
their respective level. This does not make a difference in the
document structure that reStructuredText_ defines, but looks better
in, for example, if all of the top-level bullet items use the
character ``-``, and all of the 2nd level items use ``*``, etc.

Inserting a List Item
---------------------

To start a new list you may invoke ``rst-insert-list`` (``C-c C-l
C-i``). You may choose from an item style supported by
reStructuredText_.

You may also invoke ``rst-insert-list`` at the end of a list item. In
this case it inserts a new line containing the markup for the a list
item on the same level.

Operating on Other Text Blocks
==============================

Creating and Removing Line Blocks
---------------------------------

To create line blocks, first select the region to convert and invoke
``rst-line-block-region`` ``C-c C-r C-l``. For example, the following
::

  Apples
  Oranges
  Bananas

becomes ::

  | Apples
  | Oranges
  | Bananas

This works even if the region is indented. To remove line blocks,
select a region and invoke with a prefix argument.

Commenting a Region of Text
---------------------------

``rst-mode`` understands reStructuredText_ comments. Use
``comment-dwim`` (``M-;``) to work on comments as usual::

  Apples
  Oranges
  Bananas

becomes::

  ..
     Apples
     Oranges
     Bananas

To remove a comment you have to tell this to ``comment-dwim``
explicitly by using a prefix argument (``C-u M-;``).

Please note that only indented comments are supported properly by the
parts of ``comment-dwim`` working on regions.

.. _Conversion:

Converting Documents from Emacs
===============================

``rst-mode`` provides a number of functions for running documents
being edited through the docutils tools. The key bindings for these
commands start with ``C-c C-c``.

The main generic function is ``rst-compile`` (``C-c C-c C-c``). It
invokes a compilation command with the correct output name for the
current buffer and then invokes Emacs' compile function. It also looks
for the presence of a ``docutils.conf`` configuration file in the
parent directories and adds it to the command line options. There is also
``rst-compile-alt-toolset`` (``C-c C-c C-a``) in case you often need
run your document in a second toolset.

You can customize the commands being used by setting
``rst-compile-primary-toolset`` and ``rst-compile-secondary-toolset``.

Other commands are available for other formats:

* ``rst-compile-pseudo-region`` (``C-c C-c C-x``)

  When crafting documents, it is often convenient to view which data
  structures docutils will parse them into. You can use to run the
  active region through ``rst2pseudoxml`` and have the output
  automatically be displayed in a new buffer.

* ``rst-compile-pdf-preview`` (``C-c C-c C-p``)

  Convert the current document to PDF and launch a viewer on the
  results.

* ``rst-compile-slides-preview`` (``C-c C-c C-s``): Convert the
  current document to S5 slides and view in a web browser.

Imenu Support
=============

Using Imenu
-----------

Emacs_ has a package called ``imenu``. ``rst-mode`` supports Imenu by
adding a function to convert the structure of a reStructuredText_
buffer to an Imenu index. Thus you can use invoke ``imenu`` (``M-x
imenu``) to navigate through the section index or invoke
``imenu-add-to-menubar`` (``M-x imenu-add-to-menubar``) to add an
Imenu menu entry to Emacs' menu bar.

Using which function
--------------------

As a side effect of Imenu support the ``which-func`` package is also
supported. Invoke ``which-function-mode`` (``M-x
which-function-mode``) to add the name of the current section to the
mode line. This is especially useful if you navigate through documents
with long sections which do not fit on a single screen.

Using the Table of Contents
===========================

The sections in a reStructuredText_ document can be used to form a
table of contents. ``rst-mode`` can work with such a table of contents
in various forms. Key bindings for these commands start with ``C-c
C-t``.

Navigating Using the Table of Contents
--------------------------------------

When you are editing long documents, it can be a bit difficult to
orient yourself in the structure of your text. To that effect, a
function is provided that presents a hierarchically indented table of
contents of the document in a temporary buffer, in which you can
navigate and press ``Return`` to go to a specific section.

Invoke ``rst-toc`` (``C-c C-t C-t``). It presents a temporary buffer
that looks something like this::

  Table of Contents:
  Debugging Meta-Techniques
    Introduction
    Debugging Solution Patterns
      Recognize That a Bug Exists
      Subdivide and Isolate
      Identify and Verify Assumptions
      Use a Tool for Introspection
      Change one thing at a time
      Learn about the System
    Understanding a bug
    The Basic Steps in Debugging
    Attitude
      Bad Feelings
      Good Feelings
    References

When you move the cursor to a section title and press ``RET`` or ``f``
or click with ``button1`` on a section title, the temporary buffer
disappears and you are left with the cursor positioned at the chosen
section. Clicking with ``button2`` jumps to the respective section but
keeps the toc buffer. You can use this to look at the various section
headers quickly. Use ``q`` in this buffer to just quit it without
moving the cursor in the original document. Use ``z`` to zap the
buffer altogether.

Inserting a Table of Contents
-----------------------------

Oftentimes in long text documents that are meant to be read directly,
a table of contents is inserted at the beginning of the text. In
reStructuredText_ documents, since the table of contents is
automatically generated by the parser with the ``.. contents::``
directive, people generally have not been adding an explicit table of
contents to their source documents, and partly because it is too much
trouble to edit and maintain.

The Emacs_ support for reStructuredText_ provides a function to insert
such a table of contents in your document. Since it is not meant to
be part of the document text, you should place such a table of
contents within a comment, so that it is ignored by the parser. This
is the favored usage::

  .. contents::
  ..
      1  Introduction
      2  Debugging Solution Patterns
        2.1  Recognize That a Bug Exists
        2.2  Subdivide and Isolate
        2.3  Identify and Verify Assumptions
        2.4  Use a Tool for Introspection
        2.5  Change one thing at a time
        2.6  Learn about the System
      3  Understanding a bug
      4  The Basic Steps in Debugging
      5  Attitude
        5.1  Bad Feelings
        5.2  Good Feelings
      6  References

Just place the cursor at the top-left corner where you want to insert
the TOC and invoke the function ``rst-toc-insert`` with ``C-c C-t
C-i``. The table of contents will display all the section titles that
are under the location where the insertion occurs. This way you can
insert local table of contents by placing them in the appropriate
location.

You can use a numeric prefix argument to limit the depth of rendering
of the TOC.

You can customize the look of the TOC by setting the values of the
following variables: ``rst-toc-indent``, ``rst-toc-insert-style``,
``rst-toc-insert-max-level``.

Maintaining the Table of Contents Up-to-date
--------------------------------------------

One issue is that you will probably want to maintain the inserted
table of contents up-to-date. ``rst-toc-update`` (``C-c C-t C-u``)
will automatically update an inserted table of contents following a
``.. contents::`` directive laid out like the example above.

Syntax Highlighting via Font-Lock
=================================

``rst-mode`` provides syntax highlighting for nearly all to
reStructuredText_ constructs.

Use ``customize-group rst-faces`` to customize the faces used for
font-locking.

Customization
=============

Some aspects of ``rst-mode`` can be configured through the
customization feature of Emacs_. Try ::

  M-x customize-group<RETURN>rst

for all customizations or use the respective menu entry. Those
customizations which are useful for many people are described in this
section.

Customizing Section Title Formatting
------------------------------------

For a couple of things the reStructuredText_ syntax offers a choice of
options on how to do things exactly. Some of these choices influence
the operation of ``rst.el`` and thus can be configured. The
customizations are contained in the ``rst-adjust`` group.

Among these things is the exact layout of section adornments. In fact
reStructuredText_ prescribes only the characters and how these
characters must be used but the exact use of concrete adornments may
be different in every source file. Using the customization option
``rst-preferred-adornments`` you can tell ``rst-mode`` on the exact
sequence of adornments you prefer to markup the different levels of
sections headers.

Finally the title text of over-and-under adornments may be indented in
reStructuredText_. ``rst-default-indent`` tells ``rst-mode`` how many
positions a over-and-under adornment should be indented when toggling
from simple adornment and in case a consistent indentation throughout
the whole buffer for such adornment is needed.

Customizing Indentation
-----------------------

reStructuredText_ uses indentation a lot to signify a certain meaning.
In some cases the exact amount of indentation is prescribed by the
syntax while in some cases the exact indentation is not fixed. The
customization group ``rst-indent`` allows to customize the amount of
indentation in these cases.

In field lists the content of a field needs to be indented relative to
the field label. ``rst-indent-field`` tells ``rst-mode`` the amount of
indentation to use for field content. A value of zero always indents
according to the content after the field label.

The indentation of literal blocks is controlled by
``rst-indent-literal-normal`` and ``rst-indent-literal-minimized``.
The first is used when the leading literal tag (``::``) appears alone
on a line. The second is used when the minimized style is used where
the literal tag follows some text.

The indentation of comments is controlled by ``rst-indent-comment``.
Of course this makes only sense for the indented comments of
reStructuredText_.

Customization option ``rst-indent-width`` gives the default
indentation when there are no other hints on what amount of
indentation to use.

Customizing Faces
-----------------

The faces used for font-locking can be defined in the ``rst-faces``
customization group. The customization options ending in ``-face`` are
only there for backward compatibility so please leave them as they
are.

reStructuredText_ sets no limit on the nesting of sections. By default
there are six levels of fontification defined. Section titles deeper
than six level have no special fontification - only the adornments are
fontified. The exact mapping from a level to a face is done by by
``rst-adornment-faces-alist``, however. So if you need fontification
deeper than six levels you may want to customize this option. You may
also want to customize it if you like the general idea of section
title fontification in ``rst-mode`` but for instance prefer a reversed
order.

Customizing Conversion
----------------------

Conversion_ can be customized by the customization options in the
customization group ``rst-compile``.

If some conversion does not work as expected please check
the variable ``rst-compile-toolsets`` ::

  M-x customize-option<RETURN>rst-compile-toolsets

This variable defines the commands and other details used for
conversion. In case of problems please check that the commands are
either available or customize them to what is available in your
environment.

.. note:: There are some options in V1.4.1 of ``rst.el`` which should
          be customization options but are not yet. Customization
          support will be added in a later version.

.. note:: Please note that there is a package ``rst2pdf`` based on the
          ReportLab library. Please note that the command of this
          package requires an additional ``-o`` for naming the output
          file. This breaks the usual conventions employed by Docutils
          tools. ``rst-mode`` V1.4.1 does not support this directly.

Other Customizations
--------------------

``rst-preferred-bullets`` can be customized to hold your preferred set
of bullets to use for bulleted lists.

``rst-mode-hook`` is a normal major mode hook which may be customized.
It is run if you enter ``rst-mode``.

Related aspects
===============

This section covers some general aspects using Emacs_ for editing
reStructuredText_ source. They are not directly related to
``rst-mode`` but may enhance your experience.

``text-mode`` Settings
----------------------

Consult the Emacs_ manual for more ``text-mode`` customizations. In
particular, you may be interested in setting the following variables,
functions and modes that pertain somewhat to ``text-mode``:

* ``indent-tabs-mode``
* ``colon-double-space``
* ``sentence-end-double-space``
* ``auto-fill-mode``
* ``auto-mode-alist``

Editing Tables: Emacs table mode
--------------------------------

You may want to check out `Emacs table mode`_ to create an edit
tables, it allows creating ASCII tables compatible with
reStructuredText_.

.. _Emacs table mode: http://table.sourceforge.net/

Character Processing
--------------------

Since reStructuredText punts on the issue of character processing,
here are some useful resources for Emacs_ users in the Unicode world:

* `xmlunicode.el and unichars.el from Norman Walsh
  <http://nwalsh.com/emacs/xmlchars/index.html>`__

* `An essay by Tim Bray, with example code
  <http://www.tbray.org/ongoing/When/200x/2003/09/27/UniEmacs>`__

* For Emacs_ users on Mac OS X, here are some useful useful additions
  to your .emacs file.

  - To get direct keyboard input of non-ASCII characters (like
    "option-e e" resulting in "é" [eacute]), first enable the option
    key by setting the command key as your meta key::

        (setq mac-command-key-is-meta t) ;; nil for option key

    Next, use one of these lines::

        (set-keyboard-coding-system 'mac-roman)
        (setq mac-keyboard-text-encoding kTextEncodingISOLatin1)

    I prefer the first line, because it enables non-Latin-1 characters
    as well (em-dash, curly quotes, etc.).

  - To enable the display of all characters in the Mac-Roman charset,
    first create a fontset listing the fonts to use for each range of
    characters using charsets that Emacs_ understands::

      (create-fontset-from-fontset-spec
       "-apple-monaco-medium-r-normal--10-*-*-*-*-*-fontset-monaco,
        ascii:-apple-monaco-medium-r-normal--10-100-75-75-m-100-mac-roman,
        latin-iso8859-1:-apple-monaco-medium-r-normal--10-100-75-75-m-100-mac-roman,
        mule-unicode-0100-24ff:-apple-monaco-medium-r-normal--10-100-75-75-m-100-mac-roman")

    Latin-1 doesn't cover characters like em-dash and curly quotes, so
    "mule-unicode-0100-24ff" is needed.

    Next, use that fontset::

        (set-frame-font "fontset-monaco")

  - To enable cooperation between the system clipboard and the Emacs_
    kill ring, add this line::

        (set-clipboard-coding-system 'mac-roman)

  Other useful resources are in `Andrew Choi's Emacs 21 for Mac OS X
  FAQ <http://members.shaw.ca/akochoi-emacs/stories/faq.html>`__.

Credits
=======

Part of the original code of ``rst.el`` has been written by Martin
Blais and David Goodger and Wei-Wei Guo. The font-locking came from
Stefan Merten.

Most of the code has been modified, enhanced and extended by Stefan
Merten who also is the current maintainer of ``rst.el``.

.. _Emacs: https://www.gnu.org/software/emacs/emacs.html
.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Docutils: https://docutils.sourceforge.io/

.. Emacs settings

   LocalWords:  reST utf Merten Blais rst el docutils modeline emacs
   LocalWords:  Init mEmacs sInit alist setq txt overlines RET nd py
   LocalWords:  dwim conf toolset pseudoxml pdf Imenu imenu menubar
   LocalWords:  func toc xmlunicode unichars eacute charset fontset
   LocalWords:  kTextEncodingISOLatin charsets monaco ascii latin
   LocalWords:  iso unicode Choi's Goodger Guo

   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   fill-column: 70
   End:
