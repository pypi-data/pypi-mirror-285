# pylint: disable=too-many-instance-attributes, too-many-branches, too-many-boolean-expressions
"""Git adapter for OpenDapi"""
import subprocess  # nosec: B404
from dataclasses import dataclass
from typing import List, Optional, Tuple

from opendapi.defs import ALL_OPENDAPI_SUFFIXES


def run_git_command(cwd: str, command_split: List[str]) -> str:
    """Run a git command."""
    try:
        return subprocess.check_output(
            command_split,
            cwd=cwd,
        )  # nosec
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"git command {command_split}: {exc}") from exc


def get_checked_out_branch_or_commit(cwd: str) -> str:
    """Get the checked out branch or commit."""
    # if a branch is checked out, returns the branch name, if a commit is, it returns HEAD
    branch_name_or_head = (
        run_git_command(cwd, ["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode("utf-8")
        .strip()
    )
    # if the branch is detached, it returns the commit hash
    if branch_name_or_head == "HEAD":
        return (
            run_git_command(cwd, ["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        )
    return branch_name_or_head


def _get_current_stash_names_with_index(cwd: str) -> List[Tuple[int, str]]:
    return [
        (i, stash.split(": ")[-1])
        for i, stash in enumerate(
            run_git_command(cwd, ["git", "stash", "list"]).decode("utf-8").split("\n")
        )
    ]


def add_named_stash(cwd: str, stash_name: str) -> None:
    """
    Add a named stash. Note that index not returned
    since it changes with other stashes.
    """
    # if there is nothing to stash this does not raise or fail, but instead
    # just does not create the named stash
    current_stashes = [stash for _, stash in _get_current_stash_names_with_index(cwd)]
    if stash_name in current_stashes:
        raise ValueError(f"Stash {stash_name} already exists")
    run_git_command(cwd, ["git", "stash", "save", f'"{stash_name}"'])


def pop_named_stash(cwd: str, stash_name: str) -> None:
    """Pop a named stash."""
    current_stashes_w_index = _get_current_stash_names_with_index(cwd)
    stash_index = next(
        (i for i, stash in current_stashes_w_index if stash == stash_name),
        None,
    )
    if stash_index is None:
        raise ValueError(f"Stash {stash_name} not found")
    run_git_command(cwd, [f"git", "stash", "pop", "stash@{stash_index}"])


def get_changed_opendapi_filenames(cwd: str) -> List[str]:
    """Get the list of changed opendapi files."""
    files_patterns = ["*" + suffix for suffix in ALL_OPENDAPI_SUFFIXES]
    all_files_command = [
        "git",
        "status",
        "--porcelain",
        *files_patterns,
    ]
    result = run_git_command(cwd, all_files_command)
    if not result:
        return []
    result = result.decode("utf-8").replace("'", "")
    return [r.split(" ", 2)[-1] for r in result.split("\n") if r]


def add_untracked_opendapi_files(cwd: str) -> int:
    """Add opendapi relevant untracked files to git and return number of files added."""
    files_patterns = ["*" + suffix for suffix in ALL_OPENDAPI_SUFFIXES]
    all_files_command = [
        "git",
        "add",
        "--dry-run",
        "--ignore-missing",
        *files_patterns,
    ]
    result = run_git_command(cwd, all_files_command)
    if result:
        result = result.decode("utf-8").replace("'", "")
        all_files = [r.split(" ", 2)[-1] for r in result.split("\n") if r]
        run_git_command(cwd, ["git", "add", *all_files])
        return len(all_files)
    return 0


def get_git_diff_filenames(
    root_dir: str,
    base_ref: str,
    current_ref: Optional[str] = None,
    cached: bool = False,
) -> List[str]:
    """Get the list of files changed between current and main branch"""
    commands = [
        "git",
        "diff",
        *(["--cached"] if cached else []),
        *["--name-only", base_ref],
        *([current_ref] if current_ref else []),
    ]
    files = run_git_command(root_dir, commands)
    return [filename for filename in files.decode("utf-8").split("\n") if filename]


def check_if_uncommitted_changes_exist(cwd: str) -> bool:
    """Check if uncommitted changes exist."""
    if run_git_command(cwd, ["git", "diff", "--name-only"]):
        return True
    return False


@dataclass
class ChangeTriggerEvent:
    """Change trigger event, e.g. from Github Actions"""

    where: str
    before_change_sha: str = None
    event_type: Optional[str] = None
    after_change_sha: Optional[str] = None
    repo_api_url: Optional[str] = None
    repo_html_url: Optional[str] = None
    repo_owner: Optional[str] = None
    git_ref: Optional[str] = None
    pull_request_number: Optional[int] = None
    auth_token: Optional[str] = None
    markdown_file: Optional[str] = None
    workspace: Optional[str] = None
    run_id: Optional[int] = None
    run_attempt: Optional[int] = None
    head_sha: Optional[str] = None
    repository: Optional[str] = None
    repo_full_name: Optional[str] = None
    pull_request_link: Optional[str] = None

    def __post_init__(self):
        """Post init checks"""
        if self.where not in ["local", "github"] or self.before_change_sha is None:
            raise ValueError(
                "Where should be either local or github."
                " Before change SHA is required"
            )

        if self.is_github_event:
            if (
                self.event_type is None
                or self.after_change_sha is None
                or self.repo_api_url is None
                or self.repo_html_url is None
                or self.repo_owner is None
                or self.auth_token is None
            ):
                raise ValueError(
                    "Event type, after change SHA, repo API URL, repo HTML URL, "
                    "repo owner and auth token are required"
                )

        if self.is_pull_request_event:
            if self.pull_request_number is None:
                raise ValueError("Pull request number is required")

        if self.is_push_event:
            if self.git_ref is None:
                raise ValueError("Git ref is required")

    @property
    def is_local_event(self) -> bool:
        """Check if the event is a local event"""
        return self.where == "local"

    @property
    def is_github_event(self) -> bool:
        """Check if the event is a github event"""
        return self.where == "github"

    @property
    def is_pull_request_event(self) -> bool:
        """Check if the event is a pull request event"""
        return self.event_type == "pull_request"

    @property
    def is_push_event(self) -> bool:
        """Check if the event is a push event"""
        return self.event_type == "push"
