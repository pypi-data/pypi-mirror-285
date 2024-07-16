"""Connection for ClickZetta DB-API."""

import logging
import time
import weakref

import requests
from requests.adapters import HTTPAdapter

from clickzetta.connector.v0 import _dbapi_helpers, cursor
from clickzetta.connector.v0.client import Client

# from clickzetta.bulkload.bulkload_enums import BulkLoadOperation, BulkLoadOptions, BulkLoadCommitOptions
# from clickzetta.bulkload.bulkload_stream import BulkLoadStream

is_token_init = False
https_session = None
https_session_inited = False


@_dbapi_helpers.raise_on_closed("Operating on a closed connection.")
class Connection(object):
    def __init__(self, client=None):
        if client is None:
            logging.error("Connection must has a LogParams to log in.")
            raise AssertionError("Connection must has a LogParams to log in.")
        else:
            self._owns_client = True

        self._client = client
        self._client.refresh_token()

        if not globals()["https_session_inited"]:
            session = requests.Session()
            session.mount(
                self._client.service,
                HTTPAdapter(pool_connections=20, pool_maxsize=100, max_retries=1000),
            )
            globals()["https_session"] = session
            globals()["https_session_inited"] = True

        self._client.session = globals()["https_session"]
        self._closed = False
        self._cursors_created = weakref.WeakSet()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._closed = True

        if self._owns_client:
            self._client.close()

        for cursor_ in self._cursors_created:
            if not cursor_._closed:
                cursor_.close()

    def commit(self):
        """No-op, but for consistency raise an error if connection is closed."""

    def cursor(self):
        """Return a new cursor object."""
        if self._client.username is not None and self._client.password is not None:
            self._client.refresh_token()
        new_cursor = cursor.Cursor(self)
        self._cursors_created.add(new_cursor)
        return new_cursor

    def create_bulkload_stream(self, **kwargs):
        schema = kwargs.get("schema", self._client.schema)
        table = kwargs.get("table")
        if schema is None:
            schema = self._client.schema
        if schema is None:
            raise ValueError(f"No schema specified")
        if table is None:
            raise ValueError(f"No table specified")

        from clickzetta.bulkload.bulkload_enums import (
            BulkLoadCommitOptions,
            BulkLoadOperation,
            BulkLoadOptions,
        )
        from clickzetta.bulkload.bulkload_stream import BulkLoadStream

        operation = kwargs.get("operation", BulkLoadOperation.APPEND)
        workspace = kwargs.get("workspace", self._client.workspace)
        vcluster = kwargs.get("vcluster", self._client.vcluster)
        partition_spec = kwargs.get("partition_spec")
        record_keys = kwargs.get("record_keys")
        prefer_internal_endpoint = kwargs.get("prefer_internal_endpoint", False)

        bulkload_meta_data = self._client.create_bulkload_stream(
            schema,
            table,
            BulkLoadOptions(
                operation, partition_spec, record_keys, prefer_internal_endpoint
            ),
        )
        return BulkLoadStream(
            bulkload_meta_data, self._client, BulkLoadCommitOptions(workspace, vcluster)
        )

    def get_bulkload_stream(
        self, stream_id: str, schema: str = None, table: str = None
    ):
        from clickzetta.bulkload.bulkload_enums import (
            BulkLoadCommitOptions,
            BulkLoadOperation,
            BulkLoadOptions,
        )
        from clickzetta.bulkload.bulkload_stream import BulkLoadStream

        bulkload_meta_data = self._client.get_bulkload_stream(schema, table, stream_id)
        return BulkLoadStream(
            bulkload_meta_data,
            self._client,
            BulkLoadCommitOptions(self._client.workspace, self._client.vcluster),
        )

    def get_job_profile(self, job_id: str):
        return self._client.get_job_profile(job_id)

    def get_job_result(self, job_id: str):
        return self._client.get_job_result(job_id)

    def get_job_progress(self, job_id: str):
        return self._client.get_job_progress(job_id)

    def get_job_summary(self, job_id: str):
        return self._client.get_job_summary(job_id)

    def get_job_plan(self, job_id: str):
        return self._client.get_job_plan(job_id)


def connect(**kwargs) -> Connection:
    client = kwargs.get("client")
    if client is None:
        # setting client or cz_url will ignore following parameters
        client = Client(**kwargs)
    return Connection(client)
