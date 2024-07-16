# pylint: disable=unused-import
"""Validators for DAPI."""

from .activerecord import ActiveRecordDapiValidator
from .base import DapiValidator
from .dbt import DbtDapiValidator
from .prisma import PrismaDapiValidator
from .pynamodb import PynamodbDapiValidator
from .sequelize import SequelizeDapiValidator
from .sqlalchemy import SqlAlchemyDapiValidator
from .typeorm import TypeOrmDapiValidator

DAPI_INTEGRATIONS_VALIDATORS = {
    "activerecord": ActiveRecordDapiValidator,
    "dbt": DbtDapiValidator,
    "prisma": PrismaDapiValidator,
    # Need to support static parsing for PynamoDB
    "pynamodb": None,
    # Need to support static parsing for SQLAlchemy
    "sqlalchemy": None,
    "sequelize": SequelizeDapiValidator,
    "typeorm": TypeOrmDapiValidator,
}
