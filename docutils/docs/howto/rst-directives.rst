.. include:: ../header.rst

=======================================
 Creating reStructuredText_ Directives
=======================================

:Authors: Dethe Elza, David Goodger, Lea Wiemann
:Contact: docutils-develop@lists.sourceforge.net
:Date: $Date$
:Revision: $Revision$
:Copyright: This document has been placed in the public domain.

.. _reStructuredText: https://docutils.sourceforge.io/rst.html


Directives are the primary extension mechanism of reStructuredText.
This document aims to make the creation of new directives as easy and
understandable as possible.  There are only a couple of
reStructuredText-specific features the developer needs to know to
create a basic directive.

The syntax of directives is detailed in the `reStructuredText Markup
Specification`_, and standard directives are described in
`reStructuredText Directives`_.

Directives are a reStructuredText markup/parser concept.  There is no
"directive" document tree element, no single element that corresponds
exactly to the concept of directives.  Instead, choose the most
appropriate elements from the existing Docutils elements.  Directives
build structures using the existing building blocks.  See `The
Docutils Document Tree`_ and the ``docutils.nodes`` module for more
about the building blocks of Docutils documents.

.. _reStructuredText Markup Specification:
   ../ref/rst/restructuredtext.html#directives
.. _reStructuredText Directives: ../ref/rst/directives.html
.. _The Docutils Document Tree: ../ref/doctree.html


.. contents:: Table of Contents


The Directive Class
===================

Directives are created by defining a directive class that inherits
from ``docutils.parsers.rst.Directive``::

    from docutils.parsers import rst

    class MyDirective(rst.Directive):

        ...

To understand how to implement the directive, let's have a look at the
docstring of the ``Directive`` base class::

    >>> from docutils.parsers import rst
    >>> print rst.Directive.__doc__

        Base class for reStructuredText directives.

        The following attributes may be set by subclasses.  They are
        interpreted by the directive parser (which runs the directive
        class):

        - `required_arguments`: The number of required arguments (default:
          0).

        - `optional_arguments`: The number of optional arguments (default:
          0).

        - `final_argument_whitespace`: A boolean, indicating if the final
          argument may contain whitespace (default: False).

        - `option_spec`: A dictionary, mapping known option names to
          conversion functions such as `int` or `float` (default: {}, no
          options).  Several conversion functions are defined in the
          directives/__init__.py module.

          Option conversion functions take a single parameter, the option
          argument (a string or ``None``), validate it and/or convert it
          to the appropriate form.  Conversion functions may raise
          `ValueError` and `TypeError` exceptions.

        - `has_content`: A boolean; True if content is allowed.  Client
          code must handle the case where content is required but not
          supplied (an empty content list will be supplied).

        Arguments are normally single whitespace-separated words.  The
        final argument may contain whitespace and/or newlines if
        `final_argument_whitespace` is True.

        If the form of the arguments is more complex, specify only one
        argument (either required or optional) and set
        `final_argument_whitespace` to True; the client code must do any
        context-sensitive parsing.

        When a directive implementation is being run, the directive class
        is instantiated, and the `run()` method is executed.  During
        instantiation, the following instance variables are set:

        - ``name`` is the directive type or name (string).

        - ``arguments`` is the list of positional arguments (strings).

        - ``options`` is a dictionary mapping option names (strings) to
          values (type depends on option conversion functions; see
          `option_spec` above).

        - ``content`` is a list of strings, the directive content line by line.

        - ``lineno`` is the line number of the first line of the directive.

        - ``content_offset`` is the line offset of the first line of the content from
          the beginning of the current input.  Used when initiating a nested parse.

        - ``block_text`` is a string containing the entire directive.

        - ``state`` is the state which called the directive function.

        - ``state_machine`` is the state machine which controls the state which called
          the directive function.

        Directive functions return a list of nodes which will be inserted
        into the document tree at the point where the directive was
        encountered.  This can be an empty list if there is nothing to
        insert.

        For ordinary directives, the list must contain body elements or
        structural elements.  Some directives are intended specifically
        for substitution definitions, and must return a list of `Text`
        nodes and/or inline elements (suitable for inline insertion, in
        place of the substitution reference).  Such directives must verify
        substitution definition context, typically using code like this::

            if not isinstance(state, states.SubstitutionDef):
                error = state_machine.reporter.error(
                    'Invalid context: the "%s" directive can only be used '
                    'within a substitution definition.' % (name),
                    nodes.literal_block(block_text, block_text), line=lineno)
                return [error]

    >>>


Option Conversion Functions
===========================

An option specification (``Directive.option_spec``) must be defined
detailing the options available to the directive.  An option spec is a
mapping of option name to conversion function; conversion functions
are applied to each option value to check validity and convert them to
the expected type.  Python's built-in conversion functions are often
usable for this, such as ``int``, ``float``.  Other useful conversion
functions are included in the ``docutils.parsers.rst.directives``
package (in the ``__init__.py`` module):

- ``flag``: For options with no option arguments.  Checks for an
  argument (raises ``ValueError`` if found), returns ``None`` for
  valid flag options.

- ``unchanged_required``: Returns the text argument, unchanged.
  Raises ``ValueError`` if no argument is found.

- ``unchanged``: Returns the text argument, unchanged.  Returns an
  empty string ("") if no argument is found.

- ``path``: Returns the path argument unwrapped (with newlines
  removed).  Raises ``ValueError`` if no argument is found.

- ``uri``: Returns the value (URI-reference) with whitespace removed.
  Raises ``ValueError`` if no argument is found.

- ``nonnegative_int``: Checks for a nonnegative integer argument,
  and raises ``ValueError`` if not.

- ``class_option``: Converts the argument into an ID-compatible
  string and returns it.  Raises ``ValueError`` if no argument is
  found.

- ``unicode_code``: Convert a Unicode character code to a Unicode
  character.

- ``single_char_or_unicode``: A single character is returned as-is.
  Unicode characters codes are converted as in ``unicode_code``.

- ``single_char_or_whitespace_or_unicode``: As with
  ``single_char_or_unicode``, but "tab" and "space" are also
  supported.

- ``positive_int``: Converts the argument into an integer.  Raises
  ValueError for negative, zero, or non-integer values.

- ``positive_int_list``: Converts a space- or comma-separated list
  of integers into a Python list of integers.  Raises ValueError for
  non-positive-integer values.

- ``encoding``: Verifies the encoding argument by lookup.  Raises
  ValueError for unknown encodings.

A further utility function, ``choice``, is supplied to enable
options whose argument must be a member of a finite set of possible
values.  A custom conversion function must be written to use it.
For example::

    from docutils.parsers.rst import directives

    def yesno(argument):
        return directives.choice(argument, ('yes', 'no'))

For example, here is an option spec for a directive which allows two
options, "name" and "value", each with an option argument::

    option_spec = {'name': unchanged, 'value': int}


Error Handling
==============

If your directive implementation encounters an error during
processing, you should call ``self.error()`` inside the ``run()``
method::

    if error_condition:
        raise self.error('Error message.')

The ``self.error()`` method will immediately raise an exception that
will be caught by the reStructuredText directive handler.  The
directive handler will then insert an error-level system message in
the document at the place where the directive occurred.

Instead of ``self.error``, you can also use ``self.severe`` and
``self.warning`` for more or less severe problems.

If you want to return a system message *and* document contents, you need to
create the system message yourself instead of using the ``self.error``
convenience method::

    def run(self):
        # Create node(s).
        node = nodes.paragraph(...)
        # Node list to return.
        node_list = [node]
        if error_condition:
             # Create system message.
             error = self.reporter.error(
                 'Error in "%s" directive: Your error message.' % self.name,
                 nodes.literal_block(block_text, block_text), line=lineno)
             node_list.append(error)
        return node_list


Register the Directive
======================

* If the directive is a general-use **addition to the Docutils core**,
  it must be registered with the parser and language mappings added:

  1. Register the new directive using its canonical name in
     ``docutils/parsers/rst/directives/__init__.py``, in the
     ``_directive_registry`` dictionary.  This allows the
     reStructuredText parser to find and use the directive.

  2. Add an entry to the ``directives`` dictionary in
     ``docutils/parsers/rst/languages/en.py`` for the directive, mapping
     the English name to the canonical name (both lowercase).  Usually
     the English name and the canonical name are the same.

  3. Update all the other language modules as well.  For languages in
     which you are proficient, please add translations.  For other
     languages, add the English directive name plus "(translation
     required)".

* If the directive is **application-specific**, use the
  ``register_directive`` function::

      from docutils.parsers.rst import directives
      directives.register_directive(directive_name, directive_class)


Examples
========

For the most direct and accurate information, "Use the Source, Luke!".
All standard directives are documented in `reStructuredText
Directives`_, and the source code implementing them is located in the
``docutils/parsers/rst/directives`` package.  The ``__init__.py``
module contains a mapping of directive name to module and function
name.  Several representative directives are described below.


Admonitions
-----------

`Admonition directives`__, such as "note" and "caution", are quite
simple.  They have no directive arguments or options.  Admonition
directive content is interpreted as ordinary reStructuredText.

__ ../ref/rst/directives.html#specific-admonitions

The resulting document tree for a simple reStructuredText line
"``.. note:: This is a note.``" looks as follows:

    <note>
        <paragraph>
            This is a note.

The directive class for the "note" directive simply derives from a
generic admonition directive class::

    class Note(BaseAdmonition):

        node_class = nodes.note

Note that the only thing distinguishing the various admonition
directives is the element (node class) generated.  In the code above,
the node class is set as a class attribute and is read by the
``run()`` method of ``BaseAdmonition``, where the actual processing
takes place::

    # Import Docutils document tree nodes module.
    from docutils import nodes
    # Import Directive base class.
    from docutils.parsers.rst import Directive

    class BaseAdmonition(Directive):

        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = True
        option_spec = {}
        has_content = True

        node_class = None
        """Subclasses must set this to the appropriate admonition node class."""

        def run(self):
            # Raise an error if the directive does not have contents.
            self.assert_has_content()
            text = '\n'.join(self.content)
            # Create the admonition node, to be populated by `nested_parse`.
            admonition_node = self.node_class(rawsource=text)
            # Parse the directive contents.
            self.state.nested_parse(self.content, self.content_offset,
                                    admonition_node)
            return [admonition_node]

Three things are noteworthy in the ``run()`` method above:

* The ``admonition_node = self.node_class(text)`` line creates the
  wrapper element, using the class set by the specific admonition
  subclasses (as in note, ``node_class = nodes.note``).

* The call to ``state.nested_parse()`` is what does the actual
  processing.  It parses the directive content and adds any generated
  elements as child elements of ``admonition_node``.

* If there was no directive content, the ``assert_has_content()``
  convenience method raises an error exception by calling
  ``self.error()`` (see `Error Handling`_ above).


"image"
-------

.. _image: ../ref/rst/directives.html#image

The "image_" directive is used to insert a picture into a document.
This directive has one argument, the path to the image file, and
supports several options.  There is no directive content.  Here's an
early version of the image directive class::

    # Import Docutils document tree nodes module.
    from docutils import nodes
    # Import ``directives`` module (contains conversion functions).
    from docutils.parsers.rst import directives
    # Import Directive base class.
    from docutils.parsers.rst import Directive

    def align(argument):
        """Conversion function for the "align" option."""
        return directives.choice(argument, ('left', 'center', 'right'))

    class Image(Directive):

        required_arguments = 1
        optional_arguments = 0
        final_argument_whitespace = True
        option_spec = {'alt': directives.unchanged,
                       'height': directives.nonnegative_int,
                       'width': directives.nonnegative_int,
                       'scale': directives.nonnegative_int,
                       'align': align,
                       }
        has_content = False

        def run(self):
            reference = directives.uri(self.arguments[0])
            self.options['uri'] = reference
            image_node = nodes.image(rawsource=self.block_text,
                                     **self.options)
            return [image_node]

Several things are noteworthy in the code above:

* The "image" directive requires a single argument, which is allowed
  to contain whitespace (``final_argument_whitespace = True``).  This
  is to allow for long URLs which may span multiple lines.  The first
  line of the ``run()`` method joins the URL, discarding any embedded
  whitespace.

* The reference is added to the ``options`` dictionary under the
  "uri" key; this becomes an attribute of the ``nodes.image`` element
  object.  Any other attributes have already been set explicitly in
  the reStructuredText source text.


The Pending Element
-------------------

Directives that cause actions to be performed *after* the complete
document tree has been generated can be implemented using a
``pending`` node.  The ``pending`` node causes a transform_ to be run
after the document has been parsed.

For an example usage of the ``pending`` node, see the implementation
of the ``contents`` directive in
docutils.parsers.rst.directives.parts__.

.. _transform: ../api/transforms.html
__ https://docutils.sourceforge.io/docutils/parsers/rst/directives/parts.py
