from relationalai.errors import AsBoolForNonFilter
from relationalai.metamodel import Builtins
from ..dsl import alias, rel, Vars
from .. import dsl, metamodel as m
from . import graphs, aggregates, strings, math, dates

def as_bool(expr: dsl.Expression) -> dsl.Expression:
    if expr._expr.entity.isa(Builtins.Filter):
        # add a result var
        expr._var = m.Var(Builtins.Unknown)
        prop = dsl.build.property_named("result", [])
        expr._expr.append(prop, expr._var)
        # add the filter to apply at the end
        prev_filter = expr._expr.entity.value
        filter = dsl.build.property_named("filter", [])
        expr._expr.append(filter, m.Var(value=prev_filter))
        # use pyrel_bool_filter to apply the filter and get a bool
        expr._expr.entity = m.Var(value=Builtins.BoolFilter)
    else:
        raise AsBoolForNonFilter()
    return expr

__all__ = [
    "aggregates",
    "alias",
    "dates",
    "graphs",
    "math",
    "rel",
    "strings",
    "Vars"
]