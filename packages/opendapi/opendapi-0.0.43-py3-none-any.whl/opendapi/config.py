"""Manage the opendapi.config.yaml object"""

import os
import re
from typing import Dict, List, Optional

import requests
from jsonschema import validate as jsonschema_validate

from opendapi.defs import CONFIG_FILEPATH_FROM_ROOT_DIR
from opendapi.utils import make_snake_case, read_yaml_or_json

SUPPORTED_DAPI_INTEGRATIONS = [
    "activerecord",
    "dbt",
    "pynamodb",
    "sqlalchemy",
    "sequelize",
    "typeorm",
    "prisma",
]


def _extract_source_sink(playbook: dict, table_name: str) -> Dict:
    """Extract the source or sink from the playbook"""
    namespace = playbook.get("namespace")
    identifier = (
        f"{playbook.get('identifier_prefix')}{table_name}"
        if playbook.get("identifier_prefix")
        else table_name
    )
    data = {"identifier": identifier}
    if namespace:
        data["namespace"] = namespace
    return {"urn": playbook.get("datastore_urn"), "data": data}


def construct_dapi_source_sink_from_playbooks(playbooks: Dict, table_name: str) -> Dict:
    """Construct the source and sink from the playbook"""
    sources = []
    sinks = []
    for playbook in playbooks:
        if playbook.get("type") == "add_source_datastore":
            sources.append(_extract_source_sink(playbook, table_name))
        if playbook.get("type") == "add_sink_datastore":
            sinks.append(_extract_source_sink(playbook, table_name))
    return {"sources": sources, "sinks": sinks}


def construct_owner_team_urn_from_playbooks(
    playbooks: Dict, table_name: str, table_path: str
) -> Optional[str]:
    """Construct the team URN from the playbook"""
    for playbook in playbooks:
        if playbook.get("type") == "add_owner_team" and is_model_in_allowlist(
            table_name, table_path, playbook.get("model_allowlist")
        ):
            return playbook.get("team_urn")

    return None


def construct_application_full_path(root_dir: str, application_path: str) -> str:
    """Construct the full path to the application"""
    # we expect the application path to be relative to the root path anyway
    stripped_application_path = (
        application_path.lstrip("/").rstrip("/")
        if application_path
        else application_path
    )
    if not stripped_application_path:
        return root_dir
    return os.path.join(root_dir, stripped_application_path)


def is_model_in_allowlist(
    model_name: str, model_path: str, model_allowlist: List[str]
) -> bool:
    """Check if the model name is in the list of regex in model allowlist"""
    if not model_allowlist:
        return True

    model_path_filters = []
    model_name_filters = []
    for itm in model_allowlist:
        if itm.startswith("path:"):
            model_path_filters.append(itm.split("path:")[1])
        else:
            model_name_filters.append(itm)

    match_model_name = (
        any(
            re.compile(pattern, flags=re.IGNORECASE).match(model_name)
            for pattern in model_name_filters
        )
        if model_name
        else False
    )
    match_model_path = (
        any(
            re.compile(pattern, flags=re.IGNORECASE).match(model_path)
            for pattern in model_path_filters
        )
        if model_path
        else False
    )

    return match_model_name or match_model_path


class OpenDAPIConfig:
    """Manage the opendapi.config.yaml object"""

    def __init__(self, root_dir: str, local_spec_path: Optional[str] = None):
        self.root_dir = root_dir
        self.config = self._read_config()
        self.local_spec_path = local_spec_path

    def _read_config(self) -> dict:
        """Read the contents of the opendapi.config.yaml file"""
        config_file = self.config_full_path(self.root_dir)
        if os.path.exists(config_file):
            content = read_yaml_or_json(config_file)
            if "schema" not in content:
                raise ValueError(
                    f"Invalid OpenDAPI config file: {config_file} missing schema"
                )
            return content
        raise FileNotFoundError(f"OpenDAPI config file not found: {config_file}")

    @property
    def urn(self) -> str:
        """Return the repository name"""
        return self.config["repository"]["urn"]

    @property
    def org_name(self) -> str:
        """Return the organization name"""
        return self.config["organization"]["name"]

    @property
    def org_name_snakecase(self) -> str:
        """Return the organization name in snake case"""
        return make_snake_case(self.org_name)

    @property
    def org_email_domain(self) -> str:
        """Return the organization email domain"""
        return self.config["organization"]["email_domain"]

    @staticmethod
    def config_full_path(root_dir: str) -> str:
        """Return the full path to the opendapi.config.yaml file"""
        return os.path.join(root_dir, CONFIG_FILEPATH_FROM_ROOT_DIR)

    def get_integration_types(self) -> List[str]:
        """Return the list of DAPI integrations"""
        integration_settings = self.config["dapis"]["integrations"]
        integration_types = [
            integration["type"] for integration in integration_settings
        ]
        return integration_types

    def has_integration(self, integration_type: str) -> bool:
        """Return True if the integration type is in the list of integrations"""
        return integration_type in self.get_integration_types()

    def get_integration_settings(self, integration_type: str) -> Dict:
        """Return the settings for the integration type"""
        integration_settings = self.config["dapis"]["integrations"]
        for integration in integration_settings:
            if integration["type"] == integration_type:
                return integration
        raise ValueError(
            f"Integration type not found in {CONFIG_FILEPATH_FROM_ROOT_DIR}: {integration_type}"
        )

    def get_mainline_branch(self) -> str:
        """Return the mainline branch"""
        return self.config["repository"]["mainline_branch"]

    def validate(self) -> None:
        """Return True if the config file is valid"""
        if self.local_spec_path is not None:
            schema_file = os.path.basename(self.config["schema"])
            schema_path = os.path.join(self.local_spec_path, schema_file)
            schema = read_yaml_or_json(schema_path)
        else:
            schema = requests.get(self.config["schema"], timeout=2).json()

        jsonschema_validate(self.config, schema)
