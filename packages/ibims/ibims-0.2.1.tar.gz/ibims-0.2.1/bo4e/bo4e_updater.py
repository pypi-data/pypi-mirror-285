"""
This script checks if the current BO4E version is up-to-date.
"""

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from traceback import format_exception
from typing import Any, Callable, Optional

import click
from bo4e_generator.__main__ import generate_bo4e_schemas
from bost.__main__ import main as bost_main
from bost.pull import get_source_repo, resolve_latest_version
from dotenv import dotenv_values, set_key
from git import Repo
from github import Github
from github.Auth import Token
from isort.main import main as isort_main

PR_TARGET_OWNER = "Hochfrequenz"
PR_TARGET_REPO = "intermediate-bo4e-migration-models"
REPO_ROOT = Path(__file__).parents[1]
DOTENV_FILE = REPO_ROOT / "bo4e/tox.env"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def current_version() -> str:
    """
    Query the current version from the tox.env file.
    The version tag should have the same format as the github release tag.
    E.g. "v2.0.13-rc3"
    """
    config = dotenv_values(DOTENV_FILE)
    assert config["BO4E_VERSION"] is not None
    return config["BO4E_VERSION"]


@contextmanager
def catch_all_exceptions(
    on_success: Optional[Callable[[], Any]] = None,
    on_error: Optional[Callable[[Exception], Any]] = None,
    on_finalize: Optional[Callable[[], Any]] = None,
    reraise: bool = False,
):
    """
    Context manager to catch all exceptions and call the appropriate callback functions.
    Optionally, the exception can be reraised after calling the callbacks.
    """
    try:
        yield
        if on_success is not None:
            on_success()
    except Exception as error:  # pylint: disable=broad-exception-caught
        if on_error is not None:
            on_error(error)
        if reraise:
            raise
    finally:
        if on_finalize is not None:
            on_finalize()


def rebuild_bo4e(version: str, gh_access_token: str) -> Optional[Exception]:
    """Try to rebuild auto-generated BO4E code"""
    error_during_rebuild: Optional[Exception] = None

    def error_callback(error: Exception):
        nonlocal error_during_rebuild
        error_during_rebuild = error
        logger.warning("Could not rebuild auto-generated code", exc_info=error)

    with catch_all_exceptions(
        on_error=error_callback,
        on_success=lambda: logger.info("Rebuilt and formatted auto-generated code successfully"),
    ):
        logger.info("Running bost...")
        bost_main(
            output=REPO_ROOT / "tmp/bo4e_schemas",
            target_version=version,
            update_refs=True,
            set_default_version=False,
            clear_output=True,
            config_file=REPO_ROOT / "bo4e/bo4e_config.json",
            cache_dir=REPO_ROOT / "tmp/bo4e_cache",
            token=gh_access_token,
        )
        logger.info("Running bo4e-generator...")
        generate_bo4e_schemas(
            input_directory=REPO_ROOT / "tmp/bo4e_schemas",
            output_directory=REPO_ROOT / "src/ibims/bo4e",
            target_version=version,
            clear_output=True,
            pydantic_v1=False,
        )
        logger.info("Run isort on auto-generated code. Normally, this should not change anything.")
        isort_main(str(REPO_ROOT / "src/ibims/bo4e"))
    return error_during_rebuild


# pylint: disable=too-many-locals, too-many-statements
@click.command()
def main():
    """
    Check if the current version is up-to-date. If so, exit with exit code 0.
    If not, update the version in the tox.env file and try to rebuild the BO4E code.
    Whether this succeeds or not, create a new branch and push the changes to the remote to create a pull request.
    """
    os.environ["GIT_PYTHON_TRACE"] = "full"
    with catch_all_exceptions(
        on_error=lambda error: logger.error("Access Token not provided", exc_info=error), reraise=True
    ):
        gh_access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    with catch_all_exceptions(
        on_error=lambda error: logger.error("Could not resolve latest version", exc_info=error), reraise=True
    ):
        latest_version = resolve_latest_version(token=gh_access_token)
    with catch_all_exceptions(
        on_error=lambda error: logger.error("Could not resolve current version", exc_info=error), reraise=True
    ):
        current = current_version()

    if latest_version == current:
        logger.info("Version %s is up to date.", current)
        return

    logger.info("Version %s is outdated. Updating to %s.", current, latest_version)

    with catch_all_exceptions(
        on_error=lambda error: logger.error("Could not initialize variables", exc_info=error),
        on_success=lambda: logger.info("Initialized variables successfully"),
        reraise=True,
    ):
        git_repo = Repo(REPO_ROOT)
        auth = Token(gh_access_token)
        github_repo = Github(auth=auth).get_repo(f"{PR_TARGET_OWNER}/{PR_TARGET_REPO}")
        github_bo4e_repo = get_source_repo(gh_access_token)
        latest_release = github_bo4e_repo.get_latest_release()
    # If using the script locally with a dirty working directory, stash changes to avoid conflicts
    with catch_all_exceptions(
        on_error=lambda error: logger.error("Could not stash changes", exc_info=error),
        on_success=lambda: logger.info("Stashed changes successfully"),
        reraise=True,
    ):
        git_repo.git.execute(["git", "stash", "push", "--include-untracked"])

    def log_error_and_unstash(error_msg: str) -> Callable[[Exception], None]:
        def inner(error: Exception):
            logger.error(error_msg, exc_info=error)
            git_repo.git.execute(["git", "stash", "pop"])

        return inner

    # Checkout new branch to later commit and push changes to remote etc.
    with catch_all_exceptions(
        on_error=log_error_and_unstash("Could not create new branch"),
        on_success=lambda: logger.info("Created and checkout new branch successfully"),
        reraise=True,
    ):
        new_branch_name = f"bo4e_bot/bo4e-{latest_version[1:]}"
        new_branch = git_repo.create_head(new_branch_name, logmsg=f"Create branch {new_branch_name}")
        new_branch.checkout()

    # Create some later needed variables before the long rebuilding process. For faster error responses if it fails.
    with catch_all_exceptions(
        on_error=log_error_and_unstash("Could not retrieve remote"),
        on_success=lambda: logger.info("Retrieved remote successfully"),
        reraise=True,
    ):
        remotes = git_repo.remotes
        assert len(remotes) == 1, "Expected exactly one remote"
        remote = remotes[0]
        assert remote.exists(), "Remote does not exist"

    logger.info("Branch: %s, Remote to create PR: %s", new_branch, remote.url)

    # Update BO4E-version in .env file and try to rebuild BO4E
    set_key(DOTENV_FILE, "BO4E_VERSION", latest_version, quote_mode="never")
    logger.info("Updated BO4E version in bo4e/tox.env file from %s to %s", current, latest_version)
    error = rebuild_bo4e(latest_version, gh_access_token)

    # Commit and push changes to remote
    with catch_all_exceptions(
        on_error=log_error_and_unstash("Could not commit or push changes to remote"),
        on_success=lambda: logger.info("Pushed changes to remote branch successfully"),
        reraise=True,
    ):
        # Path(REPO_ROOT / "test.txt").unlink(missing_ok=True)
        diff = git_repo.index.diff(None)
        diff_paths = [diff_elem.a_path for diff_elem in diff] + git_repo.untracked_files
        assert len(diff_paths) > 0, "Expected at least one changed file"
        print(f"Diff paths: {diff_paths}")
        git_repo.index.add(diff_paths)
        git_repo.index.commit(f"Update BO4E version to {latest_version}", skip_hooks=True)
        remote.push(f"refs/heads/{new_branch_name}:refs/heads/{new_branch_name}")

    # Create PR with new BO4E version. Even if it couldn't be rebuilt, a new version should be created.
    title = f"Bump BO4E from {current[1:]} to {latest_version[1:]}"
    body = (
        f"{title}.\n"
        f"BO4E rebuild: {'succeeded' if error is None else 'failed'}.\n\n"
        "<details>\n"
        "<summary>Changelog</summary>\n"
        f'<p><em>Sourced from <a href="{latest_release.html_url}">\n'
        "BO4E's changelog</a>.</em></p>\n"
        "<blockquote>\n"
        f"<h2>{latest_release.title}</h2>\n\n"
        f"{latest_release.body}\n"
        "</blockquote>\n"
        "</details>\n"
    )
    if error is not None:
        error_str = format_exception(error)
        body += (
            "<details>\n"
            "<summary>Rebuild error</summary>\n"
            "<blockquote>\n"
            f"```\n"
            f"{''.join(error_str)}\n"
            f"```\n"
            "</blockquote>\n"
            "</details>\n"
        )
    with catch_all_exceptions(
        on_error=log_error_and_unstash("Could not create pull request"),
        on_success=lambda: logger.info("Created pull request successfully"),
        reraise=True,
    ):
        github_repo.create_pull(
            title=title,
            body=body,
            head=new_branch_name,
            base="main",
        )

    # Pop stash if it was created
    with catch_all_exceptions(
        on_error=lambda error: logger.warning(
            "Could not pop stash. If run by the updater.yml workflow, this is usual and fine."
        ),
        on_success=lambda: logger.info("Popped stash successfully"),
    ):
        git_repo.git.execute(["git", "stash", "pop"])

    logger.info("Finished.")


if __name__ == "__main__":
    main()
