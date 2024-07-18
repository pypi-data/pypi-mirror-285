from __future__ import annotations
import atexit
import re
from collections import defaultdict
from typing import Dict, List, Any, Tuple, cast, Callable

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pandas import DataFrame
import time

from .types import AvailableModel, Import, ImportSource
from ..clients.config import Config
from ..compiler import Compiler
from .. import dsl, debugging, metamodel as m

#--------------------------------------------------
# InstallBatch
#--------------------------------------------------

class InstallBatch:
    def __init__(self):
        self.dirty = set()
        self.content:Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.control_items:List[Tuple[str, Callable|None]] = []
        self.task_map = defaultdict(dict)

    def _cell(self):
        return debugging.jupyter.cell() or ""

    def _check_dirty_cells(self, name:str):
        for cell in debugging.jupyter.dirty_cells:
            self.content[name][cell].clear()
        debugging.jupyter.dirty_cells.clear()

    def append(self, name:str, code:str, task:m.Task|None=None):
        self._check_dirty_cells(name)
        self.dirty.add(name)
        self.content[name][self._cell()].append((code, task))

    def set(self, name:str, code:str, task:m.Task|None=None):
        self.dirty.add(name)
        self.content[name][self._cell()] = [(code, task)]

    def flush(self):
        items = []
        for name in self.dirty:
            all_cells = []
            cur_line = 0
            task_map = self.task_map[name]
            for _, content in self.content[name].items():
                for (code, task) in content:
                    all_cells.append(code)
                    end = code.count("\n") + cur_line + 2
                    task_map[task] = (cur_line, end)
                    cur_line = end
            items.append((name, "\n\n".join(all_cells)))
        self.dirty.clear()
        return items

    def get_all_models(self):
        items = []
        for name in self.content:
            all_cells = []
            for _, content in self.content[name].items():
                for code, _ in content:
                    all_cells.append(code)
            items.append((name, "\n\n".join(all_cells)))
        return items

    def flush_control_items(self):
        cur = self.control_items
        self.control_items = []
        return cur

    def is_dirty(self):
        return len(self.dirty) > 0

    def line_to_task(self, name:str, line:int):
        for task, (start, end) in self.task_map[name].items():
            if start <= line <= end:
                return task
        return None

#--------------------------------------------------
# Helpers
#--------------------------------------------------
@dataclass
class ExportParams:
    source_database: str
    database: str
    engine: str
    func_name: str
    inputs: List[Tuple[str, str, Any]]
    out_fields: List[Tuple[str, Any]]
    code: str
    dry_run: bool

#--------------------------------------------------
# Resources
#--------------------------------------------------

class ResourceProvider(ABC):
    def __init__(self, profile: str | None = None, config:Config|None=None):
        super().__init__()
        self.config = config or Config(profile)
        self.delete_on_exit = True
        atexit.register(self.cancel_pending_transactions)

    @property
    def platform(self):
        return self.config.get("platform")

    @abstractmethod
    def reset(self):
        pass

    #--------------------------------------------------
    # Generic
    #--------------------------------------------------

    @abstractmethod
    def get_version(self):
        pass

    #--------------------------------------------------
    # Engines
    #--------------------------------------------------

    @abstractmethod
    def get_engine_sizes(self) -> List[Any]:
        pass

    @abstractmethod
    def list_engines(self, state: str|None = None) -> List[Any]:
        pass

    @abstractmethod
    def get_engine(self, name: str):
        pass

    @abstractmethod
    def is_valid_engine_state(self, name: str):
        pass

    @abstractmethod
    def create_engine(self, name: str, size: str, pool:str=""):
        pass

    @abstractmethod
    def delete_engine(self, name: str):
        pass

    @abstractmethod
    def suspend_engine(self, name: str):
        pass

    @abstractmethod
    def resume_engine(self, name: str):
        pass

    def get_default_engine_name(self) -> str:
        engine = self.config.get("engine")
        if not engine:
            raise Exception("No default engine in your configuration")
        return engine

    def get_app_name(self) -> str:
        return cast(str, self.config.get("rai_app_name", "relationalai"))

    #--------------------------------------------------
    # Transactions
    #--------------------------------------------------
    @abstractmethod
    def get_transaction(self, transaction_id):
        pass

    @abstractmethod
    def list_transactions(self, limit:int, only_active=False, **kwargs) -> List[dict]:
        pass

    @abstractmethod
    def cancel_transaction(self, transaction_id):
        pass

    @abstractmethod
    def cancel_pending_transactions(self):
        pass

    @abstractmethod
    def get_transaction_events(self, transaction_id:str, continuation_token:str) -> dict:
        pass

    #--------------------------------------------------
    # Graphs
    #--------------------------------------------------

    @abstractmethod
    def list_graphs(self) -> List[AvailableModel]:
        pass

    @abstractmethod
    def get_graph(self, name:str):
        pass

    @abstractmethod
    def create_graph(self, name: str):
        pass

    @abstractmethod
    def delete_graph(self, name: str):
        pass

    @abstractmethod
    def clone_graph(self, target_name: str, source_name: str, nowait_durable: bool = True):
        pass

    #--------------------------------------------------
    # Databases
    #--------------------------------------------------

    @abstractmethod
    def get_database(self, database: str):
        pass

    #--------------------------------------------------
    # Models
    #--------------------------------------------------

    @abstractmethod
    def list_models(self, database: str, engine: str):
        pass

    @abstractmethod
    def create_models(self, database: str, engine: str, models:List[Tuple[str, str]]) -> List[Any]:
        pass

    @abstractmethod
    def delete_model(self, database: str, engine: str, name: str):
        pass

    @abstractmethod
    def create_models_code(self, models:List[Tuple[str, str]]) -> str:
        pass

    #--------------------------------------------------
    # Exports
    #--------------------------------------------------

    @abstractmethod
    def list_exports(self, database: str, engine: str):
        pass

    @abstractmethod
    def create_export(self, params: ExportParams):
        pass

    @abstractmethod
    def create_export_table(self, database: str, engine: str, table: str, relation: str, columns: Dict[str, str], code: str, refresh: str|None=None):
        pass

    @abstractmethod
    def delete_export(self, database: str, engine: str, name: str):
        pass

    #--------------------------------------------------
    # Imports
    #--------------------------------------------------

    @abstractmethod
    def list_imports(self, id:str|None, name:str|None, model:str|None, status:str|None, creator:str|None) -> list[Import]:
        pass

    @abstractmethod
    def poll_imports(self, sources:List[str], model:str):
        pass

    @abstractmethod
    def get_import_stream(self, id:str|None, name:str|None):
        pass

    @abstractmethod
    def create_import_stream(self, source: ImportSource, model: str, rate: int, resume: str|None, suspend: str|None, options: dict|None):
        pass

    @abstractmethod
    def change_stream_status(self, stream_id: str, model: str, suspend: bool):
        pass

    @abstractmethod
    def set_imports_engine(self, engine: str):
        pass

    @abstractmethod
    def change_imports_status(self, suspend: bool):
        pass

    @abstractmethod
    def create_import_snapshot(self, source: ImportSource, model: str, options: dict|None):
        pass

    @abstractmethod
    def delete_import(self, import_name: str, model: str):
        pass

    #--------------------------------------------------
    # Exec
    #--------------------------------------------------

    @abstractmethod
    def exec_raw(self, database: str, engine: str, raw_code: str, readonly: bool = True, inputs={}, nowait_durable=False, headers={}) -> Any: # @FIXME: Better type annotation
        pass

    def exec_format(self, database: str, engine: str, raw_code: str, task:m.Task, format:str, readonly: bool = True, inputs={}) -> Any: # @FIXME: Better type annotation
        pass

    @abstractmethod
    def format_results(self, results, task:m.Task|None=None) -> Tuple[DataFrame, List[Any]]:
        pass

    #--------------------------------------------------
    # Types
    #--------------------------------------------------

    @abstractmethod
    def to_model_type(self, model:dsl.Graph, name:str, source:str) -> dsl.Type:
        pass


#--------------------------------------------------
# Client
#--------------------------------------------------

class Client():
    def __init__(
        self,
        resources: ResourceProvider,
        compiler: Compiler,
        database: str,
        config: Config,
        dry_run=False,
        isolated=True,
        keep_model=False,
        nowait_durable=True,
    ):
        self.dry_run = dry_run
        self._source_database = database
        self._database = database[:30] + "_" + config.get_hash() if isolated else database
        self._config = config
        self.compiler = compiler
        self._install_batch = InstallBatch()
        self.resources = resources
        self.keep_model = keep_model
        self.isolated = isolated
        self.batch_span: debugging.Span|None = None

        if not self.dry_run:
            self.create_database(isolated=isolated, nowait_durable=nowait_durable)

    #--------------------------------------------------
    # Database management
    #--------------------------------------------------

    def create_database(self, isolated=True, nowait_durable=True):
        start = time.perf_counter()
        with debugging.span("create_database", source=self._source_database, target=self._database):
            database_exists = self.resources.get_graph(self._source_database)
            if isolated:
                if not database_exists:
                    self.resources.create_graph(self._source_database)
                temp = self._database
                self._database = self._source_database
                self.exec_raw("", readonly=False, internal=True, nowait_durable=True)
                self._database = temp
                self.resources.clone_graph(self._database, self._source_database, nowait_durable=nowait_durable)
            elif not database_exists:
                self.resources.create_graph(self._database)
            if isolated and not self.keep_model:
                atexit.register(self.delete_database)
            debugging.time("create_database", time.perf_counter() - start)

    def delete_database(self):
        if self.resources.delete_on_exit and not self.dry_run:
            self.resources.delete_graph(self._database)

    #--------------------------------------------------
    # Engine
    #--------------------------------------------------

    def get_engine_name(self, name:str|None=None) -> str:
        return str(name or self.resources.config.get("engine"))

    #--------------------------------------------------
    # Error Handling
    #--------------------------------------------------

    def report_errors(self, problems: Dict[str, Any], abort_on_error=True, task=None):
        from .. import errors
        all_errors = []
        undefineds = []

        for problem in problems:
            message = problem.get("message", "")
            report = problem.get("report", "")
            path = problem.get("path", "")
            source_task = self._install_batch.line_to_task(path, problem["start_line"]) or task
            source = debugging.get_source(source_task) or debugging.SourceInfo()
            severity = problem.get("severity", "warning")
            code = problem.get("code")

            if severity in ["error", "exception"]:
                if code == "UNDEFINED_IDENTIFIER":
                    match = re.search(r'`(.+?)` is undefined', message)
                    undefineds.append((match.group(1), source))
                elif "overflowed" in report:
                    all_errors.append(errors.NumericOverflow(problem, source))
                elif abort_on_error:
                    all_errors.append(errors.RelQueryError(problem, source))
            else:
                if code == "ARITY_MISMATCH":
                    errors.ArityMismatch(problem, source)
                elif code == "IC_VIOLATION":
                    all_errors.append(errors.IntegrityConstraintViolation(problem, source))
                elif "corerel" in message and not self._config.get("compiler.show_corerel_errors", None):
                    pass
                else:
                    errors.RelQueryWarning(problem, source)

        if abort_on_error and len(undefineds):
            all_errors.append(errors.UninitializedPropertyException(undefineds))

        if len(all_errors) == 1:
            raise all_errors[0]
        elif len(all_errors) > 1:
            raise errors.RAIExceptionSet(all_errors)

    #--------------------------------------------------
    # Raw
    #--------------------------------------------------

    def load_raw_file(self, path:str):
        content = open(path).read()
        code = self.compiler.compile(dsl.build.raw_task(content))
        self._install_batch.set(path, code)

    def exec_raw(self, code:str, readonly=True, raw_results=True, inputs={}, internal=False, nowait_durable=None, headers={}):
        task = dsl.build.raw_task(code)
        debugging.set_source(task)
        return self.query(task, readonly=readonly, raw_results=raw_results, inputs=inputs, internal=internal, nowait_durable=nowait_durable, headers=headers)

    def exec_control(self, code:str, cb:Callable|None=None):
        self._install_batch.control_items.append((code, cb))

    def install_raw(self, code:str, name:str="pyrel_batch_0"):
        if not name:
            name = "pyrel_batch_0"
        task = dsl.build.raw_task(code)
        debugging.set_source(task)
        out = self.compiler.compile(task)
        self._install_batch.append(name, out, task)

    #--------------------------------------------------
    # Query
    #--------------------------------------------------

    def _query(self, code:str, task:m.Task|None, end_span, readonly=True, raw_results=False, inputs={}, nowait_durable=None, headers={}):
        if nowait_durable is None:
            nowait_durable = self.isolated

        results = self.resources.exec_raw(self._database, self.get_engine_name(), code, readonly=readonly, inputs=inputs, nowait_durable=nowait_durable, headers=headers)
        dataframe, errors = self.resources.format_results(results, task)
        end_span["results"] = dataframe
        end_span["errors"] = errors
        self.report_errors(errors, task=task, abort_on_error=not raw_results)
        return results if raw_results else dataframe

    def _query_format(self, code:str, task:m.Task, end_span, format, readonly=True, inputs={}):
        results, errors = self.resources.exec_format(self._database, self.get_engine_name(), code, task, readonly=readonly, inputs=inputs, format=format)
        # dataframe, errors = self.resources.format_results(results, task)
        end_span["results"] = results
        end_span["errors"] = errors
        # self.report_errors(errors, task=task, abort_on_error=not raw_results)
        # return results if raw_results else dataframe
        return results

    def query(self, task:m.Task, rentrant=False, readonly=True, raw_results=False, inputs={}, format="pandas", tag=None, nowait_durable=None, headers={}, internal=False) -> DataFrame|Any:
        self._install_batch_flush()

        with debugging.span("query", model=self._database, task=task, tag=tag, internal=internal) as end_span:
            code = self.compiler.compile(task)
            if task.has_persist():
                readonly = False
            if self.dry_run:
                return DataFrame()

            start = time.perf_counter()
            if format == "pandas":
                results = self._query(code, task, end_span, readonly=readonly, raw_results=raw_results, inputs=inputs, nowait_durable=nowait_durable, headers=headers)
                debugging.time("query", time.perf_counter() - start, DataFrame() if raw_results else results, internal=internal)
            else:
                results = self._query_format(code, task, end_span, readonly=readonly, inputs=inputs, format=format)
                debugging.time("query", time.perf_counter() - start, DataFrame())
            return results

    def _install_batch_flush(self):
        if not self._install_batch.is_dirty():
            return

        if not self.dry_run:
            with debugging.span("install_batch", model=self._database) as end_span:
                start = time.perf_counter()
                rules = self._install_batch.flush()
                control_items = self._install_batch.flush_control_items()
                control_code = "\n\n".join([c[0] for c in control_items])
                rule_code = self.resources.create_models_code(rules)
                install_code = control_code + rule_code
                dataframe = self._query(install_code, None, end_span, readonly=False, raw_results=True)
                for (_, cb) in control_items:
                    if cb:
                        cb(dataframe)
                debugging.time("install_batch", time.perf_counter() - start, code=install_code)

        debugging.span_end(self.batch_span)
        self.batch_span = None

    def get_install_models(self):
        return self._install_batch.get_all_models()

    def install(self, name, task:m.Task):
        debugging.set_source(task)
        if not self.batch_span:
            self.batch_span = debugging.span_start("rule_batch")
        with debugging.span("rule", model=self._database, task=task, name=name):
            code = self.compiler.compile(task)
            self._install_batch.append("pyrel_batch_0", code, task=task)

    def export_udf(self, name, inputs:List[Tuple[str, m.Var, Any]], outputs, task:m.Task, engine=""):
        self._install_batch_flush()

        cols = task.return_cols()
        if len(outputs) != len(cols):
            raise Exception(f"Expected {len(outputs)} outputs, got {len(cols)}")
        rel_code = self.compiler.compile(task)
        emitted_inputs = [(name, self.compiler.emitter.emit(var), type) for (name, var, type) in inputs]
        outputs = list(zip(cols, outputs))
        if not engine:
            engine = self.get_engine_name()
        params = ExportParams(
            source_database=self._source_database,
            database=self._database,
            engine=engine,
            func_name=name,
            inputs=emitted_inputs,
            out_fields=outputs,
            code=rel_code,
            dry_run=self.dry_run
        )
        self.resources.create_export(params)

    def export_table(self, relation, name, cols, task:m.Task, engine="", refresh=""):
        code = self.compiler.compile(task)
        if not engine:
            engine = self.get_engine_name()
        if not self.dry_run:
            self.resources.create_export_table(self._database, engine, name, relation, cols, code, refresh=refresh)
