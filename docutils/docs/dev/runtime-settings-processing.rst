.. include:: ../header.rst

=============================
 Runtime Settings Processing
=============================

:Author: David Goodger, Günter Milde
:Contact: docutils-develop@lists.sourceforge.net
:Date: $Date$
:Revision: $Revision$
:Copyright: This document has been placed in the public domain.

:Abstract: A detailled description of Docutil's settings processing
           framework.

.. contents::


The ``docutils/__init__.py``, ``docutils/core.py``, and
``docutils.frontend.py`` modules are described.
Following along with the actual code is recommended.

See `Docutils Runtime Settings`_ for a high-level description of the core
API and `Docutils Configuration`_ for a description of the individual
settings.

.. note::
   This document is informal.
   It describes the state in Docutils 0.18.1.
   Implementation details will change with the move to replace the
   deprecated optparse_ module with argparse_.


Settings priority
=================

Docutils overlays default and explicitly specified values from various
sources such that settings behave the way we want and expect them to
behave.

The souces are overlaid in the following order (later sources
overwrite earlier ones):

1. Defaults specified in `settings_spec`__ and
   `settings_defaults`__ attributes for each component_.
   (details__)

   __ ../api/runtime-settings.html#settingsspec-settings-spec
   __ ../api/runtime-settings.html#settingsspec-settings-defaults
   __ `OptionParser.populate_from_components()`_

2. Defaults specified in `settings_default_overrides`__ attribute for
   each component_.
   (details__)

   __ ../api/runtime-settings.html#settingsspec-settings-default-overrides
   __ component.settings_default_overrides_

3. Settings specified in the `"settings_overrides" argument`_ of the
   `Publisher convenience functions`_ rsp. the `settings_overrides`
   attribute of a `core.Publisher` instance.
   (details__)

   __ OptionParser.defaults_

4. If enabled, settings specified in `active sections`_ of the
   `configuration files`_ in the order described in
   `Configuration File Sections & Entries`_. (details__)

   See also `Configuration File Sections & Entries`_.

   __ `OptionParser.get_standard_config_settings()`_

5. If enabled, command line arguments (details__).

   __ `Publisher.process_command_line()`_


Settings assigned to the `"settings" argument`_ of the
`convenience functions`_ or the ``Publisher.settings`` attribute
are used **instead of** the above sources
(see below for details for `command-line tools`__ and
`other applications`__).

__ `publisher.publish()`_
__ `publisher.process_programmatic_settings()`_

.. _command-line tools:

Runtime settings processing for command-line tools
==================================================

The command-line `front-end tools`_ usually import and call
the Publisher convenience function `publish_cmdline()`_.

1. ``docutils.core.publish_cmdline()`` creates a `Publisher`_ instance::

       publisher = core.Publisher(…, settings)

   eventually sets the components_ from the respective names, and calls ::

       publisher.publish(argv, …, settings_spec,
                         settings_overrides, config_section, …)

   .. _publisher.publish():

2. If `publisher.settings` is None, ``publisher.publish()`` calls::

       publisher.process_command_line(…,
           settings_spec, config_section, **defaults)

   with `defaults` taken from `publisher.settings_overrides`.

   If `publisher.settings` is defined, steps 3 to 5 are skipped.

3. ``publisher.process_command_line()`` calls::

       optpar = publisher.setup_option_parser(…,
                    settings_spec, config_section, **defaults)

   .. _publisher.setup_option_parser():

4. ``publisher.setup_option_parser()``

   - merges the value of the `"config_section" argument`_ into
     `settings_spec` and

   - creates an `OptionParser` instance ::

        optpar = docutils.frontend.OptionParser(components, defaults)

     with `components` the tuple of the `SettingsSpec`_ instances
     ``(publisher.parser, publisher.reader, publisher.writer, settings_spec)``

   .. _OptionParser.populate_from_components():

5. The `OptionParser` instance prepends itself to the `components` tuple
   and calls ``self.populate_from_components(components)``, which updates
   the attribute ``self.defaults`` in two steps:

   a) For each component passed, ``component.settings_spec`` is processed
      and ``component.settings_defaults`` is applied.

      .. _component.settings_default_overrides:

   b) In a second loop, for each component
      ``component.settings_default_overrides`` is applied. This way,
      ``component.settings_default_overrides`` can override the default
      settings of any other component.

   .. _OptionParser.defaults:

6. Back in ``OptionParser.__init__()``, ``self.defaults`` is updated with
   the `defaults` argument passed to ``OptionParser(…)`` in step 5.

   This means that the `settings_overrides` argument of the
   `convenience functions`_ has priority over all
   ``SettingsSpec.settings_spec`` defaults.

   .. _OptionParser.get_standard_config_settings():

7. If configuration files are enabled,
   ``self.get_standard_config_settings()`` is called.

   This reads the Docutils `configuration files`_, and returns a
   dictionary of settings in `active sections`_ which is used to update
   ``optpar.defaults``. So configuration file settings have priority over
   all software-defined defaults.

   .. _Publisher.process_command_line():

8. ``publisher.process_command_line()`` calls ``optpar.parse_args()``.
   The OptionParser parses all command line options and returns a
   `docutils.frontend.Values` object.
   This is assigned to ``publisher.settings``.
   So command-line options have priority over configuration file
   settings.

9. The `<source>` and `<destination>` command-line arguments
   are also parsed, and assigned to ``publisher.settings._source``
   and ``publisher.settings._destination`` respectively.

10. ``publisher.publish()`` calls ``publisher.set_io()`` with no arguments.
    If either ``publisher.source`` or ``publisher.destination`` are not
    set, the corresponding ``publisher.set_source()`` and
    ``publisher.set_destination()`` are called:

    ``publisher.set_source()``
      checks for a ``source_path`` argument, and if there is none (which
      is the case for command-line use), it is taken from
      ``publisher.settings._source``.  ``publisher.source`` is set by
      instantiating a ``publisher.source_class`` object.
      For command-line front-end tools, the default
      ``publisher.source_class`` (i.e. ``docutils.io.FileInput``)
      is used.

    ``publisher.set_destination()``
      does the same job for the destination. (the default
      ``publisher.destination_class`` is ``docutils.io.FileOutput``).

    .. _accessing the runtime settings:

11. ``publisher.publish()`` passes ``publisher.settings`` to the reader_
    component's ``read()`` method.

12. The reader component creates a new `document root node`__.
    ``nodes.document.__init__()`` adds the settings to the internal
    attributes.

    __ ../ref/doctree.html#document

    All components acting on the Document Tree are handed the
    ``document`` root node and can access the runtime settings as
    ``document.settings``.


Runtime settings processing for other applications
==================================================

The `convenience functions`_ , ``core.publish_file()``,
``core.publish_string()``, or ``core.publish_parts()`` do not parse the
command line for settings.

1. The convenience functions call the generic programmatic interface
   function ``core.publish_programmatically()`` that creates a
   `core.Publisher` instance ::

       pub = core.Publisher(…, settings)

   eventually sets the components_ from the respective names, and calls ::

       publisher.process_programmatic_settings(
           settings_spec, settings_overrides, config_section)

   .. _publisher.process_programmatic_settings():

2. If `publisher.settings` is None,
   ``publisher.process_programmatic_settings()`` calls::

       publisher.get_settings(settings_spec, config_section, **defaults)

   with `defaults` taken from `publisher.settings_overrides`.

   If `publisher.settings` is defined, the following steps are skipped.

3. ``publisher.get_settings()`` calls::

       optpar = publisher.setup_option_parser(…,
                    settings_spec, config_section, **defaults)

4. The OptionParser instance determines setting defaults
   as described in `steps 4 to 7`__ in the previous section.

   __ `publisher.setup_option_parser()`_

5. Back in ``publisher.get_settings()``, the ``frontend.Values`` instance
   returned by ``optpar.get_default_values()`` is stored in
   ``publisher.settings``.

6. ``publish_programmatically()`` continues with setting
   ``publisher.source`` and ``publisher.destination``.

7. Finally, ``publisher.publish()`` is called. As ``publisher.settings``
   is not None, no further command line processing takes place.

8. All components acting on the Document Tree are handed the
   ``document`` root node and can access the runtime settings as
   ``document.settings`` (cf. `steps 11 and 12`__ in the previous section).

   __ `accessing the runtime settings`_


.. References:

.. _optparse: https://docs.python.org/dev/library/optparse.html
.. _argparse: https://docs.python.org/dev/library/argparse.html

.. _Docutils Runtime Settings:
   ../api/runtime-settings.html
.. _active sections: ../api/runtime-settings.html#active-sections
.. _SettingsSpec: ../api/runtime-settings.html#settingsspec
.. _component:
.. _components: ../api/runtime-settings.html#components

.. _convenience functions:
.. _Publisher convenience functions:
    ../api/publisher.html#publisher-convenience-functions
.. _publish_cmdline(): ../api/publisher.html#publish-cmdline
.. _"settings" argument: ../api/publisher.html#settings
.. _"settings_overrides" argument: ../api/publisher.html#settings-overrides
.. _"config_section" argument: ../api/publisher.html#config-section

.. _front-end tools: ../user/tools.html
.. _configuration file:
.. _configuration files:
.. _Docutils Configuration: ../user/config.html#configuration-files
.. _Configuration File Sections & Entries:
    ../user/config.html#configuration-file-sections-entries
.. _Docutils Project Model: ../peps/pep-0258.html#docutils-project-model
.. _Publisher: ../peps/pep-0258.html#publisher
.. _Reader: ../peps/pep-0258.html#reader
