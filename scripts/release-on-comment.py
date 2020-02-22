import argparse
import json
import os
import re
import sys
from pathlib import Path
from subprocess import check_call
from subprocess import check_output
from textwrap import dedent
from typing import Optional

from colorama import Fore
from colorama import init
from github3.repos import Repository


class InvalidFeatureRelease(Exception):
    pass


# remove me
SLUG = "nicoddemus/pytest"


PR_BODY = """\
Pull request was created automatically from {comment_url}.
"""


def login(token) -> Repository:
    import github3

    github = github3.login(token=token)
    owner, repo = SLUG.split("/")
    return github.repository(owner, repo)


def validate_and_get_issue_comment_payload(issue_payload_path: Optional[Path]):
    payload = json.loads(issue_payload_path.read_text(encoding="UTF-8"))
    body = payload["comment"]["body"]
    m = re.match(r"@pytestbot please prepare release from ([\w\-_\.]+)", body)
    if m:
        base_branch = m.group(1)
    else:
        base_branch = None
    return payload, base_branch


def print_and_exit(msg):
    print(msg)
    raise SystemExit(1)


def trigger_release(payload_path: Path, token: str):
    payload, base_branch = validate_and_get_issue_comment_payload(payload_path)
    if base_branch is None:
        url = payload["comment"]["url"]
        print_and_exit(
            f"Comment {Fore.CYAN}{url}{Fore.RESET} did not match the trigger command."
        )
    print()
    print(f"Precessing release for branch {Fore.CYAN}{base_branch}")

    repo = login(token)

    issue_number = payload["issue"]["number"]
    issue = repo.issue(issue_number)

    try:
        version = find_next_version(base_branch)
    except InvalidFeatureRelease as e:
        issue.create_comment(str(e))
        print_and_exit(f"{Fore.RED}{e}")

    try:
        print(f"Version: {Fore.CYAN}{version}")

        release_branch = f"release-{version}"

        check_call(["git", "config", "user.name", "pytest bot"])
        check_call(["git", "config", "user.email", "pytestbot@gmail.com"])

        check_call(["git", "checkout", "-b", release_branch, f"origin/{base_branch}"])

        print(f"Branch {Fore.CYAN}{release_branch}{Fore.RESET} created.")

        # TODO: remove skip-check-links
        check_call(
            [sys.executable, "scripts/release.py", version, "--skip-check-links"]
        )

        oauth_url = f"https://{token}:x-oauth-basic@github.com/{SLUG}.git"
        check_call(["git", "push", oauth_url, f"HEAD:{release_branch}", "--force"])
        print(f"Branch {Fore.CYAN}{release_branch}{Fore.RESET} pushed.")

        body = PR_BODY.format(comment_url=payload["comment"]["url"])
        pr = repo.create_pull(
            f"Prepare release {version}",
            base=base_branch,
            head=release_branch,
            body=body,
        )
        print(f"Pull request {Fore.CYAN}{pr.url}{Fore.RESET} created.")

        comment = issue.create_comment(
            f"Opened PR for release `{version}` in #{pr.number}"
        )
        print(f"Notified in original comment {Fore.CYAN}{comment.url}{Fore.RESET}.")

        print(f"{Fore.GREEN}Success.")
    except Exception as e:
        link = f"https://github.com/{SLUG}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
        issue.create_comment(
            dedent(
                f"""
            Sorry, the request to prepare release `{version}` from {base_branch} failed with:

            ```
            {e}
            ```

            See: {link}
            """
            )
        )
        print_and_exit(f"{Fore.RED}{e}")


def find_next_version(base_branch):
    output = check_output(["git", "tag"], encoding="UTF-8")
    valid_versions = []
    for v in output.splitlines():
        m = re.match(r"\d.\d.\d+$", v.strip())
        if m:
            valid_versions.append(tuple(int(x) for x in v.split(".")))

    valid_versions.sort()
    last_version = valid_versions[-1]

    changelog = Path("changelog")

    features = list(changelog.glob("*.feature.rst"))
    breaking = list(changelog.glob("*.breaking.rst"))
    is_feature_release = features or breaking

    if is_feature_release and base_branch != "master":
        msg = dedent(
            f"""
            Found features or breaking changes in {base_branch}, and feature releases can only be
            created from `master`.":
        """
        )
        msg += "\n".join(f"* `{x.name}`" for x in sorted(features + breaking))
        raise InvalidFeatureRelease(msg)

    if is_feature_release:
        return f"{last_version[0]}.{last_version[1] + 1}.0"
    else:
        return f"{last_version[0]}.{last_version[1]}.{last_version[2] + 1}"


def main():
    init(autoreset=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("token")
    options = parser.parse_args()
    trigger_release(Path(options.payload), options.token)


if __name__ == "__main__":
    main()
