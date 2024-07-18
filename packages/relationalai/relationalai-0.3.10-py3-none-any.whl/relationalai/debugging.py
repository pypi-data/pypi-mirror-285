from __future__ import annotations
import ast
import contextlib
from dataclasses import dataclass
import datetime
import inspect
import io
import json
import sys
from textwrap import dedent
import os
from types import TracebackType
from typing import Dict
import logging
import uuid
import warnings

import numpy as np

from pandas import DataFrame

from relationalai.errors import InvalidIfWarning, InvalidLoopWarning, InvalidTryWarning, RAIException, RAIExceptionSet, RAIWarning
from .metamodel import Action, Task

DEBUG = True
handled_error = None

#--------------------------------------------------
# Global Warning Handling
#--------------------------------------------------

# Save the original warnings.showwarning
original_showwarning = warnings.showwarning

def global_warning_handler(message, category, filename, lineno, file=None, line=None):
    if isinstance(message, RAIWarning):
        message.pprint()
    else:
        # Use the original showwarning for non-RAIWarning warnings
        original_showwarning(message, category, filename, lineno, file, line)

def install_warninghook():
    # Override the default showwarning with the custom one
    warnings.showwarning = global_warning_handler

#--------------------------------------------------
# Global Error Handling
#--------------------------------------------------

def global_exception_handler(exc_type, exc_value, exc_traceback, quiet=False):
    global handled_error

    is_set = isinstance(exc_value, RAIExceptionSet)

    if is_set:
        for err in exc_value.exceptions:
            err.pprint()
            error(err)
    elif isinstance(exc_value, RAIException):
        exc_value.pprint()

    # Ensure exc_value is actually an exception instance
    if isinstance(exc_value, BaseException) and not is_set:
        error(exc_value)

    handled_error = None

    if original_excepthook is not None:
        original_excepthook(exc_type, exc_value, exc_traceback)

original_excepthook = None

def ipy_exception_handler(shell, exc_type, exc_value, exc_traceback: TracebackType | None, tb_offset=1):
    with contextlib.redirect_stdout(io.StringIO()) as buffer:
        global_exception_handler(exc_type, exc_value, exc_traceback, True)

    if isinstance(exc_value, RAIException):
        pprinted = buffer.getvalue().strip()
        # remove the trailing divider
        pprinted = pprinted[:pprinted.rfind("\n")]
        # We strip the most _recent_ frame (rather than the top frame) because it's always part of our error handling
        exc_traceback = drop_last_frame(exc_traceback)
        exc_value = Exception(exc_value.name).with_traceback(exc_traceback)

        print(pprinted, file=sys.stderr)

    # @NOTE: We could completely takeover display for RAIExceptions to
    #        have finer control over the display, but I went with the
    #        less invasive approach for now.
    shell.showtraceback((exc_type, exc_value, exc_traceback), tb_offset=tb_offset)

def setup_exception_handler():
    try:
        from IPython import get_ipython  # type: ignore

        ipython = get_ipython()
        if ipython:
            ipython.set_custom_exc((BaseException,), ipy_exception_handler)
            return
    except Exception:
        pass

    global original_excepthook
    original_excepthook = sys.excepthook
    sys.excepthook = global_exception_handler


def drop_last_frame(tb: TracebackType | None):
    if tb is None or tb.tb_next is None:
        return None

    tail = drop_last_frame(tb.tb_next)
    return TracebackType(tail, tb.tb_frame, tb.tb_lasti, tb.tb_lineno)

#--------------------------------------------------
# Log Formatters
#--------------------------------------------------

def encode_log_message(obj):
    if isinstance(obj, DataFrame):
        # Replace NaN with None to avoid JSON serialization issues
        df = obj.replace({np.nan: None})
        return df.head(20).to_dict(orient="records")
    if isinstance(obj, datetime.datetime):
        return obj.isoformat() + "Z"
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "to_json"):
        return obj.to_json()
    else:
        return str(obj)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(record.msg, default=encode_log_message)

#--------------------------------------------------
# Logging
#--------------------------------------------------

logger = logging.getLogger("pyrellogger")
logger.setLevel(logging.DEBUG)
logger.propagate = False

#--------------------------------------------------
# File Logger
#--------------------------------------------------

class FlushingFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

with open('debug.jsonl', 'w'):
    pass

# keep the old file-based debugger around and working until it's fully replaced.
if DEBUG:
    file_handler = FlushingFileHandler('debug.jsonl', mode='a')
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

#--------------------------------------------------
# Test Logger
#--------------------------------------------------

# class TestHandler(logging.Handler):
#     def emit(self, record):
#         d = record.msg
#         if not isinstance(d, dict):
#             return

#         print(d["event"], d.get("span", None), d.get("elapsed", None))

# if DEBUG:
#     logger.addHandler(TestHandler())

#--------------------------------------------------
# Debug Spans
#--------------------------------------------------

# The deepest span in the tree
TIP_SPAN: 'Span | None' = None

def get_current_span_id() -> str | None:
    if TIP_SPAN is None:
        return None
    return str(TIP_SPAN.id)

def span_start(type: str, **kwargs) -> 'Span':
    global TIP_SPAN
    span = Span(type, TIP_SPAN, kwargs)
    TIP_SPAN = span

    if DEBUG:
        logger.debug({"event": "span_start", "span": span})

    return span

def span_end(span):
    if not DEBUG:
        return

    global TIP_SPAN
    TIP_SPAN = span.parent
    span.mark_finished()

    logger.debug({
        "event": "span_end",
        "id": str(span.id),
        "end_timestamp": span.end_timestamp.isoformat() + "Z",
        "end_attrs": span.end_attrs,
    })

def span_flush():
    while TIP_SPAN:
        span_end(TIP_SPAN)

class Span:
    def __init__(self, type: str, parent, attrs: Dict):
        self.id = uuid.uuid4()
        self.parent = parent
        self.type = type
        self.attrs = attrs
        # additional attributes added during the lifetime of the span
        self.end_attrs = {}
        # Would use `datetime.datetime.now(datetime.UTC)`, but it only works in 3.11.
        self.start_timestamp = datetime.datetime.utcnow()
        self.end_timestamp = None

    def mark_finished(self):
        self.end_timestamp = datetime.datetime.utcnow()

    def __setitem__(self, key, value):
        self.end_attrs[key] = value

    def to_json(self):
        return {
            "type": self.type,
            "id": str(self.id),
            "parent_id": str(self.parent.id) if self.parent else None,
            "start_timestamp": self.start_timestamp.isoformat() + "Z",
            "end_timestamp": None if self.end_timestamp is None else (self.end_timestamp.isoformat() + "Z"),
            "attrs": self.attrs,
        }

@contextlib.contextmanager
def span(type: str, **kwargs) -> Span:
    cur = span_start(type, **kwargs)
    try:
        yield cur
    except Exception as err:
        error(err)
        raise
    finally:
        span_end(cur)

def set_span_attr(attr, value):
    global TIP_SPAN
    TIP_SPAN.attrs[attr] = value

#--------------------------------------------------
# Debug Events
#--------------------------------------------------

EMPTY = {}

def event(event:str, parent:Span|None = None, **kwargs):
    if not DEBUG:
        return

    if not parent:
        parent = TIP_SPAN

    d = {
        "event":event,
        "timestamp": datetime.datetime.utcnow(),
        "parent_id": parent.id if parent else None,
        **kwargs
    }
    logger.debug(d)

def time(type:str, elapsed:float, results:DataFrame = DataFrame(), **kwargs):
    if DEBUG:
        event("time", type=type, elapsed=elapsed, results={
            "values": results,
            "count": len(results)
        }, **kwargs)

def error(err:Exception):
    global handled_error
    if err != handled_error and not isinstance(err, RAIExceptionSet):
        # Prepare kwargs from exception attributes if it's a custom exception
        kwargs = {}

        if hasattr(err, '__dict__'):
            kwargs = {key: getattr(err, key) for key in err.__dict__ if not key.startswith('_')}

        event("error", err=err, span_id=get_current_span_id(), **kwargs)  # Emit the error event only if it's a new or different error
        for handler in logger.handlers:
            handler.flush()
        handled_error = err

def handle_compilation(compilation):
    if not DEBUG:
        return

    (file, line, block) = compilation.get_source()
    source = {"file": file, "line": line, "block": block}
    passes = [{"name": p[0], "task": p[1], "elapsed": p[2]} for p in compilation.passes]
    emitted = compilation.emitted
    if isinstance(emitted, list):
        emitted = "\n\n".join(emitted)

    event("compilation", source=source, task=compilation.task, passes=passes, emitted=emitted, emit_time=compilation.emit_time)


def warn(warning: Warning):
    if not DEBUG:
        return

    kwargs = {}

    if hasattr(warning, "__dict__"):
        kwargs = {
            key: getattr(warning, key)
            for key in warning.__dict__
            if not key.startswith("_")
        }

    event("warn", warning=warning, **kwargs)


#--------------------------------------------------
# SourceInfo
#--------------------------------------------------

@dataclass
class SourceInfo:
    file: str = "Unknown"
    line: int = 0
    source: str = ""
    block: ast.AST|None = None

    def modify(self, transformer:ast.NodeTransformer):
        if not self.block:
            raise Exception("Cannot modify source info without a block")

        new_block = transformer.visit(self.block)
        return SourceInfo(self.file, self.line, ast.unparse(new_block), new_block)

    def to_json(self):
        return {
            "file": self.file,
            "line": self.line,
            "source": self.source
        }

#--------------------------------------------------
# Jupyter
#--------------------------------------------------

class Jupyter:
    def __init__(self):
        self.dirty_cells = set()
        try:
            from IPython import get_ipython # type: ignore
            self.ipython = get_ipython()
            if self.ipython:
                self.ipython.events.register('pre_run_cell', self.pre_run_cell)
                self.ipython.events.register('post_run_cell', self.post_run_cell)
                self.dirty_cells.add(self.cell())
        except ImportError:
            self.ipython = None

    def pre_run_cell(self, info):
        self.dirty_cells.add(info.cell_id)

    def post_run_cell(self, result):
        try:
            from . import dsl
            graph = dsl.get_graph()
            if graph._temp_is_active():
                graph._flush_temp()
                graph._restore_temp()
        except Exception:
            return

    def cell_content(self):
        if self.ipython:
            last_input = self.ipython.user_ns['In'][-1]
            return (last_input, f"In[{len(self.ipython.user_ns['In']) - 1}]")
        return ("", "")

    def is_colab(self):
        if not self.ipython:
            return False
        try:
            parent = self.ipython.get_parent() #type: ignore
        except Exception:
            return False
        if not parent or "metadata" not in parent:
            return False
        return "colab" in parent["metadata"]

    def cell(self):
        if self.ipython:
            if self.is_colab():
                return self.ipython.get_parent()["metadata"]["colab"]["cell_id"] #type: ignore
            else:
                try:
                    return self.ipython.get_parent()["metadata"]["cellId"] #type: ignore
                except Exception:
                    return None
        return None

jupyter = Jupyter()

#--------------------------------------------------
# Position capture
#--------------------------------------------------

rai_site_packages = os.path.join("site-packages", "relationalai")
rai_src = os.path.join("src", "relationalai")

def first_non_relationalai_frame(frame):
    while frame and frame.f_back:
        file = frame.f_code.co_filename
        if rai_site_packages not in file and rai_src not in file:
            break
        frame = frame.f_back
    return frame

def capture_code_info(steps=None):
    # Get the current frame and go back to the caller's frame
    caller_frame = inspect.currentframe()
    if steps is not None:
        for _ in range(steps):
            if not caller_frame or not caller_frame.f_back:
                break
            caller_frame = caller_frame.f_back
    else:
        caller_frame = first_non_relationalai_frame(caller_frame)

    if not caller_frame:
        return

    caller_filename = caller_frame.f_code.co_filename
    caller_line = caller_frame.f_lineno

    relative_filename = os.path.relpath(caller_filename, os.getcwd())

    # Read the source code from the caller's file
    source_code = None
    try:
        with open(caller_filename, "r") as f:
            source_code = f.read()
    except IOError:
        (jupyter_code, jupyter_cell) = jupyter.cell_content()
        if jupyter_code:
            source_code = jupyter_code
            relative_filename = jupyter_cell

    if not source_code:
        return SourceInfo(relative_filename, caller_line)
    else:
        return find_block_in(source_code, caller_line, relative_filename)

def find_block_in(source_code: str, caller_line: int, relative_filename: str):
    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Find the node that corresponds to the call
    class BlockFinder(ast.NodeVisitor):
        def __init__(self, target_lineno):
            self.target_lineno = target_lineno
            self.block_node = None

        def generic_visit(self, node):
            if hasattr(node, "lineno") and node.lineno == self.target_lineno:
                self.block_node = node
                # Stop visiting once the target node is found
                return
            ast.NodeVisitor.generic_visit(self, node)

    finder = BlockFinder(caller_line)
    finder.visit(tree)

    if finder.block_node:
        # Extract the lines from the source code
        start_line = finder.block_node.lineno
        end_line = getattr(finder.block_node, "end_lineno", start_line)

        block_lines = source_code.splitlines()[start_line - 1:end_line]
        block_code = "\n".join(block_lines)
        return SourceInfo(relative_filename, caller_line, dedent(block_code), finder.block_node)

    lines = source_code.splitlines()
    if caller_line > len(lines):
        return SourceInfo(relative_filename, caller_line)
    return SourceInfo(relative_filename, caller_line, lines[caller_line - 1])

def check_errors(task:Task|Action):
    class ErrorFinder(ast.NodeVisitor):
        def __init__(self, start_line):
            self.errors = []
            self.start_line = start_line

        def to_line_numbers(self, node):
            return (node.lineno, node.end_lineno)

        def generic_visit(self, node):
            if isinstance(node, ast.If):
                InvalidIfWarning(task, *self.to_line_numbers(node))
            elif isinstance(node, ast.For) or isinstance(node, ast.While):
                InvalidLoopWarning(task, *self.to_line_numbers(node))
            elif isinstance(node, ast.Try):
                InvalidTryWarning(task, *self.to_line_numbers(node))

            ast.NodeVisitor.generic_visit(self, node)

    source = get_source(task)
    if not source or not source.block:
        return
    ErrorFinder(source.line).visit(source.block)


sources:Dict[Task|Action, SourceInfo|None] = {}
def set_source(item, steps=1, dynamic=False):
    if not DEBUG or item in sources:
        return
    found = capture_code_info()
    if found:
        sources[item] = found
        if not dynamic:
            check_errors(item)
            pass
    return found

def get_source(item):
    return sources.get(item)
