from __future__ import annotations
import numbers
from typing import Union

from .. import dsl

# Custom number type
_Number = Union[numbers.Number, dsl.Producer]

# NOTE: Right now, common contains all Rel stdlib relations.
# If the stdlib is split into multiple namespaces, this will have to be updated.
_math_ns = dsl.global_ns.std.common


# ------------------------------
# Basics
# ------------------------------

def abs(value: _Number) -> dsl.Expression:
    return _math_ns.abs(value)

def isclose(x: _Number, y: _Number, tolerance: _Number = 1e-9) -> dsl.Expression:
    return _math_ns.approx_eq(tolerance, x, y)

def cbrt(value: _Number) -> dsl.Expression:
    return _math_ns.cbrt(value)

def log(x: _Number, base: _Number | None = None) -> dsl.Expression:
    if isinstance(x, numbers.Number) and x <= 0:
        raise ValueError("Cannot take the logarithm of a negative number")
    if base is None:
        return _math_ns.natural_log(x)
    return _math_ns.log(base, x)

def sign(x: _Number) -> dsl.Expression:
    return _math_ns.sign(x)

def sqrt(value: _Number) -> dsl.Expression:
    if isinstance(value, numbers.Number) and value < 0:
        raise ValueError("Cannot take the square root of a negative number")
    return _math_ns.sqrt(value)

def trunc_divide(numerator: _Number, denominator: _Number) -> dsl.Expression:
    return _math_ns.trunc_divide(numerator, denominator)


# ------------------------------
# Trigonometry
# ------------------------------

def acos(value: _Number) -> dsl.Expression:
    return _math_ns.acos(value)

def asin(value: _Number) -> dsl.Expression:
    return _math_ns.asin(value)

def atan(value: _Number) -> dsl.Expression:
    return _math_ns.atan(value)

def cos(value: _Number) -> dsl.Expression:
    return _math_ns.cos(value)

def degrees(radians: _Number) -> dsl.Expression:
    return _math_ns.rad2deg(radians)

def radians(degrees: _Number) -> dsl.Expression:
    return _math_ns.deg2rad(degrees)

def sin(value: _Number) -> dsl.Expression:
    return _math_ns.sin(value)

def tan(value: _Number) -> dsl.Expression:
    return _math_ns.tan(value)


# ------------------------------
# Rounding
# ------------------------------

def ceil(value: _Number) -> dsl.Expression:
    return _math_ns.ceil(value)

def floor(value: _Number) -> dsl.Expression:
    return _math_ns.floor(value)


# ------------------------------
# Exports
# ------------------------------

__all__ = [
    "abs",
    "acos",
    "asin",
    "atan",
    "isclose",
    "cbrt",
    "cos",
    "degrees",
    "log",
    "radians",
    "sign",
    "sin",
    "sqrt",
    "tan",
    "trunc_divide",
    "ceil",
    "floor",
]
