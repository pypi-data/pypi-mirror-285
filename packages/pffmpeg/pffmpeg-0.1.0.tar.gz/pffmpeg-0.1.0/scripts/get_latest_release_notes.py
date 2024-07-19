#!/usr/bin/env python
"""Print release notes for latest version."""

import argparse
import pathlib
import re
import sys

CHANGELOG_PATH = pathlib.Path("CHANGELOG.md")
LATEST_RELEASE_PATTERN = re.compile(
    r"(## \d+\.\d+\.\d+ \(\d{4}-\d{2}-\d{2}\)\n\n.+?)(?=\n\n## |\Z)",
    re.DOTALL,
)
VERSION_HEADER = re.compile(r"## (\d+\.\d+\.\d+) (\(\d{4}-\d{2}-\d{2}\))")
MD_HEADER = re.compile(r"^(#+) (.*)\n\n", re.MULTILINE)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        "--git-compat",
        action="store_true",
        help="Print compatible release notes with git message format.",
    )
    parser.add_argument(
        "-v",
        "--version-header",
        action="store_true",
        help="Add version header.",
    )
    args = parser.parse_args()

    changelog = CHANGELOG_PATH.read_text()

    # Retrieve release notes
    latest_release_match = LATEST_RELEASE_PATTERN.search(changelog)
    if not latest_release_match:
        sys.exit(-1)
    content = latest_release_match.group().strip()

    # Retrieve version
    version_match = VERSION_HEADER.search(content)
    if not version_match:
        sys.exit(-1)
    version = version_match.group(1)

    # Remove header
    content = content.replace(version_match.group(), "").lstrip()

    # Add version header if flag
    if args.version_header:
        content = f"## Version {version}\n\n{content}"

    # Make output git compatible, remove '#'.
    if args.git_compat:
        for m in MD_HEADER.finditer(content):
            header_level = len(m.group(1))
            header = m.group(2)
            match header_level:
                case 2:
                    content = content.replace(
                        m.group(), f"{header}\n{'-' * len(header)}\n\n", 1
                    )
                case 3:
                    content = content.replace(m.group(), f"{header}:\n", 1)

    if content:
        print(content)
    else:
        sys.exit(-1)
