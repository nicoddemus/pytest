import os
import re
import sys
from pathlib import Path

import github3


def publish_github_release(token, tag_name, body):
    github = github3.login(token=token)

    repo = github.repository("nicoddemus", "pytest")
    return repo.create_release(tag_name=tag_name, body=body)


def parse_changelog(tag_name):
    p = Path(__file__).parent.parent / "CHANGELOG.rst"
    changelog_lines = p.read_text(encoding="UTF-8").splitlines()

    title_regex = re.compile(r"pytest (\d\.\d\.\d) \(\d{4}-\d{2}-\d{2}\)")
    consuming_version = False
    version_lines = []
    for line in changelog_lines:
        m = title_regex.match(line)
        if m:
            if m.group(1) == tag_name:
                consuming_version = True
            elif consuming_version:
                break
        if consuming_version:
            version_lines.append(line)

    return "\n".join(version_lines)


def convert_rst_to_md(text):
    import pypandoc

    return pypandoc.convert_text(text, "md", format="rst")


def main(argv):
    if len(argv) > 1:
        tag_name = argv[1]
    else:
        tag_name = os.environ.get("TRAVIS_TAG")
        if not tag_name:
            print("tag_name not given and $TRAVIS_TAG not set")
            return 1

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GH_TOKEN not set")
        return 1

    rst_body = parse_changelog(tag_name)
    md_body = convert_rst_to_md(rst_body)
    if not publish_github_release(token, tag_name, md_body):
        print("Could not publish release notes:")
        print(md_body)
        return 5


if __name__ == "__main__":
    sys.exit(main(sys.argv))
