#!/usr/bin/env python3

# $Id$
# Author: engelbert gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
test buildhtml options, because ``--local`` is broken.

Build-HTML Options
------------------
--recurse               Recursively scan subdirectories for files to process.
                        This is the default.
--local                 Do not scan subdirectories for files to process.
--prune=<directory>     Do not process files in <directory>.  This option may
                        be used more than once to specify multiple
                        directories.
--ignore=<patterns>     Recursively ignore files or directories matching any
                        of the given wildcard (shell globbing) patterns
                        (separated by colons).  Default: ".svn:CVS"
--silent                Work silently (no progress messages).  Independent of
                        "--quiet".
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# TOOLS_ROOT is ./tools/ from the docutils root
TOOLS_ROOT = Path(__file__).resolve().parent.parent
BUILDHTML_PATH = TOOLS_ROOT / 'buildhtml.py'


def run_buildhtml(options: list[str]) -> str:
    ret = subprocess.run(
        [sys.executable, BUILDHTML_PATH] + options,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    return ret.stderr


def process_filelist(stderr: str) -> tuple[list[str], list[str]]:
    dirs = []
    files = []
    for line in stderr.splitlines():
        # BUG no colon in filename/path allowed
        item = line.split(": ")[-1].strip()
        if line.startswith(" "):
            files.append(item)
        else:
            dirs.append(item)
    return dirs, files


class BuildHtmlTests(unittest.TestCase):
    tree = (
        "_tmp_test_tree/one.txt",
        "_tmp_test_tree/two.txt",
        "_tmp_test_tree/dir1/one.txt",
        "_tmp_test_tree/dir1/two.txt",
        "_tmp_test_tree/dir2/one.txt",
        "_tmp_test_tree/dir2/two.txt",
        "_tmp_test_tree/dir2/sub/one.txt",
        "_tmp_test_tree/dir2/sub/two.txt",
    )

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp()).resolve()

        for file in self.tree:
            path = self.root / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('dummy', encoding='utf-8')

    def tearDown(self) -> None:
        shutil.rmtree(self.root)

    def test_1(self) -> None:
        opts = ["--dry-run", str(self.root)]
        stderr = run_buildhtml(opts)
        _dirs, files = process_filelist(stderr)
        self.assertEqual(files.count("one.txt"), 4, stderr)

    def test_local(self) -> None:
        opts = ["--dry-run", "--local", str(self.root)]
        stderr = run_buildhtml(opts)
        dirs, files = process_filelist(stderr)
        self.assertEqual(len(dirs), 1, stderr)
        self.assertEqual(files, [], stderr)


if __name__ == '__main__':
    unittest.main()
