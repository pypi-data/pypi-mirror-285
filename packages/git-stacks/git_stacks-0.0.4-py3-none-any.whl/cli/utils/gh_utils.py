# pylint: disable=invalid-name

from __future__ import annotations
import copy

import functools
import itertools
import json
import subprocess
from dataclasses import dataclass, asdict
import sys
from typing import List, Optional, cast, TypeVar, Any, Type
from abc import ABC, abstractmethod

import git

T_SerdeDataclass = TypeVar("T_SerdeDataclass", bound="SerdeDataclass")


class SerdeDataclass(ABC):
    @classmethod
    @abstractmethod
    def from_data(cls: Type[T_SerdeDataclass], data: Any) -> T_SerdeDataclass:
        """Builds the dataclass from a dictionary of data."""

    @abstractmethod
    def to_data(self) -> dict[str, Any]:
        """Converts the dataclass instance to a dict of data."""


@dataclass(frozen=True)
class GithubAuthor(SerdeDataclass):
    is_bot: bool
    login: str
    name: Optional[str] = None
    id: Optional[str] = None

    @classmethod
    def from_data(cls: Type[GithubAuthor], data: Any) -> GithubAuthor:
        return GithubAuthor(**data)

    def to_data(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GithubPR(SerdeDataclass):
    # attributes from: gh pr list --json
    #   additions
    #   assignees

    #   author
    author: GithubAuthor

    #   autoMergeRequest

    #   baseRefName
    baseRefName: str

    #   body
    body: str

    #   changedFiles
    #   closed
    #   closedAt
    #   comments
    #   commits
    #   createdAt
    #   deletions
    #   files

    #   headRefName
    headRefName: str

    #   headRefOid
    #   headRepository
    #   headRepositoryOwner
    #   id
    #   isCrossRepository
    #   isDraft
    #   labels
    #   latestReviews
    #   maintainerCanModify
    #   mergeCommit
    #   mergeStateStatus
    #   mergeable
    #   mergedAt
    #   mergedBy
    #   milestone

    #   number
    number: int

    #   potentialMergeCommit
    #   projectCards
    #   projectItems
    #   reactionGroups
    #   reviewDecision
    #   reviewRequests
    #   reviews

    #   state
    state: str
    """E.g. OPEN, CLOSED, MERGED, DRAFT"""

    #   statusCheckRollup

    #   title
    title: str

    #   updatedAt
    updatedAt: str

    #   url
    url: str

    @classmethod
    def from_data(cls: Type[GithubPR], data: Any) -> GithubPR:
        data = copy.deepcopy(data)
        data["author"] = GithubAuthor.from_data(data["author"])
        return GithubPR(**data)

    def to_data(self) -> dict[str, Any]:
        raise NotImplementedError()

    def get_summary(self, current_pr_number: Optional[int]) -> str:
        summary = f"(#{self.number}) {self.title}"
        if current_pr_number == self.number:
            summary = f"**{summary}**"
        if self.state in ("CLOSED", "MERGED"):
            summary = f"~~{summary}~~"
        return summary

    @property
    def pretty_str(self) -> str:
        return f"[{self.state.upper()}] (#{self.number}) {self.title} | {self.url}"


def coalesce_branch_name(branch_name: Optional[str] = None) -> str:
    """Defaults given branch_name to the active branch.

    Active branch fallback fails if there is no active branch (detached head).
    """
    if branch_name:
        return branch_name

    repo = get_repo()
    try:
        return repo.active_branch.name
    except TypeError as err:
        raise ValueError("Cannot coalesce branch_name in detached head state!") from err


@functools.lru_cache
def get_master_branch_name() -> str:
    # TODO: detect main
    return "master"


def get_local_base_branch() -> str:
    current_branch_name = coalesce_branch_name()
    hex_to_commit = {
        cast(git.Commit, branch.commit).hexsha: branch  # type: ignore
        for branch in get_repo().branches  # type: ignore
        if branch.name != current_branch_name
    }

    master_merge_bases = get_repo().merge_base(
        get_master_branch_name(),
        current_branch_name,
    )
    if master_merge_bases is None or len(master_merge_bases) == 0:
        raise ValueError("Current branch does not share history with master!")
    elif len(master_merge_bases) > 1:
        raise ValueError(f"Found multiple merge bases with {get_master_branch_name()}!")

    master_merge_base = master_merge_bases[0]

    base_branch: Optional[git.Head] = None
    for commit in get_repo().iter_commits(current_branch_name):
        if commit == master_merge_base:
            break

        if commit.hexsha not in hex_to_commit:
            continue

        base_branch = hex_to_commit[commit.hexsha]
        break

    if base_branch is None:
        raise ValueError(f"Current branch {current_branch_name} is not downstream of any local branch!")

    return base_branch.name


def query_prs(
    assignee: Optional[str] = None,
    author: Optional[str] = None,
    base: Optional[str] = None,
    head: Optional[str] = None,
    label: Optional[str] = None,
    limit: int = 30,
    state: str = "all",  # TODO: use enum
) -> List[GithubPR]:
    """Wraps `gh pr list`."""

    # See criteria with: gh pr list --help
    where_criteria = {
        # --app string        Filter by GitHub App author
        "assignee": assignee,
        "author": author,
        "base": base,
        "head": head,
        # --jq expression     Filter JSON output using a jq expression
        "label": label,
        "limit": limit,
        "state": state,
    }
    where_statements = [
        [
            f"--{key}",  # TODO: convert to kebab case
            str(value),  # TODO: check bool type
        ]
        for key, value in where_criteria.items()
        if value is not None
    ]
    where_args = list(itertools.chain.from_iterable(where_statements))

    # TODO: --draft             Filter by draft state

    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            *where_args,
            # TODO: use GithubPR field names
            "--json=state,title,number,url,updatedAt,author,headRefName,body,baseRefName",
        ],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    )

    raw_data = json.loads(result.stdout)
    for raw_pr in raw_data:
        raw_pr["body"] = raw_pr["body"].replace("\r\n", "\n")

    prs: List[GithubPR] = []
    prs = [cast(GithubPR, GithubPR.from_data(pr_data)) for pr_data in raw_data]
    prs.sort(
        key=lambda pr: pr.updatedAt,
        reverse=True,
    )

    return prs


def get_prs_for_branch(branch_name: str) -> List[GithubPR]:
    return query_prs(head=branch_name)


def get_downstream_branches(branch_name: str) -> List[GithubPR]:
    return query_prs(base=branch_name)


def get_base_branch(branch_name: str) -> str:
    prs = get_prs_for_branch(branch_name)
    if len(prs) == 0:
        raise ValueError(f"{branch_name} does not have a PR!")
    if len(prs) > 1:
        raise ValueError(f"Multiple PRs found for branch {branch_name}!")

    return prs[0].baseRefName


@functools.lru_cache
def get_repo() -> git.Repo:
    """Get the repo at CWD (not necessarily this code)"""
    return git.Repo(".", search_parent_directories=True)


def update_pr(pr: GithubPR) -> None:
    # TODO: fetch

    repo = get_repo()
    head_ref = repo.branches[pr.headRefName]  # type: ignore
    head_ref.checkout()

    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "pull", "origin", pr.baseRefName, "--no-edit"], check=True)
    subprocess.run(["git", "push"], check=True)


def push_upstream() -> None:
    active_branch = get_repo().active_branch

    if get_repo().head.is_detached:
        print("Cannot create upstream for detached head state!", file=sys.stderr)
        sys.exit(1)

    upstream = active_branch.tracking_branch()

    if upstream is None:
        get_repo().git.push(
            "--set-upstream",
            get_repo().remote().name,
            active_branch.name,
        )
    else:
        raise ValueError(
            f"Warning: {active_branch.name} already pushed to upstream!",
        )


def ensure_pushed_upstream() -> None:
    try:
        push_upstream()
    except ValueError as err:
        if "already pushed to upstream" not in str(err):
            raise err
