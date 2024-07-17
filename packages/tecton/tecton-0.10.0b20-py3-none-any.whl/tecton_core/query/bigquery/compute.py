import io
import json
import logging
from typing import Optional
from typing import Union

import attrs
import pandas
import pyarrow
import pyarrow.parquet as pq
from google.api_core import client_info
from google.cloud import bigquery
from google.cloud.bigquery import _pandas_helpers

from tecton_core import _gen_version
from tecton_core import conf
from tecton_core.errors import TectonInternalError
from tecton_core.query.dialect import Dialect
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.query_tree_compute import ComputeMonitor
from tecton_core.query.query_tree_compute import SQLCompute
from tecton_core.query.sql_compat import CompatFunctions
from tecton_core.schema import Schema
from tecton_core.schema_validation import cast_batch
from tecton_core.schema_validation import tecton_schema_to_arrow_schema
from tecton_core.secrets import SecretResolver
from tecton_core.specs import BigquerySourceSpec


@attrs.define
class BigqueryCompute(SQLCompute):
    is_debug: bool = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")

    def get_dialect(self) -> Dialect:
        return Dialect.BIGQUERY

    def run_sql(
        self,
        sql_string: str,
        return_dataframe: bool = False,
        expected_output_schema: Optional[Schema] = None,
        monitor: Optional[ComputeMonitor] = None,
    ) -> Optional[pyarrow.RecordBatchReader]:
        # Although `sqlparse.format` may be helpful, it has been slow at times. BQ error logs are generally good.
        if self.is_debug:
            logging.warning(f"BigQuery QT: run SQL:\n{sql_string}")

        if monitor:
            monitor.set_query(sql_string)

        client = BigquerySessionManager.get_client()
        query_job_config = BigquerySessionManager.get_query_job_config()
        query_job = client.query(sql_string, job_config=query_job_config).result()

        if not return_dataframe:
            return

        if expected_output_schema:
            output_schema = tecton_schema_to_arrow_schema(expected_output_schema)
        else:
            output_schema = _pandas_helpers.bq_to_arrow_schema(query_job.schema)

        def batch_iterator():
            for batch in query_job.to_arrow_iterable():
                yield cast_batch(batch, output_schema)

        return pyarrow.RecordBatchReader.from_batches(output_schema, batch_iterator())

    def register_temp_table(
        self, table_name: str, table_or_reader: Union[pyarrow.Table, pyarrow.RecordBatchReader]
    ) -> None:
        if self.is_debug:
            logging.warning(f"BigQuery QT: Registering temp table: _SESSION.{table_name}")

        client = BigquerySessionManager.get_client()
        load_job_config = BigquerySessionManager.get_load_job_config()
        load_job_config.source_format = bigquery.SourceFormat.PARQUET
        load_job_config.autodetect = True

        # Note: load_table_from_dataframe converts pandas to parquet and calls load_table_from_file
        # So we write the arrow batches directly to parquet without converting to a pandas dataframe
        with io.BytesIO() as stream:
            if isinstance(table_or_reader, pyarrow.RecordBatchReader):
                writer = None
                for batch in table_or_reader:
                    if writer is None:
                        writer = pq.ParquetWriter(stream, batch.schema)
                    writer.write_batch(batch)
                if writer:
                    writer.close()
            else:
                pq.write_table(table_or_reader, stream)
            stream.seek(0)
            load_job = client.load_table_from_file(stream, f"_SESSION.{table_name}", job_config=load_job_config)
            load_job.result()

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pandas.DataFrame) -> None:
        if self.is_debug:
            logging.warning(f"BigQuery QT: Registering temp table from pandas: _SESSION.{table_name}")
        client = BigquerySessionManager.get_client()
        load_job_config = BigquerySessionManager.get_load_job_config()
        load_job = client.load_table_from_dataframe(pandas_df, f"_SESSION.{table_name}", job_config=load_job_config)
        load_job.result()

    def register_temp_table_from_data_source(
        self,
        table_name: str,
        ds_node: DataSourceScanNode,
        secret_resolver: Optional[SecretResolver] = None,
        monitor: Optional[ComputeMonitor] = None,
    ) -> None:
        ds_spec = ds_node.ds.batch_source
        assert isinstance(ds_spec, BigquerySourceSpec), "BigQuery compute supports only BigQuery data sources"

        query_str = ds_node.with_dialect(Dialect.BIGQUERY).to_sql()

        if monitor:
            monitor.set_query(query_str)

        # TODO: for cases where ds compute != pipeline compute, it maybe better to register duckdb table
        # this avoids the need for bq create perms if customer just wants to limit tecton to read bq tables
        run_sql = f"CREATE TEMP TABLE {table_name} AS ({query_str})"
        client = BigquerySessionManager.get_client(ds_spec, secret_resolver)
        query_job_config = BigquerySessionManager.get_query_job_config()
        client.query(run_sql, job_config=query_job_config).result()

    def load_table(self, table_name: str, expected_output_schema: Optional[Schema] = None) -> pyarrow.RecordBatchReader:
        return self.run_sql(
            CompatFunctions.for_dialect(Dialect.BIGQUERY).query().from_(table_name).select("*").get_sql(),
            return_dataframe=True,
            expected_output_schema=expected_output_schema,
        )

    def cleanup_temp_tables(self):
        if self.is_debug:
            logging.warning("Cleaning up BigQuery session")
        BigquerySessionManager.abort_session()

    def run_odfv(
        self, qt_node: NodeRef, input_df: pandas.DataFrame, monitor: Optional[ComputeMonitor] = None
    ) -> pandas.DataFrame:
        raise NotImplementedError


class BigquerySessionManager:
    _session_id = None
    _session_client = None
    _user_agent = f"tecton/sdk/{_gen_version.VERSION}"

    @classmethod
    def _initiate_session(cls):
        if cls._session_id is None:
            job = cls._session_client.query(
                "SELECT 1;",
                job_config=bigquery.QueryJobConfig(create_session=True),
            )
            cls._session_id = job.session_info.session_id
            job.result()

    @classmethod
    def abort_session(cls):
        if cls._session_id:
            job = cls._session_client.query(
                "CALL BQ.ABORT_SESSION();",
                job_config=bigquery.QueryJobConfig(
                    create_session=False,
                    connection_properties=[bigquery.query.ConnectionProperty(key="session_id", value=cls._session_id)],
                ),
            )
            job.result()
            cls._session_id = None
            cls._session_client = None

    @classmethod
    def get_query_job_config(cls) -> "bigquery.QueryJobConfig":
        return bigquery.QueryJobConfig(
            create_session=False,
            connection_properties=[bigquery.query.ConnectionProperty(key="session_id", value=cls._session_id)],
        )

    @classmethod
    def get_load_job_config(cls) -> "bigquery.LoadJobConfig":
        return bigquery.LoadJobConfig(
            create_session=False,
            connection_properties=[bigquery.query.ConnectionProperty(key="session_id", value=cls._session_id)],
        )

    @classmethod
    def _get_credentials(cls, source: BigquerySourceSpec, secret_resolver: Optional[SecretResolver]) -> Optional[str]:
        if source.credentials:
            if secret_resolver is None:
                msg = "Missing a secret resolver."
                raise TectonInternalError(msg)
            return secret_resolver.resolve(source.credentials)

    @classmethod
    def get_client(
        cls,
        source: Optional[BigquerySourceSpec] = None,
        secret_resolver: Optional[SecretResolver] = None,
    ) -> "bigquery.Client":
        user_agent = client_info.ClientInfo(user_agent=cls._user_agent)
        if source:
            credentials = cls._get_credentials(source, secret_resolver) if source.credentials else None
            location = source.location
            if credentials:
                client = bigquery.Client.from_service_account_info(
                    json.loads(credentials), location=location, client_info=user_agent
                )
            else:
                client = bigquery.Client(location=location, client_info=user_agent)
        else:
            if cls._session_client:
                return cls._session_client
            client = bigquery.Client(client_info=user_agent)

        if not cls._session_id:
            cls._session_client = client
            cls._initiate_session()

        return client
