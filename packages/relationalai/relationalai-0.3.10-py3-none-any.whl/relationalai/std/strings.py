from __future__ import annotations
from typing import Sequence, Union

from .. import dsl, std

# Custom types
_String = Union[str, dsl.Producer]
_Integer = Union[int, dsl.Producer]

# NOTE: Right now, common contains all Rel stdlib relations.
# If the stdlib is split into multiple namespaces, this will have to be updated.
_str_ns = dsl.global_ns.std.common

#--------------------------------------------------
# Basic String Operations
#--------------------------------------------------

def length(string: _String) -> dsl.Expression:
    return _str_ns.string_length(string)


def lowercase(string: _String):
    return _str_ns.lowercase(string)


def uppercase(string: _String):
    return _str_ns.uppercase(string)


#--------------------------------------------------
# Split, Join, and Concatenate
#--------------------------------------------------

def split(string: _String, separator: _String) -> dsl.Expression:
    ix, part = std.Vars(2)
    _str_ns.string_split(separator, string, ix, part)
    return ix - 1, part  # Return 0-based index


def split_part(string: _String, separator: _String, index: _Integer) -> dsl.Expression:
    return _str_ns.string_split(separator, string, index + 1)  # Convert 0-based to 1-based index


def join(strings: Sequence[_String], separator: _String) -> dsl.Expression:
    model = dsl.get_graph()
    R = dsl.InlineRelation(model, list(enumerate(strings)))
    return _str_ns.string_join(separator, R)


def concat(string1: _String, string2: _String) -> dsl.Expression:
    return _str_ns.concat(string1, string2)


#--------------------------------------------------
# Substrings
#--------------------------------------------------

def contains(string: _String, substring: _String):
    return _str_ns.contains(string, substring)


def ends_with(string: dsl.Producer, suffix: _String):
    return _str_ns.ends_with(string, suffix)


def like(string: _String, pattern: _String):
    return _str_ns.like_match(pattern, string)


#--------------------------------------------------
# Find and Replace
#--------------------------------------------------

def replace(string: _String, old: _String, new: _String) -> dsl.Expression:
    return _str_ns.string_replace(string, old, new)


#--------------------------------------------------
# Regular Expressions
#--------------------------------------------------

def regex_match(string: _String, regex: _String):
    return _str_ns.regex_match(regex, string)


def regex_compile(regex: _String):
    return _str_ns.regex_compile(regex)


#--------------------------------------------------
# Exports
#--------------------------------------------------

__all__ = [
    "concat",
    "contains",
    "ends_with",
    "join",
    "length",
    "like",
    "lowercase",
    "regex_compile",
    "regex_match",
    "replace",
    "uppercase"
]
