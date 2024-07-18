# pyright: reportUnusedExpression=false
from __future__ import annotations
import os
import re
import json
import time
import textwrap
import ast
import uuid

import snowflake.snowpark
from .. import std
from collections import defaultdict
from railib.api import TransactionAsyncResponse, _parse_metadata_proto
import requests
import snowflake.connector
import pyarrow as pa

from snowflake.snowpark import Session
from . import result_helpers
from .. import debugging
from typing import Any, Dict, Iterable, Tuple, List, cast

from pandas import DataFrame

from ..tools.cli_controls import Spinner
from ..clients.types import AvailableModel, Import, ImportSource, ImportSourceTable
from ..clients.config import Config
from ..clients.client import Client, ExportParams, ResourceProvider
from ..clients.util import escape_for_f_string, escape_for_sproc, poll_with_specified_overhead, scrub_exception
from .. import dsl, rel, metamodel as m
from ..errors import EngineNotFoundException, EnginePending, Errors, RAIException, SnowflakeAppMissingException, SnowflakeChangeTrackingNotEnabledException, SnowflakeImportMissingException, SnowflakeInvalidSource, SnowflakeRaiAppNotStarted
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

#--------------------------------------------------
# Constants
#--------------------------------------------------

VALID_POOL_STATUS = ["ACTIVE", "IDLE", "SUSPENDED"]
# transaction list and get return different fields (duration vs timings)
LIST_TXN_SQL_FIELDS = ["id", "database_name", "engine_name", "state", "abort_reason", "read_only","created_by", "created_on", "finished_at", "duration"]
GET_TXN_SQL_FIELDS = ["id", "database", "engine", "state", "abort_reason", "read_only","created_by", "created_on", "finished_at", "timings"]
IMPORT_STREAM_FIELDS = ["ID", "CREATED_AT", "CREATED_BY", "STATUS", "REFERENCE_NAME", "REFERENCE_ALIAS", "FQ_OBJECT_NAME", "RAI_DATABASE",
                        "RAI_RELATION", "DATA_SYNC_STATUS", "PENDING_BATCHES_COUNT", "NEXT_BATCH_STATUS", "NEXT_BATCH_UNLOADED_TIMESTAMP",
                        "NEXT_BATCH_DETAILS", "LAST_BATCH_DETAILS", "LAST_BATCH_UNLOADED_TIMESTAMP", "CDC_STATUS"]
VALID_ENGINE_STATES = ["READY", "PENDING"]
ENGINE_SIZES = ["HIGHMEM_X64_S", "HIGHMEM_X64_M"]
COMPUTE_POOL_MAP = {
    "HIGHMEM_X64_S": "HIGHMEM_X64_S",
    "HIGHMEM_X64_M": "HIGHMEM_X64_M",
    "HIGHMEM_S": "HIGHMEM_X64_S",
    "HIGHMEM_M": "HIGHMEM_X64_M",
    "HighMem|S": "HIGHMEM_X64_S",
    "HighMem|M": "HIGHMEM_X64_M",
}
FIELD_MAP = {
    "database_name": "database",
    "engine_name": "engine",
}
VALID_IMPORT_STATES = ["PENDING", "PROCESSING", "QUARANTINED", "LOADED"]
RAI_APP_NAME = "RELATIONALAI"

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def process_jinja_template(template: str, indent_spaces = 0, **substitutions) -> str:
    lines = template.split('\n')
    processed_lines = []

    for line in lines:
        processed_line = re.sub(r'{{\s*(\w+)\s*}}', lambda m: str(substitutions[m.group(1)]), line)
        processed_lines.append((indent_spaces * " ") + processed_line)

    return '\n'.join(processed_lines)

def type_to_sql(type) -> str:
    if type is str:
        return "VARCHAR"
    if type is int:
        return "NUMBER"
    if type is float:
        return "FLOAT"
    if type is bool:
        return "BOOLEAN"
    if type is dict:
        return "VARIANT"
    if type is list:
        return "ARRAY"
    if type is bytes:
        return "BINARY"
    if isinstance(type, dsl.Type):
        return "NUMBER"
    raise ValueError(f"Unknown type {type}")

def type_to_snowpark(type) -> str:
    if type is str:
        return "StringType"
    if type is int:
        return "IntegerType"
    if type is float:
        return "FloatType"
    if type is bool:
        return "BooleanType"
    if type is dict:
        return "MapType"
    if type is list:
        return "ArrayType"
    if type is bytes:
        return "BinaryType"
    if isinstance(type, dsl.Type):
        return "IntegerType"
    raise ValueError(f"Unknown type {type}")

#--------------------------------------------------
# Resources
#--------------------------------------------------

APP_NAME = "___RAI_APP___"

class Resources(ResourceProvider):
    def __init__(
        self,
        profile: str | None = None,
        config: Config | None = None,
        connection: Session | None = None,
    ):
        super().__init__(profile, config=config)
        self._session = connection
        self._pending_transactions: list[str] = []
        self._ns_cache = {}

    def _exec(self, code:str, params:List[Any]|None = None, raw=False) -> Any:
        if not self._session:
            connection_parameters = {
                "account": self.config.get('account'),
                "user": self.config.get('user'),
                "password": self.config.get('password'),
                "role": self.config.get('role', ""),
                "warehouse":  self.config.get('warehouse', ""),
            }
            self._session = Session.builder.configs(connection_parameters).create()
        try:
            if params is not None and not isinstance(params, list):
                params = [params]
            sess_results = self._session.sql(
                code.replace(APP_NAME, self.get_app_name()),
                params
            )
            if raw:
                return sess_results
            return sess_results.collect()
        except Exception as e:
            orig_message = str(e).lower()
            rai_app = self.config.get("rai_app_name", "")
            if re.search(f"database '{rai_app}' does not exist or not authorized.".lower(), orig_message):
                print("\n")
                exception = SnowflakeAppMissingException(rai_app)
                raise exception from None
            elif re.search(r"javascript execution error", orig_message):
                match = re.search(r"\"message\":\"(.*)\"", orig_message)
                if match:
                    message = match.group(1)
                    if "engine was deleted" in message or "engine not found" in message:
                        exception = EngineNotFoundException(self.config.get('engine', "Unknown"), message)
                        raise exception from None
                    if "engine is in pending" in message or "engine is provisioning" in message:
                        raise EnginePending(self.config.get('engine', "Unknown"))
                    else:
                        raise RAIException(message) from None

            if re.search(r"the relationalai service has not been started.", orig_message):
                app_name = self.config.get("rai_app_name", "")
                sql = "call app.start_service(compute_pool_name, warehouse_name)"
                raise SnowflakeRaiAppNotStarted(app_name, sql)
            raise  RAIException(str(e))


    def reset(self):
        self._session = None

    #--------------------------------------------------
    # Databases
    #--------------------------------------------------

    def get_database(self, name: str):
        results = self._exec(
            f"SELECT * from {APP_NAME}.api.DATABASES WHERE name like '{name}';"
        )
        if not results:
            return None
        db = results[0]
        if not db:
            return None
        return {
            "id": db["ID"],
            "name": db["NAME"],
            "created_by": db["CREATED_BY"],
            "created_on": db["CREATED_ON"],
            "deleted_by": db["DELETED_BY"],
            "deleted_on": db["DELETED_ON"],
            "state": db["STATE"],
        }

    #--------------------------------------------------
    # Engines
    #--------------------------------------------------
    def get_engine_sizes(self):
        return ENGINE_SIZES

    def list_engines(self, state: str | None = None):
        where_clause = f"WHERE STATUS = '{state.upper()}'" if state else ""
        statement = f"SELECT NAME, ID, SIZE, STATUS, CREATED_BY, CREATED_ON, UPDATED_ON FROM {APP_NAME}.api.engines {where_clause} ORDER BY NAME ASC;"
        results = self._exec(statement)
        if not results:
            return []
        return [
            {
                "name": row["NAME"],
                "id": row["ID"],
                "size": row["SIZE"],
                "state": row["STATUS"], # callers are expecting 'state'
                "created_by": row["CREATED_BY"],
                "created_on": row["CREATED_ON"],
                "updated_on": row["UPDATED_ON"],
            }
            for row in results
        ]

    def get_engine(self, name: str):
        results = self._exec(
            f"SELECT NAME, ID, SIZE, STATUS, CREATED_BY, CREATED_ON, UPDATED_ON FROM {APP_NAME}.api.engines WHERE NAME='{name}';"
        )
        if not results:
            return None
        engine = results[0]
        if not engine:
            return None
        return {
            "name": engine["NAME"],
            "id": engine["ID"],
            "size": engine["SIZE"],
            "state": engine["STATUS"], # callers are expecting 'state'
            "created_by": engine["CREATED_BY"],
            "created_on": engine["CREATED_ON"],
            "updated_on": engine["UPDATED_ON"],
        }

    def is_valid_engine_state(self, state:str):
        return state in VALID_ENGINE_STATES

    def create_engine(self, name:str, size:str, pool:str = ""):
        if not pool:
            raise ValueError("Pool is required")
        try:
            with debugging.span("create_engine", name=name, size=size, pool=pool):
                self._exec(f"call {APP_NAME}.api.create_engine('{name}', '{pool}', '{size}');")
        except Exception as e:
            raise Exception(f"Failed to create engine {name} using pool {pool} and size {size}: {e}") from e

    def delete_engine(self, name:str, force_delete:bool = False):
        self._exec(f"call {APP_NAME}.api.delete_engine('{name}', {force_delete});")

    def suspend_engine(self, name:str):
        raise Exception("Not implemented")

    def resume_engine(self, name:str):
        raise Exception("Not implemented")

    #--------------------------------------------------
    # Graphs
    #--------------------------------------------------

    def list_graphs(self) -> List[AvailableModel]:
        with debugging.span("list_models"):
            query = textwrap.dedent(f"""
                    SELECT NAME, ID, CREATED_BY, CREATED_ON, STATE, DELETED_BY, DELETED_ON
                    FROM {APP_NAME}.api.databases
                    WHERE state <> 'DELETED'
                    ORDER BY NAME ASC;
                    """)
            results = self._exec(query)
            if not results:
                return []
            return [
                {
                    "name": row["NAME"],
                    "id": row["ID"],
                    "created_by": row["CREATED_BY"],
                    "created_on": row["CREATED_ON"],
                    "state": row["STATE"],
                    "deleted_by": row["DELETED_BY"],
                    "deleted_on": row["DELETED_ON"],
                }
                for row in results
            ]

    def get_graph(self, name: str):
        with debugging.span("get_model", name=name):
            results = self._exec(
                textwrap.dedent(f"""
                SELECT ID, NAME, CREATED_BY, CREATED_ON, DELETED_BY, DELETED_ON, STATE
                FROM {APP_NAME}.api.databases
                WHERE NAME='{name}' AND STATE <> 'DELETED'
                """)
            )
            if not results:
                return None
            return results[0]

    def create_graph(self, name: str):
        with debugging.span("create_model", name=name):
            self._exec(f"call {APP_NAME}.api.create_database('{name}');")

    def delete_graph(self, name:str):
        with debugging.span("delete_model", name=name):
            self._exec(f"call {APP_NAME}.api.delete_database('{name}');")

    def clone_graph(self, target_name:str, source_name:str, nowait_durable:bool = True):
        with debugging.span("clone_model", target_name=target_name, source_name=source_name):
            # not a mistake: the clone_database argument order is indeed target then source:
            self._exec(f"call {APP_NAME}.api.clone_database('{target_name}', '{source_name}', {nowait_durable});")

    #--------------------------------------------------
    # Models
    #--------------------------------------------------

    def list_models(self, database: str, engine: str):
        pass

    def create_models(self, database: str, engine: str, models:List[Tuple[str, str]]) -> List[Any]:
        rel_code = self.create_models_code(models)
        self.exec_raw(database, engine, rel_code, readonly=False)
        # TODO: handle SPCS errors once they're figured out
        return []

    def delete_model(self, database:str, engine:str, name:str):
        self.exec_raw(database, engine, f"def delete[:rel, :catalog, :model, \"{name}\"]: rel[:catalog, :model, \"{name}\"]", readonly=False)

    def create_models_code(self, models:List[Tuple[str, str]]) -> str:
        lines = []
        for (name, code) in models:
            name = name.replace("\"", "\\\"")
            assert "\"\"\"\"\"\"\"" not in code, "Code literals must use fewer than 7 quotes."

            lines.append(textwrap.dedent(f"""
            def delete[:rel, :catalog, :model, "{name}"]: rel[:catalog, :model, "{name}"]
            def insert[:rel, :catalog, :model, "{name}"]: raw\"\"\"\"\"\"\"
            """) + code + "\n\"\"\"\"\"\"\"")
        rel_code = "\n\n".join(lines)
        return rel_code

    #--------------------------------------------------
    # Exports
    #--------------------------------------------------

    def list_exports(self, database: str, engine: str):
        return []

    def get_export_code(self, params: ExportParams):
        sql_inputs = ", ".join([f"{name} {type_to_sql(type)}" for (name, _, type) in params.inputs])
        input_names = [name for (name, *_) in params.inputs]
        sql_out = ", ".join([f"{name} {type_to_sql(type)}" for (name, type) in params.out_fields])
        py_outs = ", ".join([f"StructField(\"{name}\", {type_to_snowpark(type)}())" for (name, type) in params.out_fields])
        py_inputs = ", ".join([name for (name, *_) in params.inputs])
        safe_rel = escape_for_f_string(params.code).strip()
        clean_inputs = []
        for (name, var, type) in params.inputs:
            if type is str:
                clean_inputs.append(f"{name} = '\"' + escape({name}) + '\"'")
            # Replace `var` with `name` and keep the following non-word character unchanged
            pattern = re.compile(re.escape(var) + r'(\W)')
            safe_rel = re.sub(pattern, rf"{{{name}}}\1", safe_rel)
        if py_inputs:
            py_inputs = f", {py_inputs}"
        clean_inputs = ("\n" + " "*20).join(clean_inputs)
        template_path = os.path.join(os.path.dirname(__file__), "export_procedure.py.jinja")
        with open(template_path) as f:
            template = f.read()
        def quote(s: str, f = False) -> str:
            return '"' + s + '"' if not f else 'f"' + s + '"'
        python_code = process_jinja_template(
            template,
            indent_spaces=12,
            func_name=quote(params.func_name),
            database=quote(params.source_database),
            persistent_database=quote(params.database),
            engine=quote(params.engine),
            rel_code=quote(safe_rel, f=True),
            APP_NAME=quote(APP_NAME),
            input_names=input_names,
            outputs=sql_out,
            clean_inputs=clean_inputs,
            py_inputs=py_inputs,
            py_outs=py_outs,
        ).strip()
        sql_code = textwrap.dedent(f"""
            CREATE OR REPLACE PROCEDURE {params.func_name}({sql_inputs}{sql_inputs and ',' or ''} engine STRING DEFAULT NULL)
            RETURNS TABLE({sql_out})
            LANGUAGE PYTHON
            RUNTIME_VERSION = '3.8'
            PACKAGES = ('snowflake-snowpark-python')
            HANDLER = 'handle'
            EXECUTE AS CALLER
            AS
            $$
            {escape_for_sproc(python_code)}
            $$;
        """)
        python_code = textwrap.dedent(" " * 12 + python_code)
        # This check helps catch invalid code early and for dry runs:
        try:
            ast.parse(python_code)
        except SyntaxError:
            raise ValueError(f"Internal error: invalid Python code generated:\n{python_code}")
        return sql_code


    def create_export(self, params: ExportParams):
        self.delete_on_exit = False
        sql_code = self.get_export_code(params)
        if not params.dry_run:
            start = time.perf_counter()
            self._exec(sql_code)
            debugging.time("export", time.perf_counter() - start, DataFrame(), code=sql_code.replace(APP_NAME, self.get_app_name()))


    def create_export_table(self, database: str, engine: str, table: str, relation: str, columns: Dict[str, str], code: str, refresh: str|None=None):
        print("Snowflake doesn't support creating export tables yet. Try creating the table manually first.")
        pass

    def delete_export(self, model: str, engine: str, export: str):
        pass

    #--------------------------------------------------
    # Imports
    #--------------------------------------------------

    def is_valid_import_state(self, state:str):
        return state in VALID_IMPORT_STATES

    def imports_to_dicts(self, results):
        parsed_results = [
            {field.lower(): row[field] for field in IMPORT_STREAM_FIELDS}
            for row in results
        ]
        return parsed_results

    def change_stream_status(self, stream_id: str, model:str, suspend: bool):
        if stream_id and model:
            if suspend:
                self._exec(f"CALL {APP_NAME}.api.suspend_data_stream('{stream_id}', '{model}');")
            else:
                self._exec(f"CALL {APP_NAME}.api.resume_data_stream('{stream_id}', '{model}');")

    def change_imports_status(self, suspend: bool):
        if suspend:
            self._exec(f"CALL {APP_NAME}.app.suspend_cdc();")
        else:
            self._exec(f"CALL {APP_NAME}.app.resume_cdc();")

    def get_imports_status(self):
        results = self._exec(f"CALL {APP_NAME}.app.cdc_status();")
        if results:
            for result in results:
                engine = result['CDC_ENGINE_NAME']
                status = result['CDC_TASK_STATUS']
                info = result['CDC_TASK_INFO']
                return {"engine": engine, "status": status, "info": info}
        return {}

    def set_imports_engine(self, engine:str):
        try:
            self._exec(f"CALL {APP_NAME}.app.setup_cdc('{engine}');")
        except Exception as e:
            if "engine not found" in str(e):
                raise ValueError(f"Engine {engine} not found. Please create the engine first.") from e

    def list_imports(
        self,
        id:str|None = None,
        name:str|None = None,
        model:str|None = None,
        status:str|None = None,
        creator:str|None = None,
    ) -> list[Import]:
        where = []
        if id and isinstance(id, str):
            where.append(f"LOWER(ID) = '{id.lower()}'")
        if name and isinstance(name, str):
            where.append(f"LOWER(FQ_OBJECT_NAME) = '{name.lower()}'")
        if model and isinstance(model, str):
            where.append(f"LOWER(RAI_DATABASE) = '{model.lower()}'")
        if creator and isinstance(creator, str):
            where.append(f"LOWER(CREATED_BY) = '{creator.lower()}'")
        if status and isinstance(status, str):
            where.append(f"LOWER(batch_status) = '{status.lower()}'")
        where_clause = " AND ".join(where)

        # this is roughly copied from the native app code because we don't have a way to
        # get the status of multiple streams at once and doing them individually is way
        # too slow
        statement = f"""
        select ID, RAI_DATABASE, FQ_OBJECT_NAME, CREATED_AT, CREATED_BY, nextBatch.status as batch_status, processing_errors, nextBatch.batches,
            from {APP_NAME}.api.data_streams as ds
            left JOIN (
            select
                data_stream_id,
                min_by(status, unloaded) as status,
                min_by(batch_details, unloaded) as batch_details,
                min(processing_details:processingErrors) as processing_errors,
                min(unloaded) as unloaded,
                count(*) as batches
            from {APP_NAME}.api.data_stream_batches
            group by data_stream_id
            ) nextBatch
            ON ds.id = nextBatch.data_stream_id
            {f"where {where_clause}" if where_clause else ""}
            ORDER BY FQ_OBJECT_NAME ASC;
        """

        results = self._exec(statement)
        items = []
        if results:
            for stream in results:
                (id, db, name, created_at, created_by, status, processing_errors, batches) = stream
                if status and isinstance(status, str):
                    status = status.upper()
                if processing_errors:
                    if status in ["QUARANTINED", "PENDING"]:
                        start = processing_errors.rfind("Error")
                        if start != -1:
                            processing_errors = processing_errors[start:-1]
                    else:
                        processing_errors = None
                items.append(cast(Import, {
                    "id": id,
                    "model": db,
                    "name": name,
                    "created": created_at,
                    "creator": created_by,
                    "status": status.upper() if status else None,
                    "errors": processing_errors if processing_errors != "[]" else None,
                    "batches": f"{batches}" if batches else "",
                }))
        return items

    def poll_imports(self, sources:List[str], model:str):
        def check_imports():
            imports = [import_ for import_ in self.list_imports(model=model) if import_["name"] in sources]
            all_completed = all(import_["status"] == "LOADED" for import_ in imports)
            failed_imports = [import_["name"] for import_ in imports if import_["status"] == "QUARANTINED"]
            if all_completed:
                return True
            if failed_imports:
                raise RAIException("Imports failed:" + ", ".join(failed_imports)) from None
        poll_with_specified_overhead(check_imports, overhead_rate=0.2, max_delay=10)

    def get_import_stream(self, stream_id:str, model:str):
        results = self._exec(f"CALL {APP_NAME}.api.get_data_stream('{stream_id}', '{model}');")
        if not results:
            return None
        return self.imports_to_dicts(results)

    def create_import_stream(self, source:ImportSource, model:str, rate = 1, options: dict|None = None):
        assert isinstance(source, ImportSourceTable), "Snowflake integration only supports loading from SF Tables. Try loading your data as a table via the Snowflake interface first."
        object = source.fqn

        if object.lower() in [x["name"].lower() for x in self.list_imports(model=model)]:
            return

        query = f"SHOW OBJECTS LIKE '{source.table}' IN {source.database}.{source.schema}"
        info = self._exec(query)
        if not info:
            raise ValueError(f"Object {source.table} not found in {source.database}.{source.schema}")
        else:
            data = info[0]
            if not data:
                raise ValueError(f"Object {source.table} not found in {source.database}.{source.schema}")
            # (time, name, db_name, schema_name, kind, *rest)
            kind = data["kind"]

        try:
            self._exec(f"ALTER {kind} {object} SET CHANGE_TRACKING = TRUE;")
        except Exception:
            pass

        command = f"""call {APP_NAME}.api.create_data_stream(
            {APP_NAME}.api.object_reference('{kind}', '{object}'),
            '{model}',
            '{object.replace('.', '_').lower()}');"""
        try:
            self._exec(command)
        except Exception as e:
            if "ensure that CHANGE_TRACKING is enabled on the source object" in str(e):
                print("\n")
                exception = SnowflakeChangeTrackingNotEnabledException(object, f"ALTER TABLE {object} SET CHANGE_TRACKING = TRUE;")
                raise exception from None
            raise e

        return

    def create_import_snapshot(self, source:ImportSource, model:str, _: dict|None = None):
        raise Exception("Snowflake integration doesn't support snapshot imports yet")

    def delete_import(self, import_name:str, model:str):
        self._exec(f"""call {APP_NAME}.api.delete_data_stream(
            '{import_name}',
            '{model}'
        );""")
        return

    #--------------------------------------------------
    # Exec Async
    #--------------------------------------------------

    def _check_exec_async_status(self, txn_id: str):
        """Check whether the given transaction has completed."""

        with debugging.span("check_status"):
            response = self._exec(f"CALL {APP_NAME}.api.get_transaction('{txn_id}');")
            assert response, f"No results from get_transaction('{txn_id}')"

        response_row = next(iter(response))
        status: str = response_row['STATE']

        # remove the transaction from the pending list if it's completed or aborted
        if status in ["COMPLETED", "ABORTED"]:
            if txn_id in self._pending_transactions:
                self._pending_transactions.remove(txn_id)

        # @TODO: Find some way to tunnel the ABORT_REASON out. Azure doesn't have this, but it's handy
        return status == "COMPLETED" or status == "ABORTED"

    def _list_exec_async_artifacts(self, txn_id: str) -> Dict[str, str]:
        """Grab the list of artifacts produced in the transaction and the URLs to retrieve their contents."""
        with debugging.span("list_results"):
            response = self._exec(
                f"CALL {APP_NAME}.api.list_transaction_outputs('{txn_id}');"
            )
            assert response, f"No results from list_transaction_outputs('{txn_id}')"
            return {row["FILE_NAME"]: row["PRESIGNED_URL"] for row in response}

    def _fetch_exec_async_artifacts(
        self, artifact_urls: Dict[str, str]
    ) -> Dict[str, Any]:
        """Grab the contents of the given artifacts from SF in parallel using threads."""
        contents = {}

        with requests.Session() as session:
            # Define _fetch_data inside the session context to close over 'session'
            def _fetch_data(name_url):
                name, url = name_url
                try:
                    response = session.get(url)
                    response.raise_for_status()  # Throw if something goes wrong
                    if name.endswith(".json"):
                        return name, response.json()
                    else:
                        return name, response.content
                except requests.RequestException as e:
                    raise scrub_exception(e)

            # Create a list of tuples for the map function
            name_url_pairs = list(artifact_urls.items())

            # Create ThreadPoolExecutor to handle requests in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Map fetch across all URLs using the executor
                results = executor.map(_fetch_data, name_url_pairs)

                # Populate contents dictionary
                for name, data in results:
                    contents[name] = data

        return contents

    def _parse_exec_async_results(self, arrow_files: List[Tuple[str, bytes]]):
        """Mimics the logic in _parse_arrow_results of railib/api.py#L303 without requiring a wrapping multipart form."""
        results = []

        for file_name, file_content in arrow_files:
            with pa.ipc.open_stream(file_content) as reader:
                schema = reader.schema
                batches = [batch for batch in reader]
                table = pa.Table.from_batches(batches=batches, schema=schema)
                results.append({"relationId": file_name, "table": table})

        return results

    def _download_results(self, artifact_urls, txn_id, state: str) -> TransactionAsyncResponse:
        with debugging.span("download_results"):
            # Fetch artifacts
            artifacts = self._fetch_exec_async_artifacts(artifact_urls)

            # Parse metadata from the artifacts
            meta = _parse_metadata_proto(artifacts["metadata.proto"])
            meta_json = artifacts["metadata.json"]

            # Use the metadata to map arrow files to the relations they contain
            arrow_files_to_relations = {}
            for ix, relation in enumerate(meta.relations):
                arrow_file = relation.file_name
                relation_id = meta_json[ix]["relationId"]
                arrow_files_to_relations[arrow_file] = relation_id

            # Hydrate the arrow files into tables
            results = self._parse_exec_async_results([
                (arrow_files_to_relations[name], content) for name, content in artifacts.items() if name.endswith(".arrow")
            ])

            # Create and return the response
            rsp = TransactionAsyncResponse()
            rsp.transaction = {"id": txn_id, "state": state, "response_format_version": None}
            rsp.metadata = meta
            rsp.problems = artifacts.get("problems.json")  # Safely access possible missing keys
            rsp.results = results
            return rsp

    # TODO get rid of this once we completely switch to exec_async_v2
    def _exec_async_v1(
        self,
        database: str,
        engine: str,
        raw_code: str,
        inputs={},
        readonly=True,
    ):
        with debugging.span("transaction") as txn_span:
            if inputs:
                raise Exception(
                    "Inputs aren't currently supported using exec_async_v1 in SPCS."
                )

            with debugging.span("create_v1"):
                response = self._exec(
                    f"CALL {APP_NAME}.api.exec_async('{database}', '{engine}', ?, {readonly});",
                    raw_code,
                )
                if not response:
                    raise Exception("No results from exec_async")

            # grab the txn_id and state from the response
            first_row = next(iter(response))
            txn_id = first_row["ID"]
            state = first_row["STATE"]

            txn_span["txn_id"] = txn_id
            debugging.event("transaction_created", txn_span, txn_id=txn_id)
            # Wait for completion or failure
            if state != "COMPLETED":
                self._pending_transactions.append(txn_id)
                with debugging.span("wait", txn_id=txn_id):
                    poll_with_specified_overhead(
                        lambda: self._check_exec_async_status(txn_id), 0.2
                    )

            with debugging.span("fetch"):
                # List the result artifacts (and the URLs to retrieve them)
                artifact_urls = self._list_exec_async_artifacts(txn_id)

                return self._download_results(artifact_urls, txn_id, state)

    def _exec_async_v2(
        self,
        database: str,
        engine: str,
        raw_code: str,
        inputs={},
        readonly=True,
        nowait_durable=False,
        headers={},
    ):
        from .. import __version__ # avoid circular import by importing here

        with debugging.span("transaction") as txn_span:
            with debugging.span("create_v2"):
                headers['user-agent'] = f"pyrel/{__version__}"

                response = self._exec(
                    f"CALL {APP_NAME}.api.exec_async_v2('{database}','{engine}', ?, {inputs}, {readonly}, {nowait_durable}, {headers});",
                    raw_code,
                )

            if not response:
                raise Exception("Failed to create transaction")

            artifact_urls = {}
            rows = list(iter(response))

            # process the first row since txn_id and state are the same for all rows
            first_row = rows[0]
            txn_id = first_row['ID']
            state = first_row['STATE']
            filename = first_row['FILENAME']
            url = first_row['PRESIGNED_URL']

            txn_span["txn_id"] = txn_id
            debugging.event("transaction_created", txn_span, txn_id=txn_id)

            # fast path: transaction already finished
            if state in ["COMPLETED", "ABORTED"]:
                if txn_id in self._pending_transactions:
                    self._pending_transactions.remove(txn_id)
                artifact_urls[filename] = url

                # Process rows to get the rest of the artifacts
                for row in rows:
                    filename = row['FILENAME']
                    url = row['PRESIGNED_URL']
                    artifact_urls[filename] = url

            # Slow path: transaction not done yet; start polling
            else:
                self._pending_transactions.append(txn_id)
                with debugging.span("wait", txn_id=txn_id):
                    poll_with_specified_overhead(
                        lambda: self._check_exec_async_status(txn_id), 1.0
                    )
                artifact_urls = self._list_exec_async_artifacts(txn_id)

            with debugging.span("fetch"):
                return self._download_results(artifact_urls, txn_id, state)


    #--------------------------------------------------
    # Exec
    #--------------------------------------------------

    def exec_raw(
        self,
        database: str,
        engine: str,
        raw_code: str,
        inputs: dict = {},
        readonly=True,
        nowait_durable=False,
        headers={},
    ):
        raw_code = raw_code.replace("'", "\\'")
        use_exec_async_v2 = self.config.get("sf_use_exec_async_v2", True)

        if use_exec_async_v2:
            return self._exec_async_v2(
                database, engine, raw_code, inputs, readonly, nowait_durable, headers
            )
        else:
            return self._exec_async_v1(database, engine, raw_code, inputs, readonly)


    def format_results(self, results, task:m.Task|None=None) -> Tuple[DataFrame, List[Any]]:
        return result_helpers.format_results(results, task)

    #--------------------------------------------------
    # Exec format
    #--------------------------------------------------

    def exec_format(
        self,
        database: str,
        engine: str,
        raw_code: str,
        task: m.Task,
        format: str,
        inputs: dict = {},
        readonly=True,
        nowait_durable=False,
        headers={},
    ):
        # TODO: add headers and nowait_durable
        start = time.perf_counter()
        output_table = "out"+str(uuid.uuid4()).replace("-", "_")
        temp_table = f"temp_{output_table}"
        self._exec(f"call {APP_NAME}.api.exec_into(?, ?, ?, ?, ?);", [database, engine, raw_code, output_table, readonly])
        debugging.time("exec_format", time.perf_counter() - start, DataFrame())

        names = ", ".join([f"col{ix:03} as {name}" for (ix, name) in enumerate(task.return_cols())])
        self._exec(f"CREATE TEMPORARY TABLE {APP_NAME}.results.{temp_table} AS SELECT {names} FROM {APP_NAME}.results.{output_table};")
        self._exec(f"call {APP_NAME}.api.drop_result_table(?)", [output_table])

        temp = cast(snowflake.snowpark.DataFrame, self._exec(f"select * from {APP_NAME}.results.{temp_table}", raw=True))
        return (temp, [])

    #--------------------------------------------------
    # Custom model types
    #--------------------------------------------------

    def _get_ns(self, model:dsl.Graph):
        if model not in self._ns_cache:
            self._ns_cache[model] = Snowflake(model)
        return self._ns_cache[model]

    def to_model_type(self, model:dsl.Graph, name: str, source:str):
        parts = source.split(".")
        if len(parts) < 3:
            raise SnowflakeInvalidSource(Errors.call_source(), source)
        ns = self._get_ns(model)
        for part in parts:
            ns = getattr(ns, part)
        return ns

    #--------------------------------------------------
    # Transactions
    #--------------------------------------------------
    def txn_list_to_dicts(self, transactions):
        dicts = []
        for txn in transactions:
            dict = {}
            txn_dict = txn.asDict()
            for key in txn_dict:
                mapValue = FIELD_MAP.get(key.lower())
                if mapValue:
                    dict[mapValue] = txn_dict[key]
                else:
                    dict[key.lower()] = txn_dict[key]
            dicts.append(dict)
        return dicts

    def get_transaction(self, transaction_id):
        results = self._exec(
            f"CALL {APP_NAME}.api.get_transaction(?);", [transaction_id])
        if not results:
            return None

        results = self.txn_list_to_dicts(results)

        txn = {field: results[0][field] for field in GET_TXN_SQL_FIELDS}

        created_on = txn.get("created_on")
        finished_at = txn.get("finished_at")
        if created_on:
            if finished_at:
                txn['duration'] = finished_at - created_on
            else:
                tz_info = created_on.tzinfo
                txn['duration'] = datetime.now(tz_info) - created_on
        return txn

    def list_transactions(self, **kwargs):
        id = kwargs.get("id", None)
        state = kwargs.get("state", None)
        engine = kwargs.get("engine", None)
        limit = kwargs.get("limit", 100)
        all_users = kwargs.get("all_users", False)
        created_by = kwargs.get("created_by", None)
        only_active = kwargs.get("only_active", False)
        where_clause_arr = []

        if id:
            where_clause_arr.append(f"id = '{id}'")
        if state:
            where_clause_arr.append(f"state = '{state.upper()}'")
        if engine:
            where_clause_arr.append(f"LOWER(engine_name) = '{engine.lower()}'")
        else:
            if only_active:
                where_clause_arr.append("state in ('CREATED', 'RUNNING', 'PENDING')")
        if not all_users and created_by is not None:
            where_clause_arr.append(f"LOWER(created_by) = '{created_by.lower()}'")

        if len(where_clause_arr):
            where_clause = f'WHERE {" AND ".join(where_clause_arr)}'
        else:
            where_clause = ""

        sql_fields = ", ".join(LIST_TXN_SQL_FIELDS)
        query = f"SELECT {sql_fields} from {APP_NAME}.api.transactions {where_clause} ORDER BY created_on DESC LIMIT ?"
        results = self._exec(query, [limit])
        if not results:
            return []
        return self.txn_list_to_dicts(results)

    def cancel_transaction(self, transaction_id):
        self._exec(f"CALL {APP_NAME}.api.CANCEL_TRANSACTION(?);", [transaction_id])
        if transaction_id in self._pending_transactions:
            self._pending_transactions.remove(transaction_id)

    def cancel_pending_transactions(self):
        for txn_id in self._pending_transactions:
            self.cancel_transaction(txn_id)

    def get_transaction_events(self, txn_id: str, continuation_token:str=''):
        results = self._exec(
            f"SELECT {APP_NAME}.api.get_transaction_events(?, ?);",
            [txn_id, continuation_token],
        )
        if not results:
            return {
                "events": [],
                "continuation_token": None
            }
        row = results[0][0]
        return json.loads(row)

    #--------------------------------------------------
    # Snowflake specific
    #--------------------------------------------------

    def get_version(self):
        results = self._exec(f"SELECT {APP_NAME}.app.get_release()")
        if not results:
            return None
        return results[0][0]

    def list_warehouses(self):
        results = self._exec("SHOW WAREHOUSES")
        if not results:
            return []
        return [{"name":name}
                for (name, *rest) in results]

    def list_compute_pools(self):
        results = self._exec("SHOW COMPUTE POOLS")
        if not results:
            return []
        return [{"name":name, "status":status, "min_nodes":min_nodes, "max_nodes":max_nodes, "instance_family":instance_family}
                for (name, status, min_nodes, max_nodes, instance_family, *rest) in results]

    def list_valid_compute_pools_by_engine_size(self, engine_size:str):
        valid_pools = self.list_compute_pools()
        if not valid_pools:
            return []
        engine_pools = [item['name'] for item in valid_pools if item['status'] in VALID_POOL_STATUS and COMPUTE_POOL_MAP.get(item['instance_family']) == engine_size]
        if not engine_pools:
            return []
        return engine_pools

    def list_roles(self):
        results = self._exec("SELECT CURRENT_AVAILABLE_ROLES()")
        if not results:
            return []
        # the response is a single row with a single column containing
        # a stringified JSON array of role names:
        row = results[0]
        if not row:
            return []
        return [{"name": name} for name in json.loads(row[0])]

    def list_apps(self):
        all_apps = self._exec(f"SHOW APPLICATIONS LIKE '{RAI_APP_NAME}'")
        if not all_apps:
            all_apps = self._exec("SHOW APPLICATIONS")
            if not all_apps:
                return []
        return [{"name":name}
                for (time, name, *rest) in all_apps]

    def list_databases(self):
        results = self._exec("SHOW DATABASES")
        if not results:
            return []
        return [{"name":name}
                for (time, name, *rest) in results]

    def list_sf_schemas(self, database:str):
        results = self._exec(f"SHOW SCHEMAS IN {database}")
        if not results:
            return []
        return [{"name":name}
                for (time, name, *rest) in results]

    def list_tables(self, database:str, schema:str):
        results = self._exec(f"SHOW OBJECTS IN {database}.{schema}")
        items = []
        if results:
            for (time, name, db_name, schema_name, kind, *rest) in results:
                items.append({"name":name, "kind":kind.lower()})
        return items

    def schema_info(self, database:str, schema:str, tables:Iterable[str]):
        pks = self._exec(f"SHOW PRIMARY KEYS IN SCHEMA {database}.{schema};")
        fks = self._exec(f"SHOW IMPORTED KEYS IN SCHEMA {database}.{schema};")
        tables = ", ".join([f"'{x.upper()}'" for x in tables])
        columns = self._exec(textwrap.dedent(f"""
            select TABLE_NAME, COLUMN_NAME, DATA_TYPE
            from {database.upper()}.INFORMATION_SCHEMA.COLUMNS
            where TABLE_SCHEMA ILIKE '{schema.upper()}'
            and TABLE_NAME in ({tables})
            and TABLE_CATALOG ILIKE '{database.upper()}';
        """))
        results = defaultdict(lambda: {"pks": [], "fks": {}, "columns": {}})
        if pks:
            for row in pks:
                results[row[3].lower()]["pks"].append(row[4]) # type: ignore
        if fks:
            for row in fks:
                results[row[7].lower()]["fks"][row[8]] = row[3]
        if columns:
            for row in columns:
                results[row[0].lower()]["columns"][row[1]] = row[2]
        return results

#--------------------------------------------------
# Snowflake Wrapper
#--------------------------------------------------

class PrimaryKey:
    pass

class Snowflake:
    def __init__(self, model, auto_import=False):
        self._model = model
        self._auto_import = auto_import
        if not isinstance(model._client.resources, Resources):
            raise ValueError("Snowflake model must be used with a snowflake config")
        self._dbs = {}
        imports = model._client.resources.list_imports(model=model.name)
        self._import_structure(imports)

    def _import_structure(self, imports: list[Import]):
        tree = self._dbs
        # pre-create existing imports
        schemas = set()
        for item in imports:
            database_name, schema_name, table_name = item["name"].lower().split('.')
            database = getattr(self, database_name)
            schema = getattr(database, schema_name)
            schemas.add(schema)
            schema._add(table_name, is_imported=True)
        for schema in schemas:
            schema._fetch_info()
        return tree

    def __getattribute__(self, __name: str) -> 'SnowflakeDB':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        __name = __name.lower()
        if __name in self._dbs:
            return self._dbs[__name]
        self._dbs[__name] = SnowflakeDB(self, __name)
        return self._dbs[__name]

class SnowflakeDB:
    def __init__(self, parent, name):
        self._name = name
        self._parent = parent
        self._model = parent._model
        self._schemas = {}

    def __getattribute__(self, __name: str) -> 'SnowflakeSchema':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        __name = __name.lower()
        if __name in self._schemas:
            return self._schemas[__name]
        self._schemas[__name] = SnowflakeSchema(self, __name)
        return self._schemas[__name]

class SnowflakeSchema:
    def __init__(self, parent, name):
        self._name = name
        self._parent = parent
        self._model = parent._model
        self._tables = {}
        self._imported = set()
        self._table_info = defaultdict(lambda: {"pks": [], "fks": {}, "columns": {}})

    def _fetch_info(self):
        self._table_info = self._model._client.resources.schema_info(self._parent._name, self._name, self._imported)

    def _add(self, name, is_imported=False):
        name = name.lower()
        if name in self._tables:
            return self._tables[name]
        if is_imported:
            self._imported.add(name)
        else:
            self._tables[name] = SnowflakeTable(self, name)
        return self._tables.get(name)

    def __getattribute__(self, __name: str) -> 'SnowflakeTable':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        table = self._add(__name)
        table._lazy_init()
        return table

class SnowflakeTable(dsl.Type):
    def __init__(self, parent, name):
        super().__init__(parent._model, f"sf_{name}")
        self._name = name
        self._model = parent._model
        self._parent = parent
        self._aliases = {}
        self._finalzed = False

    def _lazy_init(self):
        parent = self._parent
        name = self._name
        if name not in parent._imported:
            if self._parent._parent._parent._auto_import:
                with Spinner(f"Creating stream for {self.fqname()}", f"Stream created for {self.fqname()}"):
                    db_name = parent._parent._name
                    schema_name = parent._name
                    self._model._client.resources.create_import_stream(ImportSourceTable(db_name, schema_name, name), self._model.name)
                print("")
                parent._imported.add(name)
            else:
                imports = self._model._client.resources.list_imports(model=self._model.name)
                for item in imports:
                    cur_name = item["name"].lower().split(".")[-1]
                    parent._imported.add(cur_name)
            if name not in parent._imported:
                exception = SnowflakeImportMissingException(debugging.capture_code_info(), self.fqname(), self._model.name)
                raise exception from None

        if name not in parent._table_info:
            parent._fetch_info()

        self._finalize()

    def _finalize(self):
        if self._finalzed:
            return

        self._finalzed = True
        self._schema = self._parent._table_info[self._name]
        relation_name = self.fqname().replace(".", "_").lower()
        model:dsl.Graph = self._model
        model.install_raw(f"declare {relation_name}")
        edb = getattr(std.rel, relation_name)
        id_rel = getattr(std.rel, f"{relation_name}_pyrel_id")

        with model.rule():
            id, val = std.Vars(2)
            edb(dsl.Symbol("METADATA$ROW_ID"), id, val)
            id_rel.add(id)

        with model.rule():
            prop, id, val = std.Vars(3)
            with model.not_found():
                edb(dsl.Symbol("METADATA$ROW_ID"), id, val)
            edb(prop, id, val)
            id_rel.add(id)

        with model.rule(dynamic=True):
            prop, id, val = std.Vars(3)
            if self._schema["pks"]:
                getattr(edb, self._schema["pks"][0])(id, val)
            else:
                id_rel(id)
            self.add(snowflake_id=id)

        for prop, prop_type in self._schema["columns"].items():
            with model.rule(dynamic=True):
                id, val = std.Vars(2)
                getattr(edb, prop)(id, val)
                if getattr(self, prop.lower()).is_multi_valued:
                    inst = self(snowflake_id=id)
                    getattr(inst, prop.lower()).add(val)
                else:
                    self(snowflake_id=id).set(**{prop.lower(): val})

    def namespace(self):
        return f"{self._parent._parent._name}.{self._parent._name}"

    def fqname(self):
        return f"{self.namespace()}.{self._name}"

    def describe(self, **kwargs):
        model = self._model
        for k, v in kwargs.items():
            if v is PrimaryKey:
                self._schema["pks"] = [k]
            elif isinstance(v, tuple):
                (table, name) = v
                if isinstance(table, SnowflakeTable):
                    fk_table = table
                    pk = fk_table._schema["pks"]
                    with model.rule():
                        inst = fk_table()
                        me = self()
                        getattr(inst, pk[0]) == getattr(me, k)
                        if getattr(self, name).is_multi_valued:
                            getattr(me, name).add(inst)
                        else:
                            me.set(**{name: inst})
                else:
                    raise ValueError(f"Invalid foreign key {v}")
            else:
                raise ValueError(f"Invalid column {k}={v}")
        return self

#--------------------------------------------------
# Graph
#--------------------------------------------------

def Graph(
    name,
    *,
    profile: str | None = None,
    config: Config,
    dry_run: bool = False,
    isolated: bool = True,
    connection: Session | None = None,
    keep_model: bool = False,
    nowait_durable: bool = True,
    format: str = "default",
):
    client = Client(
        Resources(profile, config, connection),
        rel.Compiler(config),
        name,
        config,
        dry_run=dry_run,
        isolated=isolated,
        keep_model=keep_model,
        nowait_durable=nowait_durable
    )
    client.install("pyrel_base", dsl.build.raw_task("""
        @inline
        def make_identity(x..., z):
            exists((u) | hash128({x...}, x..., u) and
            hash_value_uint128_convert(u, z))

        @inline
        def pyrel_default({F}, c, k..., v):
            F(k..., v) or (not F(k..., _) and v = c)

        @inline
        def pyrel_unwrap(x in UInt128, y): y = x

        @inline
        def pyrel_dates_period_days(x in Date, y in Date, z):
            exists((u) | dates_period_days(x, y , u) and u = ::std::common::^Day[z])

        @inline
        def pyrel_datetimes_period_milliseconds(x in DateTime, y in DateTime, z in Int):
            exists((u) | datetimes_period_milliseconds(x, y , u) and u = ^Millisecond[z])

        @inline
        def pyrel_bool_filter(a, b, z, {F}): { z = if_then_else[F(a, b), boolean_true, boolean_false] }
    """))
    return dsl.Graph(client, name, format=format)
