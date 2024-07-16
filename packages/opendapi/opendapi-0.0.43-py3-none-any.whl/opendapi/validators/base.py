# pylint: disable=too-many-instance-attributes
"""Validator class for DAPI and related files"""
import os
from typing import Dict, List, Tuple

import requests
from deepmerge import STRATEGY_END, Merger, extended_set
from jsonschema import ValidationError as JsonValidationError
from jsonschema import validate as jsonschema_validate
from ruamel.yaml import YAML

from opendapi.config import OpenDAPIConfig
from opendapi.defs import OPENDAPI_URL
from opendapi.logging import LogCounterKey, increment_counter
from opendapi.utils import (
    find_files_with_suffix,
    read_yaml_or_json,
    sort_dict_by_keys,
    sorted_yaml_dump,
)


class ValidationError(Exception):
    """Exception raised for validation errors"""


class MultiValidationError(ValidationError):
    """Exception raised for multiple validation errors"""

    def __init__(self, errors: List[str], prefix_message: str = None):
        self.errors = errors
        self.prefix_message = prefix_message

    def __str__(self):
        return (
            f"\n\n{self.prefix_message}\n\n"
            + f"Found {len(self.errors)} errors:\n\n"
            + "\n\n".join(self.errors)
        )


class BaseValidator:
    """Base validator class for DAPI and related files"""

    SUFFIX: List[str] = NotImplemented

    # Paths & keys to use for uniqueness check within a list of dicts when autoupdating
    AUTOUPDATE_UNIQUE_LOOKUP_KEYS: List[Tuple[List[str], str]] = []

    # Paths to disallow new entries when autoupdating
    AUTOUPDATE_DISALLOW_NEW_ENTRIES_PATH: List[List[str]] = []

    SPEC_VERSION: str = NotImplemented

    def __init__(
        self,
        root_dir: str,
        enforce_existence: bool = False,
        should_autoupdate: bool = False,
    ):
        self.schema_cache = {}
        self.yaml = YAML()
        self.root_dir = root_dir
        self.enforce_existence = enforce_existence
        self.should_autoupdate = should_autoupdate
        self.config: OpenDAPIConfig = OpenDAPIConfig(root_dir)
        if self.should_autoupdate and not self.enforce_existence:
            raise ValueError(
                "should_autoupdate cannot be True if enforce_existence is False"
            )
        self.parsed_files: Dict[str, Dict] = self._get_file_contents_for_suffix(
            self.SUFFIX
        )

    def base_dir_for_autoupdate(self) -> str:
        """Get the base directory for the spec files"""
        return self.root_dir

    def _get_merger(self):
        """Get the merger object for deepmerge"""

        def _get_match_using_lookup_keys(
            list_to_match: List, itm: Dict, lookup_keys: List[str]
        ) -> List[Dict]:
            """Get the match from the list using the lookup keys"""
            lookup_vals = [(k, itm.get(k)) for k in lookup_keys if itm.get(k)]
            return [
                n
                for n in list_to_match
                if lookup_vals and n.get(lookup_vals[0][0]) == lookup_vals[0][1]
            ]

        def _autoupdate_merge_strategy_for_dict_lists(config, path, base, nxt):
            """append items without duplicates in nxt to base and handles dict appropriately"""
            if (base and not isinstance(base[0], dict)) or (
                nxt and not isinstance(nxt[0], dict)
            ):
                return STRATEGY_END
            result = []
            autoupdate_unique_lookup_keys_for_path = [
                v for k, v in self.AUTOUPDATE_UNIQUE_LOOKUP_KEYS if k == path
            ]
            for idx, itm in enumerate(base):
                filter_nxt_items = _get_match_using_lookup_keys(
                    nxt, itm, autoupdate_unique_lookup_keys_for_path
                )
                if filter_nxt_items:
                    result.append(
                        config.value_strategy(path + [idx], itm, filter_nxt_items[0])
                    )
                else:
                    result.append(itm)

            if path in self.AUTOUPDATE_DISALLOW_NEW_ENTRIES_PATH:
                return result

            # Sort dict by keys to prevent duplicates because of YAML re-ordering
            result_as_set = extended_set.ExtendedSet(
                [sort_dict_by_keys(itm) for itm in result]
            )

            # This deduplicates the result - although not the intent, it is probably okay
            addable_candidates = [
                n for n in nxt if sort_dict_by_keys(n) not in result_as_set
            ]

            to_be_added = []

            if autoupdate_unique_lookup_keys_for_path:
                # Add only items from nxt ONLY
                # if they are not already merged earlier using the lookup keys
                #   OR if they are not already present in the result
                for itm in addable_candidates:
                    result_match = _get_match_using_lookup_keys(
                        result, itm, autoupdate_unique_lookup_keys_for_path
                    ) or _get_match_using_lookup_keys(
                        to_be_added, itm, autoupdate_unique_lookup_keys_for_path
                    )
                    if result_match:
                        continue

                    to_be_added.append(itm)
            else:
                to_be_added = addable_candidates

            return result + to_be_added

        return Merger(
            [
                (list, [_autoupdate_merge_strategy_for_dict_lists, "append_unique"]),
                (dict, "merge"),
                (set, "union"),
            ],
            ["override"],
            ["override"],
        )

    def _assert_dapi_location_is_valid(self, dapi_location: str) -> None:
        """Assert that the DAPI location is valid"""
        if not dapi_location.startswith(self.base_dir_for_autoupdate()):
            raise AssertionError(
                "Dapi location must be in the base dir, "
                "otherwise validator cannot find these files"
            )

    def _get_files_for_suffix(self, suffixes: List[str]):
        """Get all files in the root directory with given suffixes"""
        all_files = find_files_with_suffix(self.root_dir, suffixes)
        return [
            file
            for file in all_files
            if not file.endswith(OpenDAPIConfig.config_full_path(self.root_dir))
        ]

    def _read_yaml_or_json(self, file: str):
        """Read the file as yaml or json"""
        try:
            return read_yaml_or_json(file, self.yaml)
        except ValueError as exc:
            raise ValidationError(f"Unsupported file type for {file}") from exc

    def _get_file_contents_for_suffix(self, suffixes: List[str]):
        """Get the contents of all files in the root directory with given suffixes"""
        files = self._get_files_for_suffix(suffixes)
        contents = {}
        for file in files:
            contents[file] = self._read_yaml_or_json(file)
        return contents

    def validate_existance(self):
        """Validate that the files exist"""
        if self.enforce_existence and not self.parsed_files:
            raise ValidationError(
                f"OpenDapi {self.__class__.__name__} error: No files found in {self.root_dir}"
            )

    def _fetch_schema(self, jsonschema_ref: str) -> dict:
        """Fetch a schema from a URL and cache it in the requests cache"""
        if not jsonschema_ref.startswith(OPENDAPI_URL):
            raise ValidationError(
                f"Unsupported schema found at {jsonschema_ref} for "
                f"- not hosted on {OPENDAPI_URL}"
            )
        try:
            self.schema_cache[jsonschema_ref] = (
                self.schema_cache.get(jsonschema_ref)
                or requests.get(jsonschema_ref, timeout=2).json()
            )
        except requests.exceptions.RequestException as exc:
            error_message = f"Error fetching schema {jsonschema_ref}: {str(exc)}"
            raise ValidationError(error_message) from exc

        return self.schema_cache[jsonschema_ref]

    def validate_schema(self, file: str, content: Dict):
        """Validate the yaml file for schema adherence"""
        if "schema" not in content:
            raise ValidationError(f"Schema not found in {file}")

        jsonschema_ref = content["schema"]

        try:
            schema = self._fetch_schema(jsonschema_ref)
        except ValidationError as exc:
            error_message = f"Validation error for {file}: \n{str(exc)}"
            raise ValidationError(error_message) from exc

        try:
            jsonschema_validate(content, schema)
        except JsonValidationError as exc:
            error_message = f"Validation error for {file}: \n{str(exc)}"
            raise ValidationError(error_message) from exc

    def base_template_for_autoupdate(self) -> Dict[str, Dict]:
        """Set Autoupdate templates in {file_path: content} format"""
        raise NotImplementedError

    def autoupdate(self):
        """Autocreate or update the files"""
        for file, base_content in self.base_template_for_autoupdate().items():
            self._assert_dapi_location_is_valid(file)
            content = base_content
            if file in self.parsed_files:
                new_content = self._get_merger().merge(content, self.parsed_files[file])
                # Move on if the content is the same
                if self.parsed_files[file] == new_content:
                    continue
            else:
                new_content = content

            # Create the directory if it does not exist
            dir_name = os.path.dirname(file)
            os.makedirs(dir_name, exist_ok=True)

            with open(file, "w", encoding="utf-8") as file_handle:
                jsonschema_ref = new_content.get("schema")
                json_spec = (
                    self._fetch_schema(jsonschema_ref) if jsonschema_ref else None
                )
                sorted_yaml_dump(
                    new_content,
                    file_handle,
                    json_spec=json_spec,
                    yaml=self.yaml,
                )

        self.parsed_files = self._get_file_contents_for_suffix(self.SUFFIX)

    def custom_content_validations(self, file: str, content: Dict):
        """Custom content validations if any desired"""

    def validate_content(self, file: str, content: Dict):
        """Validate the content of the files"""
        self.custom_content_validations(file, content)

    def validate(self):
        """Run the validators"""
        # Update the files after autoupdate
        self.parsed_files = self._get_file_contents_for_suffix(self.SUFFIX)

        # Check if the files exist if enforce_existence is True
        if self.enforce_existence:
            self.validate_existance()

        # Collect the errors for all the files
        errors = []
        for file, content in self.parsed_files.items():
            try:
                self.validate_schema(file, content)
            except ValidationError as exc:
                errors.append(str(exc))
            else:
                try:
                    self.validate_content(file, content)
                except ValidationError as exc:
                    errors.append(str(exc))

        # Increment the counter for the number of items validated
        tags = {
            "validator_type": self.__class__.__name__,
            "org_name": self.config.org_name_snakecase,
        }
        increment_counter(
            LogCounterKey.VALIDATOR_ITEMS,
            value=len(self.parsed_files),
            tags=tags,
        )
        if errors:
            # Increment the counter for the number of errors
            increment_counter(
                LogCounterKey.VALIDATOR_ERRORS,
                value=len(errors),
                tags=tags,
            )
            raise MultiValidationError(
                errors, f"OpenDapi {self.__class__.__name__} error"
            )

    def run(self):
        """Autoupdate and validate"""
        if self.should_autoupdate:
            self.autoupdate()
        self.validate()
