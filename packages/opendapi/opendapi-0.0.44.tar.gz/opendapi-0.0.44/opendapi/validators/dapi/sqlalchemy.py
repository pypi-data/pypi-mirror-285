"""SqlAlchemy DAPI validator module"""

from typing import TYPE_CHECKING, Dict, List

from opendapi.defs import OPENDAPI_SPEC_URL
from opendapi.validators.dapi.base import DapiValidator

if TYPE_CHECKING:
    from sqlalchemy import MetaData, Table  # pragma: no cover


class SqlAlchemyDapiValidator(DapiValidator):
    """
    Validator class for DAPI files created for SQLAlchemy datasets

    Example usage:

    from opendapi.validators.sqlalchemy import SqlAlchemyDapiValidator
    from my_service.db.sqlalchemy import Base

    class MySqlAlchemyDapiValidator(SqlAlchemyDapiValidator):
        def get_sqlalchemy_metadata_objects(self):
            return [Base.metadata]

        def build_datastores_for_table(self, table):
            return {
                "sources": [
                    {
                        "urn": "my_company.datastore.mysql",
                        "data": {
                            "identifier": table.name,
                            "namespace": table.schema,
                        },
                    },
                ],
                "sinks": [
                    {
                        "urn": "my_company.datastore.snowflake",
                        "data": {
                            "identifier": table.name,
                            "namespace": table.schema,
                        }
                    }
                ]
            }

        def build_owner_team_urn_for_table(self, table):
            return f"my_company.sample.team.{table.name}"

        def build_urn_for_table(self, table):
            return f"my_company.sample.dataset.{table.name}"

        def build_dapi_location_for_table(self, table):
            return f"{self.base_dir_for_autoupdate()}/sqlalchemy/{table.name}.dapi.yaml"

    """

    def get_sqlalchemy_metadata_objects(self) -> List["MetaData"]:
        """Get the SQLAlchemy metadata objects"""
        raise NotImplementedError

    def get_sqlalchemy_tables(self) -> List["Table"]:
        """Get the SQLAlchemy models"""
        tables = []
        for metadata in self.get_sqlalchemy_metadata_objects():
            tables.extend(metadata.sorted_tables)
        return tables

    def build_datastores_for_table(self, table: "Table") -> Dict:
        """Build the datastores for the table"""
        raise NotImplementedError

    def build_owner_team_urn_for_table(self, table: "Table") -> str:
        """Build the owner for the table"""
        raise NotImplementedError

    def build_urn_for_table(self, table: "Table") -> str:
        """Build the urn for the table"""
        raise NotImplementedError

    def _sqlalchemy_column_type_to_dapi_datatype(self, column_type: str) -> str:
        """Convert the SQLAlchemy column type to DAPI data type"""
        return str(column_type).lower()

    def build_fields_for_table(self, table: "Table") -> List[Dict]:
        """Build the fields for the table"""
        fields = []
        for column in table.columns:
            fields.append(
                {
                    "name": str(column.name),
                    "data_type": self._sqlalchemy_column_type_to_dapi_datatype(
                        column.type
                    ),
                    "description": None,
                    "is_nullable": column.nullable,
                    "is_pii": None,
                    "access": "private",
                }
            )
        fields.sort(key=lambda x: x["name"])
        return fields

    def build_primary_key_for_table(self, table: "Table") -> List[str]:
        """Build the primary key for the table"""
        primary_key = []
        for column in table.columns:
            if column.primary_key:
                primary_key.append(str(column.name))
        return primary_key

    def build_dapi_location_for_table(self, table: "Table") -> str:
        """Build the relative path for the DAPI file"""
        return f"{self.base_dir_for_autoupdate()}/dapis/sqlalchemy/{table.name.lower()}.dapi.yaml"

    def base_template_for_autoupdate(self) -> Dict[str, Dict]:
        """Build the base template for autoupdate"""
        result = {}
        for table in self.get_sqlalchemy_tables():
            result[self.build_dapi_location_for_table(table)] = {
                "schema": OPENDAPI_SPEC_URL.format(
                    version=self.SPEC_VERSION,
                    entity="dapi",
                ),
                "urn": self.build_urn_for_table(table),
                "type": "entity",
                "description": None,
                "owner_team_urn": self.build_owner_team_urn_for_table(table),
                "datastores": self.build_datastores_for_table(table),
                "fields": self.build_fields_for_table(table),
                "primary_key": self.build_primary_key_for_table(table),
                # TODO: Figure out how to get the service name and relative model path  # pylint: disable=W0511
                "context": {
                    "integration": "sqlalchemy",
                },
            }
        return result
