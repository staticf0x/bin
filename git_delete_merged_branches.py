#!/usr/bin/env python3
"""Delete local branches that are already gone from remote."""

import argparse
import re
import subprocess

from rich import print as rprint

# Patterns for finding issue IDs
# Each pattern has to contain a single capture group for the whole issue ID
PATTERNS = []

# URL to Jira (must end with /)
JIRA_URL = ""


def get_default_branch() -> str:
    output = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "origin/HEAD"],
        shell=False,
        check=True,
        stdout=subprocess.PIPE,
    )
    output_str = output.stdout.decode("ascii").strip()

    return output_str.replace("origin/", "")


def get_current_branch() -> str:
    output = subprocess.run(
        ["git", "b", "--show-current"], shell=False, check=True, stdout=subprocess.PIPE
    )

    return output.stdout.decode("ascii").strip()


def get_all_remote_branches() -> list[str]:
    output = subprocess.run(
        ["git", "branch", "-r"], shell=False, check=True, stdout=subprocess.PIPE
    )
    output_str = output.stdout.decode("ascii")

    branches = [line.strip() for line in output_str.strip().split("\n")]
    branches = [branch for branch in branches if "->" not in branch]
    branches = [
        branch.removeprefix("origin/")
        for branch in branches
        if branch.startswith("origin")
    ]
    branches = [branch for branch in branches if branch not in ("main", "master")]

    return set(branches)


def get_all_local_branches() -> list[str]:
    output = subprocess.run(
        ["git", "branch"], shell=False, check=True, stdout=subprocess.PIPE
    )
    output_str = output.stdout.decode("ascii")

    branches = [line.strip() for line in output_str.strip().split("\n")]
    branches = [branch.removeprefix("* ") for branch in branches]
    branches = [branch.split()[0] for branch in branches]
    branches = [branch for branch in branches if branch not in ("main", "master")]

    return set(branches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", action="store_true", default=False, help="fetch --prune before checking"
    )

    args = parser.parse_args()

    # Check that we're on default branch
    default_branch = get_default_branch()
    current_branch = get_current_branch()

    if current_branch != default_branch:
        rprint(
            f"[red]Currently checked out branch is not {default_branch}, it is: {current_branch}[/red]"
        )
        exit(1)

    if args.f:
        # First, call git fetch --prune
        subprocess.run(["git", "fetch", "--all", "--prune"], shell=False, check=True)

    merged_branches = get_all_local_branches() - get_all_remote_branches()

    for branch in merged_branches:
        rprint(
            f"Branch [bold yellow]{branch}[/bold yellow] seems to be deleted in remote"
        )

        for pattern in PATTERNS:
            if m := pattern.match(branch):
                issue_id = m.group(1)
                rprint(f"  Issue ID: [bold cyan]{issue_id}[/bold cyan]")
                rprint(f"  Link:     [bold green]{JIRA_URL}{issue_id}[/bold green]")

        rprint(
            rf"  Delete [bold underline]local[/bold underline] branch [bold red]{branch}[/bold red]? \[y/N] ",
            end="",
        )
        ans = input().lower()

        if ans == "y":
            rprint(f"  Deleting [bold red]{branch}[/bold red]")
            subprocess.run(["git", "b", "-D", branch])
