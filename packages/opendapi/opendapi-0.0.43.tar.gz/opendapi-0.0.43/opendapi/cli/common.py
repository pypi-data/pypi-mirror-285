"""Common utilities for the OpenDAPI CLI."""

import os
from typing import List, Optional

import click

from opendapi.config import OpenDAPIConfig
from opendapi.defs import CONFIG_FILEPATH_FROM_ROOT_DIR


def check_command_invocation_in_root():
    """Check if the `opendapi` CLI command is invoked from the root of the repository."""
    if not (os.path.isdir(".github") or os.path.isdir(".git")):
        click.secho(
            "  This command must be run from the root of your repository. Exiting...",
            fg="red",
        )
        raise click.Abort()
    click.secho(
        "  We are in the root of the repository. Proceeding...",
        fg="green",
    )
    return True


def get_opendapi_config(
    root_dir: str, local_spec_path: Optional[str] = None
) -> OpenDAPIConfig:
    """Get the OpenDAPI configuration object."""
    try:
        config = OpenDAPIConfig(root_dir, local_spec_path=local_spec_path)
        click.secho(
            f"  Found the {CONFIG_FILEPATH_FROM_ROOT_DIR} file. Proceeding...",
            fg="green",
        )
        return config
    except FileNotFoundError as exc:
        click.secho(
            f"  The {CONFIG_FILEPATH_FROM_ROOT_DIR} file does not exist. "
            "Please run `opendapi init` first. Exiting...",
            fg="red",
        )
        raise click.Abort() from exc


def check_if_opendapi_config_is_valid(config: OpenDAPIConfig) -> bool:
    """Check if the `opendapi.config.yaml` file is valid."""
    try:
        config.validate()
    except Exception as exc:
        click.secho(
            f"  The `{CONFIG_FILEPATH_FROM_ROOT_DIR}` file is not valid. "
            f"`opendapi init` may rectify. {exc}. Exiting...",
            fg="red",
        )
        raise click.Abort()
    click.secho(
        f"  The {CONFIG_FILEPATH_FROM_ROOT_DIR} file is valid. Proceeding...",
        fg="green",
    )
    return True


def pretty_print_errors(errors: List[Exception]):
    """Prints all the errors"""
    if errors:
        click.secho("\n\n")
        click.secho(
            "OpenDAPI: Encountered validation errors",
            fg="red",
            bold=True,
        )

    for error in errors:
        click.secho("\n")
        click.secho("OpenDAPI: ", nl=False, fg="green", bold=True)
        click.secho(error.prefix_message, fg="red")
        for err in error.errors:
            click.secho(err)
    click.secho("\n\n")


def dev_options(func: click.core.Command) -> click.core.Command:
    """Set of click options required for most commands."""
    options = [
        click.option(
            "--local-spec-path",
            default=None,
            envvar="LOCAL_SPEC_PATH",
            help="Use specs in the local path instead of the DAPI server",
            show_envvar=False,
        ),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def dapi_server_options(func: click.core.Command) -> click.core.Command:
    """Set of click options required for the dapi server commands."""
    options = [
        click.option(
            "--dapi-server-host",
            envvar="DAPI_SERVER_HOST",
            show_envvar=True,
            default="https://api.wovencollab.com",
            help="The host of the DAPI server",
        ),
        click.option(
            "--dapi-server-api-key",
            envvar="DAPI_SERVER_API_KEY",
            show_envvar=True,
            help="The API key for the DAPI server",
        ),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def github_options(func: click.core.Command) -> click.core.Command:
    """Set of click options required for the enrich command."""
    options = [
        click.option(
            "--github-event-name",
            type=click.Choice(
                ["push", "pull_request", "schedule", "workflow_dispatch"],
                case_sensitive=True,
            ),
            envvar="GITHUB_EVENT_NAME",
            show_envvar=False,
        ),
        click.option(
            "--github-run-attempt",
            envvar="GITHUB_RUN_ATTEMPT",
            show_envvar=False,
        ),
        click.option(
            "--github-run-id",
            envvar="GITHUB_RUN_ID",
            show_envvar=False,
        ),
        click.option(
            "--github-head-sha",
            envvar="GITHUB_HEAD_SHA",
            show_envvar=False,
        ),
        click.option(
            "--github-repository",
            envvar="GITHUB_REPOSITORY",
            show_envvar=False,
        ),
        click.option(
            "--github-workspace",
            envvar="GITHUB_WORKSPACE",
            show_envvar=False,
        ),
        click.option(
            "--github-step-summary",
            envvar="GITHUB_STEP_SUMMARY",
            show_envvar=False,
        ),
        click.option(
            "--github-event-path",
            envvar="GITHUB_EVENT_PATH",
            show_envvar=False,
        ),
        click.option("--github-token", envvar="GITHUB_TOKEN", show_envvar=False),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def opendapi_run_options(func: click.core.Command) -> click.core.Command:
    """Set of click options required for the client commands for debugging."""
    options = [
        click.option(
            "--mainline-branch-name",
            default="main",
            envvar="MAINLINE_BRANCH_NAME",
            show_envvar=True,
            help="The name of the mainline branch to compare against",
        ),
        click.option(
            "--enrich-batch-size",
            default=5,
            envvar="ENRICH_BATCH_SIZE",
            help="Batch size for validating and enriching DAPI files",
            show_envvar=False,
        ),
        click.option(
            "--register-batch-size",
            default=30,
            envvar="REGISTER_BATCH_SIZE",
            help="Batch size for validating and enriching DAPI files",
            show_envvar=False,
        ),
        click.option(
            "--analyze-impact-batch-size",
            default=15,
            envvar="ANALYZE_IMPACT_BATCH_SIZE",
            help="Batch size for analyzing impact of DAPI files",
            show_envvar=False,
        ),
        click.option(
            "--suggest-changes",
            is_flag=True,
            default=True,
            envvar="SUGGEST_CHANGES",
            show_envvar=True,
            help="Suggest changes to the DAPI files",
        ),
        click.option(
            "--revalidate-all-files",
            is_flag=True,
            default=False,
            envvar="REVALIDATE_ALL_FILES",
            help="Revalidate all files, not just the ones that have changed",
            show_envvar=True,
        ),
        click.option(
            "--require-committed-changes",
            is_flag=True,
            default=False,
            envvar="REQUIRE_COMMITTED_CHANGES",
            help="Do not Overwrite uncommitted DAPI files with server suggestions",
            show_envvar=True,
        ),
        click.option(
            "--ignore-suggestions-cache",
            is_flag=True,
            default=False,
            envvar="IGNORE_SUGGESTIONS_CACHE",
            help="Ignore suggestions cache and fetch fresh suggestions",
            show_envvar=False,
        ),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def third_party_options(func: click.core.Command) -> click.core.Command:
    """Set of click options required for the third-party integrations."""
    options = [
        click.option(
            "--dbt-cloud-url",
            envvar="DAPI_DBT_CLOUD_URL",
            show_envvar=True,
            help="The host of the dbt Cloud integration",
        ),
        click.option(
            "--dbt-cloud-api-key",
            envvar="DAPI_DBT_CLOUD_API_KEY",
            show_envvar=True,
            help="The API key for the dbt cloud integration",
        ),
        click.option(
            "--dbt-cloud-retry-count",
            envvar="DAPI_DBT_CLOUD_RETRY_COUNT",
            show_envvar=True,
            help="The retry count for dbt cloud integration",
        ),
        click.option(
            "--dbt-cloud-retry-interval",
            envvar="DAPI_DBT_CLOUD_RETRY_INTERVAL",
            show_envvar=True,
            help="The retry interval for dbt cloud integration",
        ),
    ]
    for option in reversed(options):
        func = option(func)
    return func
