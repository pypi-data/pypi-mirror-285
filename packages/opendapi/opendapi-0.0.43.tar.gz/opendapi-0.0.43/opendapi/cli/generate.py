"""Entrypoint for the OpenDAPI CLI `opendapi generate` command."""

import os
from typing import Optional

import click

from opendapi.cli.common import (
    check_command_invocation_in_root,
    check_if_opendapi_config_is_valid,
    dev_options,
    get_opendapi_config,
    pretty_print_errors,
)
from opendapi.logging import LogDistKey, Timer
from opendapi.validators.base import MultiValidationError
from opendapi.validators.dapi import DAPI_INTEGRATIONS_VALIDATORS
from opendapi.validators.datastores import DatastoresValidator
from opendapi.validators.teams import TeamsValidator


@click.command()
@dev_options
def cli(
    local_spec_path: Optional[str],
):
    """
    Generate DAPI files for integrations specified in the OpenDAPI configuration file.

    For certain integrations such as DBT and PynamoDB, this command will also run
    additional commands in the respective integration directories to generate DAPI files.
    """
    click.secho(
        "\nHello, again!"
        " This command will use your `opendapi.config.yaml` configuration"
        " to generate DAPI files for your integrations.",
        fg="green",
    )
    click.secho("\n\nChecking if we are in the right repository...", fg="yellow")

    check_command_invocation_in_root()
    root_dir = os.getcwd()
    config = get_opendapi_config(root_dir, local_spec_path=local_spec_path)

    check_if_opendapi_config_is_valid(config)

    validators = [
        TeamsValidator,
        DatastoresValidator,
    ]

    click.secho("\n\nIdentifying your integrations...", fg="yellow")
    for intg, validator in DAPI_INTEGRATIONS_VALIDATORS.items():
        if config.has_integration(intg):
            if validator:
                validators.append(validator)
            click.secho(f"  Found {intg}...", fg="green")

    click.secho("\n\nGenerating DAPIs for your integrations...", fg="yellow")
    errors = []
    metrics_tags = {"org_name": config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.CLI_GENERATE, tags=metrics_tags):
        for validator in validators:
            inst_validator = validator(
                root_dir=root_dir,
                enforce_existence=True,
                should_autoupdate=True,
            )

            try:
                inst_validator.run()
            except MultiValidationError as exc:
                errors.append(exc)

    if errors:
        pretty_print_errors(errors)
        raise click.ClickException("Encountered one or more validation errors")

    click.secho("\n\nSuccess!", fg="green", bold=True)
