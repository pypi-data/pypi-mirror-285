from __future__ import annotations
from collections import defaultdict
import numbers
from typing import Any, Dict, Iterable, List, Set, cast

from .rel_emitter import Emitter

from .metamodel import Behavior, Builtins, Action, ActionType, Type, Var, Task
from . import metamodel as m
from . import compiler as c
from .clients import config
from .dsl import build
from . import dsl

gather_vars = m.Utils.gather_vars
gather_task_vars = m.Utils.gather_task_vars

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def is_static(x:Any):
    if isinstance(x, m.Action):
        return all([is_static(z) for z in x.bindings.values()])
    if isinstance(x, Var):
        return x.value is not None
    if isinstance(x, Type):
        return True
    if isinstance(x, str):
        return True
    if isinstance(x, numbers.Number):
        return True
    if isinstance(x, list):
        return all(is_static(i) for i in x)
    if isinstance(x, tuple):
        return all(is_static(i) for i in x)
    if isinstance(x, dict):
        return all(is_static(i) for i in x.values())
    return False

def prepend_bindings(prefix:List[Var], action:Action):
    neue_bindings = {}
    for i, var in enumerate(prefix):
        neue_bindings[Builtins.Relation.properties[i]] = var
    prop_len = len(neue_bindings)
    for v in action.bindings.values():
        neue_bindings[Builtins.Relation.properties[prop_len]] = v
        prop_len += 1
    action.bindings = neue_bindings

#--------------------------------------------------
# OrderedSet
#--------------------------------------------------

class OrderedSet:
    def __init__(self):
        self.set:Set[Var] = set()
        self.list:List[Var] = []

    def add(self, item):
        if item not in self.set:
            self.set.add(item)
            self.list.append(item)

    def update(self, items:Iterable[Any]):
        for item in items:
            self.add(item)

    def __getitem__(self, ix):
        return self.list[ix]

    def __contains__(self, item):
        return item in self.set

    def __bool__(self):
        return bool(self.set)

    def __iter__(self):
        return iter(self.list)

#--------------------------------------------------
# FlowFrame
#--------------------------------------------------

class FlowFrame:
    multi_names = set()

    def __init__(self, task:Task, prev:'FlowFrame|None'=None):
        self.task = task
        self.finalized = False
        self.demands:Dict[Var, List[Action]] = defaultdict(list)
        self.flushed_vars = set()
        self.keys:Dict[Var, Var] = {}
        self.multi = set()
        self.prev = prev
        self.merge(prev)

    def merge(self, other:'FlowFrame|None'):
        if not other:
            return

        for (k, vs) in other.demands.items():
            for v in vs:
                if v not in self.demands[k]:
                    self.demands[k].append(v)
        for (k, v) in other.keys.items():
            self.keys[k] = v
        self.multi.update(other.multi)
        self.flushed_vars.update(other.flushed_vars)

    def push_demand(self, var:Var, action:Action, with_key=None):
        for a in self.demands[var]:
            if a.equiv(action):
                return
        self.demands[var].append(action)
        if with_key:
            self.push_key(var, with_key)

    def demand(self, var):
        ret = self.demands.get(var, [])
        if var in self.demands:
            del self.demands[var]
        self.flushed_vars.add(var)
        return ret

    def has_demand(self, var):
        return var in self.demands or var in self.flushed_vars

    def is_unique_demand(self, var, action:Action):
        for a in self.demands[var]:
            if a.equiv(action):
                return False
        return True

    def demands_available(self):
        return set(self.demands.keys())

    def check_multi_prop(self, prop:m.Property, var:Var|None=None):
        # For queries we need to know if a property is multi-valued so we can include
        # it in the key of the split up return. This doesn't apply to rules, so by the
        # time a query is called if we don't know that a prop is multi, it doesn't really
        # matter since it can't affect the results.
        if prop.name in self.multi_names or Builtins.MultiValued in prop.parents:
            self.multi_names.add(prop.name)
            if var and var.value is None:
                self.multi.add(var)
            return True
        return False

    def is_multi(self, var:Var):
        return var in self.multi

    def push_key(self, var:Var, key:Var):
        self.keys[var] = key

    def key(self, var, default):
        return self.keys.get(var, default)

    def has_action(self, action:Action):
        for a in self.task.items:
            if a.equiv(action):
                return True
        return False

    def keys_recursive(self, var):
        key = self.keys.get(var)
        if key and key != var:
            recur = self.keys_recursive(key)
            if key not in recur:
                return recur + [key]
            elif recur:
                return recur
            else:
                return [key]
        elif key:
            return [key]
        return []

    def is_empty_continue(self):
        if len(self.task.items) == 1 \
            and self.prev \
            and self.task.items[0].action == ActionType.Get \
            and self.task.items[0].entity.value == self.prev.task:
            return True

    def is_empty(self):
        return not len(self.task.items) and not len(self.task.bindings)

    def create_get(self, var_mapping:Dict[Var, Var]={}) -> Action:
        if Builtins.InlineAnnotation not in self.task.parents:
            self.task.parents.append(Builtins.InlineAnnotation)
        vars = gather_task_vars(self.task, only_direct_children=True)
        if not self.finalized:
            self.finalized = True
            self.task.items.append(build.relation_action(ActionType.Bind, self.task, vars))
        return build.relation_action(ActionType.Get, self.task, [var_mapping.get(v, v) for v in vars])

    def is_keylike_var(self, var: Var):
        key = self.key(var, None)
        return self.is_multi(var) or key is None or key == var

#--------------------------------------------------
# Flow
#--------------------------------------------------

class Flow():
    def __init__(self):
        self.tasks:List[Task] = []
        self.frames:List[FlowFrame] = []

    def frame(self):
        return self.frames[-1]

    def reset(self):
        self.tasks.clear()
        self.frames = []

    def _prev_frame(self, pop=False):
        if not self.frames:
            return None
        prev_frame = self.frames.pop() if pop else self.frames[-1]
        if prev_frame and prev_frame.is_empty_continue():
            grand_parent = prev_frame.prev
            if grand_parent:
                grand_parent.merge(prev_frame)
            if prev_frame.task in self.tasks:
                self.tasks.remove(prev_frame.task)
            return grand_parent
        return prev_frame

    def branch(self, inline=False, ignore_deps=False, var_mapping:Dict[Var,Var]={}):
        neue = Task()
        prev_frame = self._prev_frame()
        self.frames.append(FlowFrame(neue, prev_frame))
        if not inline:
            self.tasks.append(neue)
        if not ignore_deps and prev_frame and not prev_frame.is_empty():
            self.append(prev_frame.create_get(var_mapping))
        return neue

    def join(self, discard=False):
        frame = self.frames.pop()
        if discard:
            self.tasks.remove(frame.task)
        return frame.task

    def continue_(self):
        # remove the original root frame, and use it as the root of the continuation frame
        prev = cast(FlowFrame, self._prev_frame(pop=True))
        neue = Task()
        self.frames.append(FlowFrame(neue, prev))
        if not prev.is_empty():
            self.append(prev.create_get())
        self.tasks.append(neue)
        return neue

    def append(self, action:Action):
        task = self.frame().task
        for item in task.items:
            if item.equiv(action):
                return
        task.items.append(action)

    def available_vars(self):
        frame = self.frame()
        return gather_task_vars(frame.task) | frame.demands_available()

    def finalize(self):
        final_tasks = []
        for task in self.tasks[:-1]:
            if len(task.items) or len(task.bindings):
                final_tasks.append(task)

        # We'll often end up with a task at the end that is the continuation with
        # no items or bindings, aside from a reference to the previous task, we
        # ignore those
        if not final_tasks or len(self.tasks[-1].bindings) or len(self.tasks[-1].items) > 1:
            final_tasks.append(self.tasks[-1])

        return final_tasks

#--------------------------------------------------
# Dataflow
#--------------------------------------------------

class Dataflow(c.Pass):
    def __init__(self, copying=True) -> None:
        super().__init__(copying)
        self.flow = Flow()

    def reset(self):
        super().reset()
        self.flow.reset()

    #--------------------------------------------------
    # Query
    #--------------------------------------------------

    def query(self, query: Task, parent=None):
        self.query_flow(query)
        if not parent:
            final_tasks = self.flow.finalize()
            query.behavior = Behavior.Sequence
            query.items = [build.relation_action(ActionType.Call, task, []) for task in final_tasks]

    def query_flow(self, task:Task, inline=False, ignore_deps=False, always_demand=False, raw_return=False):
        flow = self.flow
        flow.branch(ignore_deps=ignore_deps)

        for orig in task.items:
            ent:Any = orig.entity
            if orig.is_subtask_call():
                behavior = ent.value.behavior
                if behavior == Behavior.Union:
                    self.union_call(orig)
                elif behavior == Behavior.OrderedChoice:
                    self.ordered_choice_call(orig)
                elif behavior == Behavior.Query:
                    self.walk(orig, task)
                    flow.continue_()
            elif ent.isa(Builtins.Quantifier):
                self.quantifier_call(orig)
            elif ent.isa(Builtins.Aggregate):
                self.aggregate_call(orig)
            else:
                self.check_demand(orig, always_demand=always_demand, raw_return=raw_return)

        return flow.join()

    #--------------------------------------------------
    # Demand handling
    #--------------------------------------------------

    def check_demand(self, action:Action, always_demand=False, raw_return=False):
        flow = self.flow
        frame = self.flow.frame()

        if isinstance(action.entity.value, m.Property):
            frame.check_multi_prop(action.entity.value, action.params_list()[-1])

        # statics and always demands just get added directly
        if is_static(action) or always_demand:
            self.demand_action(action)

        # for non-relation gets (Types and Props) we need to store the demand
        elif action.action == ActionType.Get and not action.entity.isa(Builtins.Relation):
            self.store_demand(action)

        # Handle identity specially so we can break up big chains of adds
        elif action.entity.isa(Builtins.make_identity):
            self.demand_identity(action)

        # store construct calls
        elif action.action == ActionType.Construct:
            value = action.params_list()[-1]
            frame.push_demand(value, action)

        # For returns, we either split or keep it as is
        elif action.entity.isa(Builtins.Return):
            if not raw_return:
                self.split_return(action)
            else:
                self.demand_action(action)

        # For effects, we need to branch the flow so any demands don't kill the
        # original flow
        elif action.action.is_effect():
            flow.branch()
            self.demand_action(action)
            flow.join()
            flow.continue_()

        # For everything else, we just demand the vars and add the action
        else:
            self.demand_action(action)

    def store_demand(self, action:Action):
        flow = self.flow
        frame = flow.frame()
        root = action.entity.value
        if isinstance(root, m.Property):
            [key, value] = action.params_list()
            if is_static(value):
                self.demand_action(action)
            elif frame.has_demand(value) and frame.is_unique_demand(value, action):
                self.demand_action(action)
            elif frame.has_demand(key):
                self.demand(key)
                frame.push_demand(value, action, with_key=key)
            else:
                frame.push_demand(value, action, with_key=key)
        elif isinstance(root, m.Type):
            [key] = action.params_list()
            frame.push_demand(key, action)
            if not frame.key(key, None):
                frame.push_key(key, key)

    def demand_identity(self, action:Action):
        flow = self.flow
        frame = flow.frame()
        # if there are few vars leading into this add, we'll reify the identities
        # so that if there are many properties we only do the join once. 4 was chosen
        # randomly as a small arity
        flow.branch()
        cur_frame = flow.frame()
        self.demand_action(action)
        child_vars = gather_task_vars(cur_frame.task, only_direct_children=True)
        # include variables that are keys so that they'll properly join to the
        # correct ID downstream
        out_var = action.params_list()[-1]
        shared_vars = [c for c in child_vars if frame.is_keylike_var(c) and c != out_var]
        vars = [*shared_vars, out_var]
        if len(vars) <= 4:
            self.flow.append(build.relation_action(ActionType.Bind, cur_frame.task, vars))
            flow.join()
            flow.continue_()
            flow.frame().push_demand(vars[-1], build.relation_action(ActionType.Get, cur_frame.task, vars))
        else:
            # otherwise, just defer the identity demand and reify in each prop
            flow.join(discard=True)
            value = action.params_list()[-1]
            frame.push_demand(value, action)

    def demand_action(self, action:Action):
        for demand in action.vars(recursive=True):
            self.demand(demand)
        self.flow.append(action)

    def demand(self, var:Var, is_return=False, allow_missing=False):
        frame = self.flow.frame()
        for cur in frame.demand(var):
            if not frame.has_action(cur):
                if isinstance(cur.entity.value, m.Property):
                    [key, value] = cur.params_list()
                    if is_return and (allow_missing or frame.check_multi_prop(cur.entity.value)):
                        cur = build.relation_action(ActionType.Call, dsl.rel.pyrel_default._rel, [cur.entity.value, Builtins.Missing, key, value])
                    self.demand(key)
                elif cur.action == ActionType.Construct:
                    self.demand_action(cur)
                    continue
                elif isinstance(cur.entity.value, m.Type):
                    # For arbitrary relations (pyrel_default, make_identity), we need to demand keys
                    for key in cur.vars(recursive=True):
                        self.demand(key)
                self.flow.append(cur)

    #--------------------------------------------------
    # Return splitting
    #--------------------------------------------------

    def split_return(self, action:Action):
        flow = self.flow
        frame = flow.frame()

        all_keys = []
        hidden_keys = []
        unkeyed = []
        ret_params = action.params_list()
        is_distinct = action.entity.isa(Builtins.Distinct)

        available_roots = set()
        for ret in ret_params:
            if ret == frame.key(ret, None):
                available_roots.add(ret)

        for ret in ret_params:
            last_key = frame.key(ret, None)
            has_key = last_key and (not is_distinct or last_key in available_roots)

            if not has_key and last_key:
                if last_key not in hidden_keys:
                    hidden_keys.append(last_key)
                unkeyed.append(ret)
                self.demand(ret, is_return=True, allow_missing=True)
            elif has_key and last_key not in all_keys:
                all_keys.append(last_key)
            elif not last_key and ret.value is None:
                unkeyed.append(ret)

        multis = [x for x in ret_params if frame.is_multi(x)]
        if len(multis) > 1:
            all_keys.extend(multis)

        if len(unkeyed):
            ident = Var()
            flow.append(build.call(Builtins.make_identity, [Var(value=all_keys + unkeyed), ident]))
            all_keys.append(ident)

        for key in all_keys:
            self.demand(key, is_return=True)

        is_export = action.entity.isa(Builtins.ExportReturn)

        for (ix, ret) in enumerate(ret_params):
            flow.branch()
            self.demand(ret)
            col = Var(Builtins.Symbol, value=f"col{ix:03}")
            rel = dsl.rel.output.cols._rel
            if is_export:
                rel = dsl.rel.Export_Relation._rel
                uuid_str = dsl.rel.uuid_string._rel
                v = Var()
                flow.append(build.relation_action(ActionType.Call, dsl.rel.pyrel_default._rel, [uuid_str, ret, ret, v]))
                flow.append(build.relation_action(ActionType.Bind, rel, [col, *all_keys, v]))
            else:
                rel = dsl.rel.output.cols._rel
                flow.append(build.relation_action(ActionType.Bind, rel, [col, *all_keys, ret]))
            flow.join()

        return self.flow.continue_()

    #--------------------------------------------------
    # Union
    #--------------------------------------------------

    def union_call(self, call:Action):
        flow = self.flow

        # run through the subtasks and add them to the flow
        union_task = cast(Task, call.entity.value)
        union_task.parents.append(Builtins.InlineAnnotation)

        # find any vars that this union task depends on
        inner_vars = gather_task_vars(union_task)
        deps = list(flow.available_vars() & inner_vars)

        for item in union_task.items:
            neue = self.query_flow(cast(Task, item.entity.value), raw_return=True)
            rets = [i for i in neue.items if i.entity.isa(Builtins.Return)]
            if len(rets):
                rets[0].entity.value = union_task
                rets[0].action = ActionType.Bind
                if deps:
                    prepend_bindings(deps, rets[0])

        flow.continue_()
        # Get the result of the union
        get = build.relation_action(ActionType.Get, cast(Task, call.entity.value), deps + call.params_list())
        flow.append(get)

    #--------------------------------------------------
    # Ordered choice
    #--------------------------------------------------

    def ordered_choice_call(self, call:Action):
        flow = self.flow
        choice = cast(Task, call.entity.value)
        prevs = []
        branches = []

        # find any vars that this choice task depends on
        inner_vars = gather_task_vars(choice)
        deps = list(flow.available_vars() & inner_vars)

        for item in choice.items:
            cur_task = cast(Task, item.entity.value)

            # Negate all the previous branches to ensure we only return a value if
            # we're at our position in the order
            for prev in reversed(prevs):
                fetch = build.relation_action(ActionType.Get, prev, deps)
                prev_task = Task(items=[fetch])
                cur_task.items.insert(0, build.call(Builtins.Not, [Var(value=[]), Var(value=prev_task)]))

            neue:Task = self.query_flow(cur_task, raw_return=True)
            branches.append(neue)

            # find the return statement and turn it into a bind for the overall orderd_choice
            rets = [i for i in neue.items if i.entity.isa(Builtins.Return)]
            ret_bindings = [*deps]
            if len(rets):
                rets[0].entity.value = choice
                prepend_bindings(deps, rets[0])
            else:
                rets.append(build.relation_action(ActionType.Bind, choice, ret_bindings))
                neue.items.append(rets[0])

            # add a bind for this particular task so that we can negate it in subsequent
            # branches to create the ordering
            bind = build.relation_action(ActionType.Bind, neue, deps)
            neue.items.append(bind)

            prevs.append(neue)

        flow.continue_()
        # Get the result of the choice
        get = build.relation_action(ActionType.Get, choice, deps + call.params_list())
        flow.append(get)

    #--------------------------------------------------
    # Quantifiers
    #--------------------------------------------------

    def quantifier_call(self, call:Action):
        flow = self.flow
        quantifier = cast(Task, call.entity.value)
        group, task_var = [*call.bindings.values()]
        sub_task = self.query_flow(cast(Task, task_var.value), always_demand=True, ignore_deps=True)
        sub_task.parents.append(Builtins.InlineAnnotation)

        if isinstance(group.value, list) and len(group.value):
            raise Exception("TODO: grouped quantifiers")

        # Find any vars that this quantified task depends on
        sub_vars = gather_task_vars(sub_task)
        parent_vars = flow.available_vars()

        shared = sub_vars & parent_vars
        # bind those so we can use them in the quantified task
        sub_task.items.append(build.relation_action(ActionType.Bind, sub_task, shared))

        # create the quantified task, which just gets the subtask
        quantifed_task = Task()
        quantifed_task.items.append(build.relation_action(ActionType.Get, sub_task, shared))

        # add the call to the quantifier
        flow.continue_()
        for parent_var in parent_vars:
            self.demand(parent_var)
        flow.append(build.call(quantifier, [group, Var(value=quantifed_task)]))

    #--------------------------------------------------
    # Aggregates
    #--------------------------------------------------

    def aggregate_call(self, call:Action):
        flow = self.flow
        agg = cast(Task, call.entity.value)
        is_extender = agg.isa(Builtins.Extender)
        (args, group, pre_args, ret) = call.params_list()
        group_vars = cast(List[Var], group.value)
        arg_vars = cast(List[Var], args.value)
        pre_arg_vars = cast(List[Var], pre_args.value)

        for demand in arg_vars + group_vars:
            self.demand(demand)

        # to prevent shadowing errors we need to map the inner vars to new vars
        mapped = [Var(name=var.name, type=var.type, value=var.value) for var in arg_vars]
        var_mapping = dict(zip(arg_vars, mapped))

        # create the inner relation we'll aggregate over
        flow.branch(inline=True, var_mapping=var_mapping)

        # vars that are in both the projection and grouping needed to be mapped in
        # the projection but made equivalent in the body so the grouping takes effect
        equivs = [(orig, neue) for (orig, neue) in var_mapping.items() if orig in group_vars]
        for (orig, neue) in equivs:
            flow.append(build.relation_action(ActionType.Call, Builtins.eq, [orig, neue]))
        # bind the mapped vars as the output of the inner relation
        for demand in arg_vars:
            self.demand(demand)
        flow.append(build.relation_action(ActionType.Bind, flow.frame().task, mapped))
        inner = flow.join()

        # create the outer aggregate
        flow.branch(ignore_deps=True)
        outer_bindings = [ret] if not is_extender else [ret, *arg_vars]
        outer_call = build.relation_action(ActionType.Call, agg, [*pre_arg_vars, Var(value=inner), *outer_bindings])
        flow.append(outer_call)

        out_params = [*group_vars, ret] if not is_extender else [ret, *group_vars, *arg_vars]
        flow.append(build.relation_action(ActionType.Bind, flow.frame().task, out_params))
        outer = flow.join()
        outer.parents.append(Builtins.InlineAnnotation)

        # Resume the flow
        flow.continue_()
        get = build.relation_action(ActionType.Get, outer, out_params)
        flow.append(get)


#--------------------------------------------------
# Shredder
#--------------------------------------------------

class Shredder(c.Pass):
    def query(self, query: Task, parent=None):
        neue_actions = []
        for item in query.items:
            if item.action not in [ActionType.Call, ActionType.Construct] and not item.entity.isa(Builtins.Relation):
                ident, action = item.entity, item.action
                for type in item.types:
                    neue_actions.append(build.relation_action(action, type, [ident]))
                for prop, value in item.bindings.items():
                    neue_actions.append(build.relation_action(action, prop, [ident, value]))
            else:
                walked = self.walk(item)
                neue_actions.append(walked)
        query.items = neue_actions

#--------------------------------------------------
# Splinter
#--------------------------------------------------

class Splinter(c.Pass):

    def query(self, query: Task, parent=None):
        effects = [i for i in query.items if i.action.is_effect()]

        grouped_effects = defaultdict(list)
        for item in effects:
            grouped_effects[(item.action, item.entity.value)].append(item)

        if len(grouped_effects) > 1:
            neue_items = []

            non_effects = [i for i in query.items if not i.action.is_effect()]
            effects_vars = gather_vars(effects)

            fetch = None
            if len(non_effects):
                fetch = self.create_fetch(non_effects, effects_vars)
                neue_items.append(fetch)

            for (k, b) in grouped_effects.items():
                neue_items.append(self.create_effect_query(b, effects_vars, fetch.entity.value if fetch else None))

            query.behavior = Behavior.Sequence
            query.items = neue_items

    #--------------------------------------------------
    # Subtask creation
    #--------------------------------------------------

    def create_fetch(self, non_effects: List[Action], effects_vars: Iterable[Var]):
        fetch = Task()
        fetch.parents.append(Builtins.InlineAnnotation)
        non_effects.append(build.relation_action(ActionType.Bind, fetch, effects_vars))
        fetch.items = non_effects
        return build.call(fetch, [])

    def create_effect_query(self, effects: List[Action], effects_vars: Iterable[Var], fetch: Any):
        neue = Task()
        if fetch:
            effects.insert(0, build.relation_action(ActionType.Get, fetch, effects_vars))
        neue.items = effects
        return build.call(neue, [])

#--------------------------------------------------
# SetCollector
#--------------------------------------------------

set_types = [ActionType.Bind, ActionType.Persist, ActionType.Unpersist]

class SetCollector(c.Pass):
    def query(self, query: Task, parent=None):
        binds = [i for i in query.items if i.action in set_types]
        if len(binds) > 1:
            neue_items = []
            for item in query.items:
                if item.action not in set_types:
                    neue_items.append(item)
            neue_items.extend(self.create_raw(binds))
            query.items = neue_items

    def create_raw(self, binds: List[Action]):
        vals = [Var(value=[]) for i in range(len(binds[0].bindings))]
        vars = [Var() for v in vals]

        for bind in binds:
            for ix, var in enumerate(bind.bindings.values()):
                cast(List[Var], vals[ix].value).append(var)

        return [
            build.relation_action(ActionType.Get, Builtins.RawData, vals + vars),
            build.relation_action(binds[0].action, cast(Type, binds[0].entity.value), vars)
        ]

#--------------------------------------------------
# Compiler
#--------------------------------------------------

class Clone(c.Pass):
    pass

class Compiler(c.Compiler):
    def __init__(self, config:config.Config):
        super().__init__(Emitter(config), [
            Clone(),
            Shredder(),
            Dataflow(),
            Splinter(),
            SetCollector(),
        ])
