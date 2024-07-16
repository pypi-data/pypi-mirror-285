from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from chalk.integrations.named import load_integration_variable
from chalk.sql._internal.sql_source import BaseSQLSource, SQLSourceKind, TableIngestMixIn
from chalk.sql.protocols import SQLSourceWithTableIngestProtocol
from chalk.utils.log_with_context import get_logger
from chalk.utils.missing_dependency import missing_dependency_exception

if TYPE_CHECKING:
    import sqlalchemy as sa
    from sqlalchemy.engine import URL, Engine

try:
    import sqlalchemy as sa
except ImportError:
    sa = None

if sa is None:
    _supported_sqlalchemy_types_for_pa_csv_querying = ()
else:
    _supported_sqlalchemy_types_for_pa_csv_querying = (
        sa.BigInteger,
        sa.Boolean,
        sa.Float,
        sa.Integer,
        sa.String,
        sa.Text,
        sa.DateTime,
        sa.Date,
        sa.SmallInteger,
        sa.BIGINT,
        sa.BOOLEAN,
        sa.CHAR,
        sa.DATETIME,
        sa.FLOAT,
        sa.INTEGER,
        sa.SMALLINT,
        sa.TEXT,
        sa.TIMESTAMP,
        sa.VARCHAR,
    )

_logger = get_logger(__name__)


class TrinoSourceImpl(BaseSQLSource, TableIngestMixIn, SQLSourceWithTableIngestProtocol):
    kind = SQLSourceKind.trino

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[Union[int, str]] = None,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        engine_args: Optional[Dict[str, Any]] = None,
    ):
        try:
            import trino  # pyright: ignore
        except ImportError:
            raise missing_dependency_exception("chalkpy[trino]")
        self.name = name
        self.host = host or load_integration_variable(integration_name=name, name="TRINO_HOST")
        if self.host is None:
            raise ValueError("Failed to resolve trino required trino host.")

        self.port = (
            int(port)
            if port is not None
            else load_integration_variable(integration_name=name, name="TRINO_PORT", parser=int)
        )
        self.catalog = catalog or load_integration_variable(integration_name=name, name="TRINO_CATALOG")
        self.schema = schema or load_integration_variable(integration_name=name, name="TRINO_SCHEMA")
        self.user = user or load_integration_variable(integration_name=name, name="TRINO_USER")
        self.password = password or load_integration_variable(integration_name=name, name="TRINO_PASSWORD")
        self.ingested_tables: Dict[str, Any] = {}

        if engine_args is None:
            engine_args = {}

        if name:
            engine_args_from_ui = self._load_env_engine_args(name)
            for k, v in engine_args_from_ui.items():
                engine_args.setdefault(k, v)

        chalk_default_engine_args = {
            "session_properties": {"query_max_run_time": "1d"},
        }
        for k, v in chalk_default_engine_args.items():
            engine_args.setdefault(k, v)

        # We set the default isolation level to autocommit since the SQL sources are read-only, and thus
        # transactions are not needed
        # Setting the isolation level on the engine, instead of the connection, avoids
        # a DBAPI statement to reset the transactional level back to the default before returning the
        # connection to the pool
        BaseSQLSource.__init__(self, name=name, engine_args=engine_args, async_engine_args=None)

    def get_sqlglot_dialect(self) -> str | None:
        return "trino"

    def local_engine_url(self) -> URL:
        import trino.sqlalchemy as ts
        from sqlalchemy.engine import make_url

        return make_url(
            ts.URL(
                user=self.user,
                password=self.password,
                # host is checked for None in the constructor
                host=self.host,  # pyright: ignore
                port=self.port,
                catalog=self.catalog,
                schema=self.schema,
            )
        )

    def get_engine(self) -> Engine:
        from sqlalchemy.engine import create_engine

        if self._engine is None:
            self.register_sqlalchemy_compiler_overrides()
            self._check_engine_isolation_level()
            self._engine = create_engine(url=self.local_engine_url(), connect_args=self._engine_args)
        return self._engine
