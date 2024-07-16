"""dapi validator for prisma schemas"""

# pylint: disable=too-many-locals, too-many-instance-attributes, R0801, too-many-statements

import os
from dataclasses import dataclass
from typing import Dict, List
from typing import Optional as OptionalType

from pyparsing import (
    Group,
    Keyword,
    OneOrMore,
    Optional,
    SkipTo,
    Suppress,
    Word,
    ZeroOrMore,
    alphanums,
    delimitedList,
    identbodychars,
    identchars,
    nestedExpr,
    quoted_string,
    remove_quotes,
    restOfLine,
)

from opendapi.config import (
    construct_application_full_path,
    construct_dapi_source_sink_from_playbooks,
    construct_owner_team_urn_from_playbooks,
    is_model_in_allowlist,
)
from opendapi.defs import OPENDAPI_SPEC_URL
from opendapi.utils import find_files_with_suffix
from opendapi.validators.dapi.base import DapiValidator


@dataclass
class Column:
    """Data class for a prisma column definition"""

    name: str
    data_type: str
    options: dict
    is_enum: bool = False

    def _prisma_type_to_dapi_datatype(self, prisma_type: str) -> str:
        """Convert the Prisma data type to DAPI data type"""
        if self.is_enum:
            return f"enum:{prisma_type}"
        return prisma_type.lower()

    def for_dapi(self) -> dict:
        """Return the column as a dictionary for DAPI."""
        return {
            "name": self.options.get("db_field") or self.name,
            "data_type": self._prisma_type_to_dapi_datatype(self.data_type),
            "description": None,
            "is_pii": None,
            "is_nullable": self.options.get("nullable", False),
            "access": "private",
        }


@dataclass
class Table:
    """Data class for a prisma table definition"""

    table_name: str
    table_options: dict
    primary_keys: List[str]
    parsed_columns: List["Column"]
    parsed_indices: List["Index"]
    app_full_path: str
    schema_full_path: str
    org_name_snakecase: str
    playbooks: OptionalType[List] = None
    is_allowlisted: OptionalType[bool] = None

    def construct_urn(self) -> str:
        """Construct the URN for the table."""
        return f"{self.org_name_snakecase}.prisma.{self.app_name}.{self.table_name}"

    def construct_datastores(self) -> List[str]:
        """Get the datastores for the table."""
        return (
            construct_dapi_source_sink_from_playbooks(self.playbooks, self.table_name)
            if self.playbooks
            else {"sources": [], "sinks": []}
        )

    def construct_team_urn(self) -> OptionalType[str]:
        """Construct the team URN for the table."""
        return (
            construct_owner_team_urn_from_playbooks(
                self.playbooks, self.table_name, self.schema_full_path
            )
            if self.playbooks
            else None
        )

    def construct_dapi_location(self) -> str:
        """Construct the DAPI location for the table."""

        path_split = os.path.split(self.app_full_path)
        app_path = path_split[0] if path_split[1] == "prisma" else self.app_full_path
        return os.path.join(app_path, "dapis", f"{self.table_name}.dapi.yaml")

    @property
    def columns(self) -> List[Column]:
        """Get the columns in the table."""
        return self.parsed_columns

    @property
    def app_name(self) -> str:
        """Get the name of the application."""
        path_split = os.path.split(self.app_full_path)
        app_path = path_split[0] if path_split[1] == "prisma" else self.app_full_path
        return os.path.basename(app_path).replace("-", "_").replace(" ", "_").lower()


@dataclass
class ApplicationSchema:
    """Data class for a prisma application schema definition"""

    app_full_path: str
    schema_full_path: str
    org_name_snakecase: str
    playbooks: OptionalType[List] = None
    model_allowlist: OptionalType[List] = None

    @property
    def tables(self) -> List["Table"]:
        """Returns a list of tables in the schema"""

        with open(self.schema_full_path, encoding="utf-8") as schema_file:
            schema = schema_file.read()

        LBRACE, RBRACE, AT = map(Suppress, "{}@")  # pylint: disable=invalid-name
        identifier = Word(identchars, identbodychars)
        qtd_string = quoted_string().setParseAction(remove_quotes)

        # Define an enum and try to find all the enums in the input schema
        enum_defs = {}
        enums_pattern = (
            Suppress("enum")
            + identifier("name")
            + LBRACE
            + OneOrMore(Word(identchars))("enum_values")
            + RBRACE
        )

        for enum_def in enums_pattern.searchString(schema):
            enum_defs[enum_def.name] = list(enum_def.enum_values)

        # We will define a basic model pattern to COUNT the number of models in the schema
        # We will then use this to validate that all models were generated
        model_count_pattern = (
            Suppress("model")
            + identifier("table_name")
            + LBRACE
            + SkipTo(RBRACE)
            + RBRACE
        )

        expected_models = set(
            table.table_name for table in model_count_pattern.searchString(schema)
        )

        # Define the various datatypes
        integer = Keyword("Int")
        boolean = Keyword("Boolean")
        datetime = Keyword("DateTime")
        string = Keyword("String")
        unsupported = Keyword("Unsupported") + nestedExpr(ignore_expr=quoted_string())

        # Define a field type
        field_type = integer | datetime | string | boolean | unsupported | identifier

        # Define various keywords
        comment = Suppress(Group(Suppress("//") + restOfLine))

        default = Group(
            AT
            + Suppress(Keyword("default"))
            + nestedExpr(ignore_expr=quoted_string() | Keyword("value:"))("value")
        )("default")

        # A primary key is defined as @id
        id_attribute = Group(AT + Keyword("id"))("primary_key")

        # A compound id is defined as @@id([field1, field2, ...])
        compound_id = Group(
            Keyword("@@id")
            + Suppress("([")
            + delimitedList(identifier)
            + Suppress("])")
        )

        # Unique field is defined as @unique or @@unique([field1, field2, ...])
        unique = Group(AT + Keyword("unique"))
        compound_unique = Group(
            Keyword("@@unique")
            + Suppress("([")
            + delimitedList(identifier)
            + Suppress("])")
        )

        # A @@map definition is use to map a model definition to a different table name
        table_mapping = Group(
            Keyword("@@map")
            + Suppress("(")
            + Suppress(Optional(Keyword("name:")))
            + qtd_string("table_name")
            + Suppress(")")
        )

        # A @@schema definition is used to define the schema for a table
        schema_mapping = Group(
            Keyword("@@schema")
            + Suppress("(")
            + Suppress(Optional(Keyword("name:")))
            + qtd_string("schema_name")
            + Suppress(")")
        )

        # Index field is defined as @@index([field1, field2, ...])
        index = Suppress(Group(Keyword("@@index") + restOfLine))

        # Map fields are used to map a model definition to an underlying database field
        map_attribute = (
            Keyword("@map")
            + Suppress("(")
            + Suppress(Optional(Keyword("name:")))
            + qtd_string("db_field")
            + Suppress(")")
        )

        # This is used only in mongodb schema definitions
        # db_object_id = Suppress(Keyword("@db.ObjectId"))

        # Catch generic decorators
        generic_decorators = Suppress(AT + Word(alphanums + "."))

        decorators = Group(
            ZeroOrMore(
                default | id_attribute | unique | map_attribute | generic_decorators
            )
        )
        relationship = Suppress(
            Group(
                identifier("field")
                + identifier("model")
                + Optional("?")("nullable")
                + Optional("[]")("is_array")
                + AT
                + Keyword("relation")
                + restOfLine
            )
        )

        # A field is defined as
        # field_name field_type @default(value) @id @unique  // comment
        field = Group(
            identifier("name")
            + field_type("type")
            + Optional("?")("nullable")
            + Optional("[]")("is_array")
            + decorators("info")
            + Optional(comment)
        )("field")

        # A table is defined as
        # model table_name {
        #   field1 field_type @default(value) @id @unique  // comment
        #   field2 field_type @default(value) @id @unique  // comment
        #   ...
        #   @@id([field1, field2, ...])
        #   @@unique([field1, field2, ...])
        #   @@index([field1, field2, ...])
        # }
        models = (
            Suppress("model")
            + identifier("table_name")
            + LBRACE
            + Group(
                OneOrMore(
                    relationship
                    | field
                    | comment
                    | compound_id
                    | compound_unique
                    | index
                    | Suppress("@@ignore")
                    | table_mapping
                    | schema_mapping
                )
            )("info")
            + RBRACE
        )

        tables = []
        parsed_models = set()
        for table in models.searchString(schema):
            primary_keys = []
            columns = []
            table_name = table.table_name
            schema_name = None
            parsed_models.add(table_name)
            field_map = {}

            for row in table.info:
                if row.name:
                    # This is a parsed column
                    column = row
                    default_value = (
                        column.info.default.value.as_list()[0]
                        if column.info.default
                        else None
                    )
                    db_field = (
                        column.info.db_field
                        if "db_field" in column.info
                        else column.name
                    )
                    field_map[column.name] = db_field
                    data_type = column.type[0]

                    columns.append(
                        Column(
                            name=column.name,
                            data_type=data_type,
                            is_enum=data_type in enum_defs,
                            options={
                                "nullable": bool(column.nullable),
                                "is_array": bool(column.is_array),
                                "default_value": default_value,
                                "db_field": db_field,
                            },
                        )
                    )

                    if column.info.primary_key:
                        primary_keys.append(column.name)

                elif row[0] == "@@id":
                    # This is a parsed compound primary key
                    primary_keys = row[1:]

                elif row[0] == "@@map":
                    # Remove the quotes and store the table name
                    table_name = row[1]

                elif row[0] == "@@schema":
                    schema_name = row[1]

            primary_keys = [field_map[pk] for pk in primary_keys]

            tables.append(
                Table(
                    table_name=table.table_name,
                    table_options={
                        "enum_defs": enum_defs,
                        "table_name": table_name,
                        "schema_name": schema_name,
                    },
                    primary_keys=primary_keys,
                    parsed_columns=columns,
                    parsed_indices=[],
                    app_full_path=self.app_full_path,
                    schema_full_path=self.schema_full_path,
                    org_name_snakecase=self.org_name_snakecase,
                    playbooks=self.playbooks,
                    is_allowlisted=is_model_in_allowlist(
                        table.table_name,
                        self.schema_full_path,
                        self.model_allowlist,
                    ),
                )
            )

        missed_models = expected_models - parsed_models
        if missed_models:
            raise RuntimeError(
                f"Missed parsing the following models: {', '.join(missed_models)} "
                + f"from {self.schema_full_path}"
            )

        return tables


class PrismaDapiValidator(DapiValidator):
    """
    Validator class for DAPI files created for Prisma schemas
    """

    SCHEMA_FILE_PATH_SUFFIX = ".prisma"
    # This is used by the npm prisma-multischema package. We will exclude the
    # subschemas directory from the search and parse only the combined schema file.
    SCHEMA_FILE_EXCLUDE_DIRS = ["subschemas"]

    def _prisma_settings(self):
        """Get the settings frm the config file."""
        return self.config.get_integration_settings("prisma")

    def get_all_prisma_schema(self) -> List[ApplicationSchema]:
        """Get all Prisma schema files."""
        all_schema_files = find_files_with_suffix(
            self.root_dir,
            [f"{self.SCHEMA_FILE_PATH_SUFFIX}"],
            exclude_dirs=self.SCHEMA_FILE_EXCLUDE_DIRS,
        )
        return [
            ApplicationSchema(
                os.path.dirname(schema_file),
                schema_file,
                self.config.org_name_snakecase,
            )
            for schema_file in all_schema_files
        ]

    def _assert_schema_files_exist(self, applications: Dict[str, ApplicationSchema]):
        """Assert that the schema files exist."""
        errors = []
        for app in applications.values():
            if not os.path.exists(app.schema_full_path):
                errors.append(
                    f"Prisma Schema file {app.schema_full_path} "
                    f"not found for application {app.app_full_path}"
                )
        if errors:
            raise FileNotFoundError("/n".join(errors))

    def selected_applications(self) -> List[ApplicationSchema]:
        """Get the selected applications."""
        applications = {}
        config_settings = self._prisma_settings()
        if config_settings.get("applications", {}).get("include_all", True):
            for app in self.get_all_prisma_schema():
                applications[app.app_full_path] = app

        for app in config_settings.get("applications", {}).get("overrides", []):
            app_full_path = construct_application_full_path(
                self.root_dir, app["application_path"]
            )
            applications[app_full_path] = ApplicationSchema(
                app_full_path,
                os.path.join(
                    app_full_path,
                    app.get("schema_path", f"schema.{self.SCHEMA_FILE_PATH_SUFFIX}"),
                ),
                self.config.org_name_snakecase,
                app.get("playbooks"),
                app.get("model_allowlist"),
            )

        # Verify that all applications and their schema files exist
        self._assert_schema_files_exist(applications)

        return list(applications.values())

    def get_owner_team_urn_for_table(self, table: Table) -> str:
        """Get the owner team URN for a table."""

    def base_template_for_autoupdate(self) -> Dict[str, Dict]:
        result = {}
        for schema in self.selected_applications():
            for table in schema.tables:
                if table.is_allowlisted:
                    result[table.construct_dapi_location()] = {
                        "schema": OPENDAPI_SPEC_URL.format(
                            version=self.SPEC_VERSION,
                            entity="dapi",
                        ),
                        "type": "entity",
                        "urn": table.construct_urn(),
                        "owner_team_urn": table.construct_team_urn()
                        or self.get_owner_team_urn_for_table(table),
                        "description": None,
                        "datastores": table.construct_datastores(),
                        "fields": [field.for_dapi() for field in table.columns],
                        "primary_key": table.primary_keys,
                        "context": {
                            "service": table.app_name,
                            "integration": "prisma",
                            "rel_model_path": os.path.relpath(
                                schema.schema_full_path,
                                os.path.dirname(table.construct_dapi_location()),
                            ),
                        },
                    }
        return result


if __name__ == "__main__":  # pragma: no cover
    import sys
    from pprint import pprint

    pprint(
        ApplicationSchema(
            app_full_path=None,
            schema_full_path=sys.argv[1],
            org_name_snakecase="test_org",
        ).tables,
        sort_dicts=True,
    )
