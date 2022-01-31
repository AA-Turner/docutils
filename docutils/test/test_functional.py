#!/usr/bin/env python3
# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Perform tests with the data in the functional/ directory.

Please see the documentation on `functional testing`__ for details.

__ ../../docs/dev/testing.html#functional
"""

import os
import os.path
from pathlib import Path
import shutil
import unittest

import docutils.core

NO_EXPECTED_TEMPLATE = """\
Cannot find expected output at {exp}
If the output in {out}
is correct, move it to the expected/ dir and check it in:

  mv {out} {exp}
  svn add {exp}
  svn commit -m "<comment>" {exp}"""

EXPECTED_OUTPUT_DIFFERS_TEMPLATE = """\
The expected and actual output differs.
Please compare the expected and actual output files:

  diff {exp} {out}

If the actual output is correct, please replace the
expected output and check it in:

  mv {out} {exp}
  svn add {exp}
  svn commit -m "<comment>" {exp}"""


class FunctionalTests(unittest.TestCase):

    """Test case for one config file."""
    maxDiff = None

    def setUp(self):
        """Clear output directory."""
        for entry in os.scandir(Path('functional', 'output')):
            if os.path.isdir(entry.path):
                shutil.rmtree(entry.path)
            elif entry.name != "README.txt":
                os.unlink(entry.path)

    def test_functional(self):
        """Process test file."""
        for test_file in Path('functional', 'tests').glob("*.py"):
            with self.subTest(test_file=test_file.as_posix()):
                namespace = {}
                # Load variables set in the current test file into the namespace
                exec(test_file.read_text(encoding='utf-8'), namespace)

                # Full source, actual output, and expected output paths
                source_path = Path('functional', 'input', namespace['test_source'])
                destination_path = Path('functional', 'output', namespace['test_destination'])
                expected_path = Path('functional', 'expected', namespace['test_destination'])

                # remove unneeded keys:
                for key in 'test_source', 'test_destination', '__builtins__':
                    del namespace[key]

                # Get output (automatically written to the output/ directory
                # by publish_file):
                output = docutils.core.publish_file(
                    **namespace, source_path=source_path.as_posix(),
                    destination_path=destination_path.as_posix())

                # Get the expected output *after* writing the actual output.
                try:
                    expected = expected_path.read_text(encoding='utf-8')
                except OSError as err:
                    raise OSError(NO_EXPECTED_TEMPLATE.format(
                        exp=expected_path, out=destination_path)) from err

                self.assertEqual(
                    output, expected,
                    EXPECTED_OUTPUT_DIFFERS_TEMPLATE.format(
                        exp=expected_path, out=destination_path))


if __name__ == '__main__':
    unittest.main()
