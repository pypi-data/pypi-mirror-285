from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from digitalhub_core.stores.objects.base import Store, StoreConfig
from digitalhub_core.utils.exceptions import StoreError
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import LegacyRow
from sqlalchemy.exc import SQLAlchemyError


class SQLStoreConfig(StoreConfig):
    """
    SQL store configuration class.
    """

    host: str
    """SQL host."""

    port: int
    """SQL port."""

    user: str
    """SQL user."""

    password: str
    """SQL password."""

    database: str
    """SQL database name."""


class SqlStore(Store):
    """
    SQL store class. It implements the Store interface and provides methods to fetch and persist
    artifacts on SQL based storage.
    """

    def __init__(self, name: str, store_type: str, config: SQLStoreConfig) -> None:
        """
        Constructor.

        Parameters
        ----------
        config : SQLStoreConfig
            SQL store configuration.

        See Also
        --------
        Store.__init__
        """
        super().__init__(name, store_type)
        self.config = config

    ############################
    # IO methods
    ############################

    def download(self, src: str, dst: str | None = None) -> str:
        """
        Download an artifact from SQL based storage.

        See Also
        --------
        fetch_artifact
        """
        return self._registry.get(src, self.fetch_artifact(src, dst))

    def fetch_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Fetch an artifact from SQL based storage. If the destination is not provided,
        a temporary directory will be created and the artifact will be saved there.

        Parameters
        ----------
        src : str
            Table name.
        dst : str
            The destination of the artifact on local filesystem.

        Returns
        -------
        str
            Returns a file path.
        """
        dst = dst if dst is not None else self._build_temp(src)
        dst = str(Path(dst) / "data.parquet")
        schema = self._get_schema(src)
        table = self._get_table_name(src)
        return self._download_table(schema, table, dst)

    def upload(self, src: str, dst: str | None = None) -> str:
        """
        Method to upload an artifact to the backend. Please note that this method is not implemented
        since the SQL store is not meant to upload artifacts.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("SQL store does not support upload.")

    def persist_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to persist an artifact. Note that this method is not implemented
        since the SQL store is not meant to write artifacts.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("SQL store does not support persist_artifact.")

    def get_file_info(self, path: str, src_path: str | None = None) -> dict | None:
        """
        Method to get file metadata.

        Parameters
        ----------
        path : str
            The path of the file.
        src_path : str
            The source path of the file.

        Returns
        -------
        None
        """

    ############################
    # Private helper methods
    ############################

    def _get_connection_string(self) -> str:
        """
        Get the connection string.

        Returns
        -------
        str
            The connection string.
        """
        return (
            f"postgresql://{self.config.user}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/{self.config.database}"
        )

    def _get_engine(self, schema: str | None = None) -> Engine:
        """
        Create engine from connection string.

        Parameters
        ----------
        schema : str
            The schema.

        Returns
        -------
        Engine
            An SQLAlchemy engine.
        """
        connection_string = self._get_connection_string()
        if not isinstance(connection_string, str):
            raise StoreError("Connection string must be a string.")
        try:
            if schema is not None:
                return create_engine(connection_string, connect_args={"options": f"-csearch_path={schema}"})
            return create_engine(connection_string)
        except Exception as ex:
            raise StoreError(f"Something wrong with connection string. Arguments: {str(ex.args)}")

    def _check_factory(self, schema: str | None = None) -> Engine:
        """
        Check if the database is accessible and return the engine.

        Parameters
        ----------
        schema : str
            The schema.

        Returns
        -------
        Engine
            The database engine.
        """
        engine = self._get_engine(schema)
        self._check_access_to_storage(engine)
        return engine

    @staticmethod
    def _parse_path(path: str) -> dict:
        """
        Parse the path and return the components.

        Parameters
        ----------
        path : str
            The path.

        Returns
        -------
        dict
            A dictionary containing the components of the path.
        """
        # Parse path
        err_msg = "Invalid SQL path. Must be sql://<database>/<schema>/<table> or sql://<database>/<table>"
        protocol, pth = path.split("://")
        components = pth.split("/")
        if protocol != "sql" or not (2 <= len(components) <= 3):
            raise ValueError(err_msg)

        # Get components
        database = components[0]
        table = components[-1]
        schema = components[1] if len(components) == 3 else "public"
        return {"database": database, "schema": schema, "table": table}

    def _get_schema(self, uri: str) -> str:
        """
        Get the name of the SQL schema from the URI.

        Parameters
        ----------
        uri : str
            The URI.

        Returns
        -------
        str
            The name of the SQL schema.
        """
        return str(self._parse_path(uri).get("schema"))

    def _get_table_name(self, uri: str) -> str:
        """
        Get the name of the table from the URI.

        Parameters
        ----------
        uri : str
            The URI.

        Returns
        -------
        str
            The name of the table
        """
        return str(self._parse_path(uri).get("table"))

    @staticmethod
    def _check_access_to_storage(engine: Engine) -> None:
        """
        Check if there is access to the storage.

        Parameters
        ----------
        engine : Engine
            An SQLAlchemy engine.

        Returns
        -------
        None

        Raises
        ------
        StoreError
            If there is no access to the storage.
        """
        try:
            engine.connect()
        except SQLAlchemyError:
            engine.dispose()
            raise StoreError("No access to db!")

    def _download_table(self, schema: str, table: str, dst: str) -> str:
        """
        Download a table from SQL based storage.

        Parameters
        ----------
        schema : str
            The origin schema.
        table : str
            The origin table.
        dst : str
            The destination path.

        Returns
        -------
        str
            The destination path.
        """
        engine = self._check_factory(schema=schema)
        self._check_local_dst(dst)

        # Read the table from the database
        sa_table = Table(table, MetaData(), autoload_with=engine)
        query = sa_table.select()
        with engine.begin() as conn:
            result: list[LegacyRow] = conn.execute(query).fetchall()

        # Parse the result
        data = self._parse_result(result)

        # Convert the result to a pyarrow table and
        # write the pyarrow table to a Parquet file
        arrow_table = pa.Table.from_pydict(data)
        pq.write_table(arrow_table, dst)

        engine.dispose()

        return dst

    @staticmethod
    def _parse_result(result: list[LegacyRow]) -> dict:
        """
        Convert a list of list of tuples to a dict.

        Parameters
        ----------
        result : list[LegacyRow]
            The data to convert.

        Returns
        -------
        dict
            The converted data.
        """
        data_list = [row.items() for row in result]
        data = {}
        for row in data_list:
            for column_name, value in row:
                if column_name not in data:
                    data[column_name] = []
                data[column_name].append(value)
        return data

    ############################
    # Store interface methods
    ############################

    @staticmethod
    def is_local() -> bool:
        """
        Check if the store is local.

        Returns
        -------
        bool
            False
        """
        return False
