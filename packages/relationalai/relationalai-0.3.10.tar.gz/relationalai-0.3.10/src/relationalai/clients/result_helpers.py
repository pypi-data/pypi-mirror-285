from collections import defaultdict
from functools import reduce
import re
from typing import Any, List, Tuple
import base64

import numpy as np
from pandas import DataFrame
import pandas as pd
import decimal
from .. import metamodel as m

#--------------------------------------------------
# Constants
#--------------------------------------------------

UNIXEPOCH = 62135683200000
MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000

#--------------------------------------------------
# Result formatting
#--------------------------------------------------

def format_columns(result_frame:DataFrame, types:List[str]):
    for i, col in enumerate(result_frame.columns):
        if "UInt128" in types[i]:
            result_frame[col] = result_frame[col].apply(decode_uint128)
        elif "FixedDecimal" in types[i]:
            decimal_info = re.search(r"FixedDecimal\{Int(\d+), (\d+)\}", types[i])
            if decimal_info:
                bits = int(decimal_info.group(1))
                scale = int(decimal_info.group(2))
                if bits == 128:
                    result_frame[col] = result_frame[col].apply(lambda x: (decimal.Decimal(str((int(x[1]) << 64) + int(x[0]))) if x[1] > 0 else decimal.Decimal(str(x[0]))) / (10 ** scale))
                else:
                    result_frame[col] = result_frame[col].apply(lambda x: decimal.Decimal(str(x)) / (10 ** scale))
        elif "Int128" in types[i]:
            result_frame[col] = result_frame[col].apply(lambda x: (int(x[1]) << 64) + int(x[0]) if x[1] > 0 else x[0])
        elif "Missing" in types[i]:
            result_frame[col] = result_frame[col].apply(lambda x: None)
        elif types[i] == "Dates.DateTime":
            result_frame[col] = pd.to_datetime(result_frame[col] - UNIXEPOCH, unit="ms")
        elif types[i] == "Dates.Date":
            result_frame[col] = pd.to_datetime(result_frame[col] * MILLISECONDS_PER_DAY - UNIXEPOCH, unit="ms")
    return result_frame

def decode_uint128(x):
    if isinstance(x, dict):
        keys = sorted(x.keys())
        result = []
        for key in keys:
            value = x[key]
            if isinstance(value, np.ndarray):
                result.extend(value)
            elif isinstance(value, (int, np.integer)):
                result.append(value)
            else:
                raise ValueError(f"Unsupported type for key {key}: {type(value)}")

        return decode_uint128(np.array(result, dtype=np.uint64))

    elif isinstance(x, np.ndarray):
        return base64.b64encode(x.tobytes()).decode()[:-2]

    else:
        raise ValueError(f"Unsupported input type: {type(x)}")

def convert_hash_value(value):
    if isinstance(value, np.ndarray):
        return tuple(value)
    return value

def merge_columns(left:DataFrame, right:DataFrame, on:List[str]):
    if not len(left.columns):
        for col in on:
            left.insert(loc=len(left.columns), column=col, value=np.nan)
    if left.empty:
        col_count = len(left.columns)
        left.insert(loc=col_count, column=f'new_column{col_count}', value=np.nan)
    if right.empty:
        col_count = len(left.columns)
        left.insert(loc=col_count, column=f'new_column{col_count}', value=np.nan)
        return left
    return pd.merge(left, right, on=on, how='outer')

def format_results(results, task:m.Task) -> Tuple[DataFrame, List[Any]]:
    data_frame = DataFrame()
    problems = defaultdict(
        lambda: {
            "message": "",
            "path": "",
            "start_line": None,
            "end_line": None,
            "report": "",
            "code": "",
            "severity": "",
            "decl_id": "",
            "name": "",
            "output": "",
            "end_character": None,
            "start_character": None,
        }
    )

    # Check if there are any results to process
    if len(results.results):
        ret_cols = task.return_cols() if task else []
        has_cols:List[DataFrame] = [DataFrame() for _ in range(0, len(ret_cols))]
        key_len = 0
        for result in results.results:
            relation_id = result["relationId"]
            result_frame = result["table"].to_pandas()

            # Process diagnostics
            if "/:rel/:catalog/:diagnostic/" in relation_id:
                # Handle different types of diagnostics based on relation_id
                if "/:message/" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[row.iloc[0]]["message"] = row.iloc[1]
                elif "/:report/" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[row.iloc[0]]["report"] = row.iloc[1]
                elif "/:start/:line" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 2:
                            problems[row.iloc[0]]["start_line"] = row.iloc[2]
                elif "/:end/:line" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 2:
                            problems[row.iloc[0]]["end_line"] = row.iloc[2]
                elif "/:model" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[row.iloc[0]]["path"] = row.iloc[1]
                elif "/:severity" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[row.iloc[0]]["severity"] = row.iloc[1]
                elif "/:code" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[row.iloc[0]]["code"] = row.iloc[1]

            # Process integrity constraint violations
            elif "/:rel/:catalog/:ic_violation" in relation_id:
                if "/:decl_id" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["decl_id"] = (
                                row.iloc[1]
                            )
                            problems[convert_hash_value(row.iloc[0])]["code"] = (
                                "IC_VIOLATION"
                            )
                elif "/:model" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["path"] = (
                                row.iloc[1]
                            )
                elif "/:name" in relation_id:
                    # Get the last segment of the relation_id as the name
                    segments = [
                        segment[1:]
                        for segment in relation_id.split("/")[4:]
                        if segment.startswith(":")
                    ]
                    for _, row in result_frame.iterrows():
                        problems[convert_hash_value(row.iloc[0])]["name"] = segments[-1]
                elif "/:output" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["message"] = (
                                row.iloc[1]
                            )
                elif "/:range/:end/:character" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])][
                                "end_character"
                            ] = row.iloc[1]
                elif "/:range/:end/:line" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["end_line"] = (
                                row.iloc[1]
                            )
                elif "/:range/:start/:character" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])][
                                "start_character"
                            ] = row.iloc[1]
                elif "/:range/:start/:line" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["start_line"] = (
                                row.iloc[1]
                            )
                elif "/:report" in relation_id:
                    for _, row in result_frame.iterrows():
                        if len(row) > 1:
                            problems[convert_hash_value(row.iloc[0])]["report"] = (
                                row.iloc[1]
                            )

            # Process other results
            else:
                types = [
                    t
                    for t in result["relationId"].split("/")
                    if t != "" and not t.startswith(":")
                ]
                result_frame = format_columns(result_frame, types)
                result["table"] = result_frame
                if ":output/:cols" in result["relationId"]:
                    col_ix = int(
                        re.search(r":col([0-9]+)", result["relationId"]).group(1)
                    )
                    key_cols = [
                        f"id{i}" for i in range(0, len(result_frame.columns) - 1)
                    ]
                    key_len = len(key_cols)
                    result_frame.columns = [*key_cols, f"v{col_ix}"]
                    if has_cols[col_ix].empty:
                        has_cols[col_ix] = result_frame
                    else:
                        has_cols[col_ix] = pd.concat([has_cols[col_ix], result_frame], ignore_index=True)
                elif ":output" in result["relationId"]:
                    data_frame = pd.concat(
                        [data_frame, result_frame], ignore_index=True
                    )

        if any(not col.empty for col in has_cols):
            key_cols = [f"id{i}" for i in range(0, key_len)]
            df_wide_reset = reduce(lambda left, right: merge_columns(left, right, key_cols), has_cols)
            data_frame = df_wide_reset.drop(columns=key_cols)
            data_frame.sort_values(by=[str(c) for c in data_frame.columns], ascending=[True] * len(data_frame.columns), inplace=True)
            data_frame = data_frame.reset_index(drop=True)

        if len(ret_cols) and len(data_frame.columns) == len(ret_cols):
            data_frame.columns = task.return_cols()[0 : len(data_frame.columns)]
    return (data_frame, list(problems.values()))
