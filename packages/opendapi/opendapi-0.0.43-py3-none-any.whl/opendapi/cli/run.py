"""CLI for generating, validating and enriching DAPI files: `opendapi run`."""

import click

from opendapi.cli.common import (
    dapi_server_options,
    dev_options,
    github_options,
    opendapi_run_options,
    third_party_options,
)
from opendapi.cli.enrich.main import cli as enrich_cli
from opendapi.cli.generate import cli as generate_cli


def _should_skip_run_for_dbt_cloud(**kwargs):
    """
    Check if the run command should be skipped

    Skip scenarios:
    1. If integrated with dbt Cloud
        a. Skip if pull request event and the run is the first attempt
        b. Skip if push event
    """

    should_wait_on_dbt_cloud = kwargs.get("dbt_cloud_url") is not None
    run_attempt = (
        int(kwargs.get("github_run_attempt")) if kwargs.get("github_run_attempt") else 0
    )
    is_push_event = kwargs.get("github_event_name") == "push"

    if should_wait_on_dbt_cloud and is_push_event:
        click.secho(
            "Skipping opendapi run command for push event",
            fg="yellow",
            bold=True,
        )
        return True

    if should_wait_on_dbt_cloud and run_attempt == 1:
        click.secho(
            "Skipping opendapi run command for first run attempt",
            fg="yellow",
            bold=True,
        )
        return True

    return False


@click.command()
@dev_options
@opendapi_run_options
@dapi_server_options
@github_options
@third_party_options
def cli(**kwargs):
    """
    This command combines the `opendapi generate` and `opendapi enrich` commands.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """
    if _should_skip_run_for_dbt_cloud(**kwargs):
        click.secho(
            "Skipping opendapi run command",
            fg="yellow",
            bold=True,
        )
        return

    click.secho(
        'Running "opendapi generate" to generate DAPI files...',
        fg="green",
        bold=True,
    )

    generate_params = generate_cli.params
    generate_kwargs = {key.name: kwargs.get(key.name) for key in generate_params}
    with click.Context(generate_cli) as ctx:
        ctx.invoke(generate_cli, **generate_kwargs)

    click.secho(
        'Running "opendapi enrich" to validate and enrich DAPI files...',
        fg="green",
        bold=True,
    )
    enrich_params = enrich_cli.params
    enrich_kwargs = {key.name: kwargs.get(key.name) for key in enrich_params}

    # Invoke enrich_cli using the click.Context.invoke method
    with click.Context(enrich_cli) as ctx:
        ctx.invoke(enrich_cli, **enrich_kwargs)
