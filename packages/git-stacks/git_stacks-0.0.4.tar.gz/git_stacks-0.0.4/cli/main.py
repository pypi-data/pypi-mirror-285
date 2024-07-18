import subprocess
import sys
import click
import git
from .utils import gh_utils


NUM_RECOMMIT_RETRIES = 3


cli = click.Group(help="extra git utilities")


@cli.command(name="pr")
@click.argument("branch_name", default="")
def print_prs(branch_name: str) -> None:
    prs = gh_utils.get_prs_for_branch(gh_utils.coalesce_branch_name(branch_name))
    for pr in prs:
        print(pr.pretty_str)


@cli.command()
@click.argument("message", nargs=-1)
def recommit(message: list[str]) -> None:
    """Runs git commit -am with retries then pushes."""
    if not message:
        message = ["."]
    message_str = " ".join(message)

    active_branch = gh_utils.coalesce_branch_name()
    if active_branch == gh_utils.get_master_branch_name():
        raise ValueError(f"Cannot recommit directly to {gh_utils.get_master_branch_name()}!")

    commit_args = [
        "git",
        "commit",
        "-am",
        message_str,
    ]

    for retry_idx in range(NUM_RECOMMIT_RETRIES):
        result = subprocess.run(
            args=commit_args,
            check=retry_idx == NUM_RECOMMIT_RETRIES - 1,
        )

        if result.returncode == 0:
            break

    # Push to upstream
    push_cmd_args = ["git", "push"]
    push_result = subprocess.run(
        args=push_cmd_args,
        check=False,
        text=True,
        capture_output=True,
    )

    no_upstream_message = f"fatal: The current branch {active_branch} has no upstream branch."

    if push_result.returncode == 0:
        pass
    elif no_upstream_message in push_result.stderr:
        gh_utils.push_upstream()
        print("Automatically submitted to upstream.")
    else:
        print("stdout:")
        print(push_result.stdout)
        print("stderr:")
        print(push_result.stderr)
        raise subprocess.CalledProcessError(
            returncode=push_result.returncode,
            cmd=push_cmd_args,
            output=push_result.stdout,
            stderr=push_result.stderr,
        )


@cli.command()
@click.argument("title", nargs=-1, required=True)
def submit(title: list[str]) -> None:
    title_str = " ".join(title)

    active_branch_name = gh_utils.coalesce_branch_name()
    current_prs = gh_utils.get_prs_for_branch(active_branch_name)
    if current_prs:
        raise ValueError(f"PR already created! {[pr.pretty_str for pr in current_prs]}")

    gh_utils.ensure_pushed_upstream()

    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            title_str,
            "--body",
            "",
        ],
        check=True,
        text=True,
    )


@cli.command(name="print-merged")
def print_merged_branches() -> None:
    """Print all local branch names from merged PRs."""

    def is_merged(branch_name: str) -> bool:
        """Whether ALL (at least 1) prs for a branch are merged."""
        prs = gh_utils.get_prs_for_branch(branch_name)

        if not prs:
            return False

        return all(pr.state == "MERGED" for pr in prs)

    refs: list[git.Head] = list(gh_utils.get_repo().branches)  # type: ignore

    print(" ".join(ref.name for ref in refs if is_merged(ref.name)))


@cli.command(name="pr")
@click.argument("branch-name", default="")
def print_pr_for_branch(branch_name: str = "") -> None:
    """Prints the PR for a given branch.

    If there is not exactly one, will print all of them and then throw.
    """
    coalesced_branch_name = gh_utils.coalesce_branch_name(branch_name)

    prs = gh_utils.get_prs_for_branch(coalesced_branch_name)

    open_prs = [pr for pr in prs if pr.state == "open"]
    if open_prs:
        prs = open_prs

    for pr in prs:
        print(pr.pretty_str)

    if len(prs) != 1:
        sys.exit(1)


@cli.command(name="newbranch")
@click.argument("branch-name", type=str)
@click.option("--silent", is_flag=True, default=False, show_default=False, help="Whether to print nothing on success")
def create_branch(
    branch_name: str,
    silent: bool = False,
) -> None:
    """Creates a new branch and checks that the name isn't taken."""
    prs = gh_utils.get_prs_for_branch(branch_name)

    if prs:
        print("Found PR(s) with that branch name already!")
        for pr in prs:
            print("- " + pr.get_summary(current_pr_number=None) + f" {pr.url}")
        sys.exit(1)

    if not silent:
        print(f'Verified that branch name "{branch_name}" does not conflict with any existing PRs.')

    command = [
        "git",
        "checkout",
        "-b",
        branch_name,
    ]
    if not silent:
        print(f"RUNNING: {subprocess.list2cmdline(command)}")

    subprocess.run(command, check=True)
