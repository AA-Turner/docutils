"""
Generic Docutils command line interface.

Also contains rst* tool entry points.
"""

import argparse

from docutils.core import publish_cmdline, default_description
from docutils.frontend import ConfigParser, OptionParser

_CONFIG_SECTION = "docutils-cli application"

_config_parser = ConfigParser()
_config_parser.read(OptionParser().get_standard_config_files(), OptionParser())
_config_settings = _config_parser.get_section(_CONFIG_SECTION)

_parser = argparse.ArgumentParser(
    description="Publish documents from reStructuredText or Markdown sources.",
    epilog="Further optional arguments are added by the selected components, "
           "the list below adapts to your selection.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    add_help=False,
)
_parser.add_argument("source", nargs="?")
_parser.add_argument("destination", nargs="?")
_parser.add_argument("-h", "--help", help="show this help message and exit",
                     action="store_true")
_parser.add_argument("-r", "--reader", help="name of the reader",
                     default=_config_settings.get("reader", "standalone"))
_parser.add_argument("-p", "--parser", help="name of the parser",
                     default=_config_settings.get("parser", "rst"))
_parser.add_argument("-w", "--writer", help="name of the writer",
                     default=_config_settings.get("writer", "html5"))


def _publish(__argv=None, __description=default_description):
    args, unknown = _parser.parse_known_args(__argv)

    if args.help:
        print(_parser.format_help())
        unknown.append("--help")

    try:
        publish_cmdline(
            reader_name=args.reader,
            parser_name=args.parser,
            writer_name=args.writer,
            config_section=_CONFIG_SECTION,
            description=__description,
            argv=[*filter(None, [args.source, args.destination, *unknown])],
        )
    except ImportError as err:
        if "--traceback" in set(unknown):
            raise err
        print(err)
        raise SystemExit("Use '--traceback' to show details.")


if __name__ == "__main__":
    _publish()

# ENTRY POINTS
# ############
import sys

ARGS = sys.argv[1:]


def publish_html():
    description = ('Generates (X)HTML documents from standalone reStructuredText '
                   'sources.  ' + default_description)
    _publish(["--writer", "html"] + ARGS, description)


def publish_html4():
    description = ('Generates (X)HTML documents from standalone reStructuredText '
                   'sources.  ' + default_description)
    _publish(["--writer", "html4"] + ARGS, description)


def publish_html5():
    description = ('Generates HTML5 documents from standalone '
                   'reStructuredText sources.\n' + default_description)
    _publish(["--writer", "html5"] + ARGS, description)


def publish_latex():
    description = ('Generates LaTeX documents from standalone reStructuredText '
                   'sources. '
                   'Reads from <source> (default is stdin) and writes to '
                   '<destination> (default is stdout).  See '
                   '<https://docutils.sourceforge.io/docs/user/latex.html> for '
                   'the full reference.')
    _publish(["--writer", "latex"] + ARGS, description)


def publish_xetex():
    description = ('Generates LaTeX documents from standalone reStructuredText '
                   'sources for compilation with the Unicode-aware TeX variants '
                   'XeLaTeX or LuaLaTeX. '
                   'Reads from <source> (default is stdin) and writes to '
                   '<destination> (default is stdout).  See '
                   '<http://docutils.sourceforge.net/docs/user/latex.html> for '
                   'the full reference.')
    _publish(["--writer", "xetex"] + ARGS, description)


def publish_xml():
    description = ('Generates Docutils-native XML from standalone '
                   'reStructuredText sources.  ' + default_description)
    _publish(["--writer", "xml"] + ARGS, description)


def publish_pseudo_xml():
    description = ('Generates pseudo-XML from standalone reStructuredText '
                   'sources (for testing purposes).  ' + default_description)
    _publish(["--writer", "pseudoxml"] + ARGS, description)


def publish_man():
    description = ("Generates plain unix manual documents.  " + default_description)
    _publish(["--writer", "manpage"] + ARGS, description)


def publish_pep():
    description = ('Generates (X)HTML from reStructuredText-format PEP files.  '
                   + default_description)
    _publish(["--reader", "pep", "--writer", "pep_html",
              "--description", description] + ARGS)


def publish_s5():
    description = ('Generates S5 (X)HTML slideshow documents from standalone '
                   'reStructuredText sources.  ' + default_description)
    _publish(["--writer", "s5"] + ARGS, description)
