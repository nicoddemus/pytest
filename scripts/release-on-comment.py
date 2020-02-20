import argparse
import json
import re
from pathlib import Path
from subprocess import check_call
from subprocess import check_output
from textwrap import dedent
from typing import Optional

from colorama import Fore
from colorama import init
from github3.repos import Repository

from .release import pre_release


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


def trigger_release(issue_payload_path: Path, token: str):
    payload, base_branch = validate_and_get_issue_comment_payload(issue_payload_path)
    if base_branch is None:
        url = payload["comment"]["url"]
        print_and_exit(
            f"Comment {Fore.CYAN}{url}{Fore.RESET} did not match the trigger command."
        )

    repo = login(token)

    issue_number = payload["issue"]["number"]
    issue = repo.issue(issue_number)

    try:
        version = find_next_version(base_branch)
    except InvalidFeatureRelease as e:
        issue.create_comment(str(e))
        print_and_exit(f"{Fore.RED}{e}")

    release_branch = f"release-{version}"

    check_call(["git", "checkout", "-b", release_branch, f"origin/{base_branch}"])

    pre_release(version, skip_check_links=False)

    oauth_url = f"https://{token}:x-oauth-basic@github.com/{SLUG}.git"

    check_call(["git", "push", oauth_url, f"HEAD:{release_branch}", "--force"])

    body = PR_BODY.format(comment_url=payload["comment"]["url"])
    pr = repo.create_pull(
        f"Prepare release {version}", base=base_branch, head=release_branch, body=body
    )

    comment = issue.create_comment(f"Opened PR for release `{version}` in #{pr.number}")
    print(
        dedent(
            f"""
        {Fore.GREEN}Success.{Fore.RESET}
        notification: {Fore.CYAN}{comment.url}{Fore.RESET}
        pull request: {Fore.CYAN}{pr.url}{Fore.RESET}
        """
        )
    )


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
    parser.add_argument("--issue-payload")
    parser.add_argument("--token")
    options = parser.parse_args()
    trigger_release(
        issue_payload_path=Path(options.issue_payload), token=options.token,
    )


if __name__ == "__main__":
    main()
