"""DAPI validator module"""

from typing import Dict, List, Tuple

from opendapi.config import construct_application_full_path
from opendapi.defs import DAPI_SUFFIX, OPENDAPI_SPEC_URL
from opendapi.utils import find_files_with_suffix
from opendapi.validators.base import BaseValidator, ValidationError


class DapiValidator(BaseValidator):
    """
    Validator class for DAPI files
    """

    SUFFIX = DAPI_SUFFIX
    SPEC_VERSION = "0-0-1"

    # Paths & keys to use for uniqueness check within a list of dicts when autoupdating
    AUTOUPDATE_UNIQUE_LOOKUP_KEYS: List[Tuple[List[str], str]] = [(["fields"], "name")]

    # Paths to disallow new entries when autoupdating
    AUTOUPDATE_DISALLOW_NEW_ENTRIES_PATH: List[List[str]] = [["fields"]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_field_names(self, content: dict) -> List[str]:
        """Get the field names"""
        return [field["name"] for field in content["fields"]]

    def _validate_primary_key_is_a_valid_field(self, file: str, content: Dict):
        """Validate if the primary key is a valid field"""
        primary_key = content.get("primary_key") or []
        field_names = self._get_field_names(content)
        for key in primary_key:
            if key not in field_names:
                raise ValidationError(
                    f"Primary key element {key} not a valid field in {file}"
                )

    def validate_content(self, file: str, content: Dict):
        """Validate the content of the files"""
        self._validate_primary_key_is_a_valid_field(file, content)
        super().validate_content(file, content)

    def base_dir_for_autoupdate(self) -> str:
        return self.root_dir

    def base_template_for_autoupdate(self) -> Dict[str, Dict]:
        """Set Autoupdate templates in {file_path: content} format"""
        return {
            f"{self.base_dir_for_autoupdate()}/sample_dataset.dapi.yaml": {
                "schema": OPENDAPI_SPEC_URL.format(
                    version=self.SPEC_VERSION, entity="dapi"
                ),
                "urn": "my_company.sample.dataset",
                "type": "entity",
                "description": "Sample dataset that shows how DAPI is created",
                "owner_team_urn": "my_company.sample.team",
                "datastores": {
                    "sources": [
                        {
                            "urn": "my_company.sample.datastore_1",
                            "data": {
                                "identifier": "sample_dataset",
                                "namespace": "sample_db.sample_schema",
                            },
                        }
                    ],
                    "sinks": [
                        {
                            "urn": "my_company.sample.datastore_2",
                            "data": {
                                "identifier": "sample_dataset",
                                "namespace": "sample_db.sample_schema",
                            },
                        }
                    ],
                },
                "fields": [
                    {
                        "name": "field1",
                        "data_type": "string",
                        "description": "Sample field 1 in the sample dataset",
                        "is_nullable": False,
                        "is_pii": False,
                        "access": "public",
                    }
                ],
                "primary_key": ["field1"],
                "context": {
                    "integration": "custom_dapi",
                },
            }
        }


class PackageScopedDapiValidatorBase(DapiValidator):
    """Base class for DAPI validators that are scoped to packages."""

    PACKAGE_JSON: str = "package.json"

    INTEGRATION_NAME: str = NotImplementedError
    LOOKUP_FILE_SUFFIXES: List[str] = NotImplementedError

    def _config_settings(self):
        """Get the settings frm the config file."""
        return self.config.get_integration_settings(self.INTEGRATION_NAME)

    def get_all_packages_with_configs(self) -> Dict[str, Dict]:
        """Get all package.json files in the project."""
        files = find_files_with_suffix(self.root_dir, [f"/{self.PACKAGE_JSON}"])
        packages = [filename.replace(f"/{self.PACKAGE_JSON}", "") for filename in files]
        config = self._config_settings()
        should_include_all = config.get("packages", {}).get("include_all", False)
        overrides = config.get("packages", {}).get("overrides", [])

        if should_include_all:
            result = {package: {} for package in packages}
        else:
            result = {}

        for override in overrides:
            package_path = construct_application_full_path(
                self.root_dir, override.get("package_path")
            )
            if package_path in packages:
                result[package_path] = override

        return result

    def get_all_files(self) -> List[str]:
        """Get all files in the project."""
        packages = self.get_all_packages_with_configs()
        files = []
        for pkg, config in packages.items():
            pkg_files = find_files_with_suffix(pkg, self.LOOKUP_FILE_SUFFIXES)
            for filename in pkg_files:
                with open(filename, encoding="utf-8") as f:
                    files.append((filename, f.read(), pkg, config))
        return files
