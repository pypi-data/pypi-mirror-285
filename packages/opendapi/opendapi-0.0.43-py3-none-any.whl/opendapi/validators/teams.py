"""Teams validator module"""

import os
from typing import Dict, List, Tuple

from opendapi.defs import DEFAULT_DAPIS_DIR, OPENDAPI_SPEC_URL, TEAMS_SUFFIX
from opendapi.validators.base import BaseValidator, ValidationError


class TeamsValidator(BaseValidator):
    """
    Validator class for Teams files
    """

    SUFFIX = TEAMS_SUFFIX
    SPEC_VERSION = "0-0-1"

    # Paths & keys to use for uniqueness check within a list of dicts when autoupdating
    AUTOUPDATE_UNIQUE_LOOKUP_KEYS: List[Tuple[List[str], str]] = [(["teams"], "urn")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team_urns = self._collect_team_urns()

    def _collect_team_urns(self) -> List[str]:
        """Collect all the team urns"""
        team_urns = []
        for _, content in self.parsed_files.items():
            for team in content["teams"]:
                team_urns.append(team["urn"])
        return team_urns

    def _validate_parent_team_urn(self, file: str, content: dict):
        """Validate if the parent team urn is valid"""
        teams = content.get("teams") or []
        for team in teams:
            if (
                team.get("parent_team_urn")
                and team["parent_team_urn"] not in self.team_urns
            ):
                raise ValidationError(
                    f"Parent team urn {team['parent_team_urn']}"
                    f" not found in {team['urn']} in {file}"
                )

    def validate_content(self, file: str, content: Dict):
        """Validate the content of the files"""
        self._validate_parent_team_urn(file, content)
        super().validate_content(file, content)

    def base_dir_for_autoupdate(self) -> str:
        return os.path.join(self.root_dir, DEFAULT_DAPIS_DIR)

    def base_template_for_autoupdate(self) -> Dict[str, Dict]:
        """Set Autoupdate templates in {file_path: content} format"""
        return {
            f"{self.base_dir_for_autoupdate()}/{self.config.org_name_snakecase}.teams.yaml": {
                "schema": OPENDAPI_SPEC_URL.format(
                    version=self.SPEC_VERSION, entity="teams"
                ),
                "organization": {"name": self.config.org_name},
                "teams": [],
            }
        }
