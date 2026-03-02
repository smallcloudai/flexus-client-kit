import inspect
import json
import logging
import types
from typing import Any, Callable, Dict, List, Literal, Optional, get_args, get_origin, get_type_hints

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("bunch")


class OpError(Exception):
    pass


def _type_to_schema(annotation) -> dict:
    if annotation is inspect.Parameter.empty or annotation is Any:
        return {"type": "string"}
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Literal:
        values = list(args)
        if all(isinstance(v, str) for v in values):
            return {"type": "string", "enum": values}
        if all(isinstance(v, int) for v in values):
            return {"type": "integer", "enum": values}
        return {"enum": values}
    if origin is type(None):
        return {"type": "string"}
    if _is_optional(annotation):
        inner = [a for a in args if a is not type(None)][0]
        return _type_to_schema(inner)
    if origin is list:
        return {"type": "array", "items": _type_to_schema(args[0] if args else Any)}
    if origin is dict:
        return {"type": "object", "additionalProperties": _type_to_schema(args[1] if len(args) > 1 else Any)}
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    raise TypeError(f"unsupported type annotation: {annotation}")


def _is_optional(annotation) -> bool:
    origin = get_origin(annotation)
    if origin is type(None):
        return False
    if origin is getattr(types, "UnionType", None) or str(origin) == "typing.Union":
        return type(None) in get_args(annotation)
    return False


def _func_schema(func: Callable, skip_first: type = None) -> dict:
    extra_ns = {skip_first.__name__: skip_first} if skip_first is not None else {}
    hints = get_type_hints(func, localns=extra_ns, include_extras=True)
    sig = inspect.signature(func)
    properties = {}
    required = []
    params = list(sig.parameters.items())
    if skip_first is not None:
        assert len(params) >= 1, f"{func.__name__}: need at least one parameter for context"
        first_name = params[0][0]
        first_ann = hints.get(first_name, inspect.Parameter.empty)
        assert first_ann is skip_first or (isinstance(first_ann, type) and issubclass(first_ann, skip_first)), \
            f"{func.__name__}: first param '{first_name}' hinted as {first_ann}, expected {skip_first}"
        params = params[1:]
    for name, param in params:
        if name == "self":
            continue
        ann = hints.get(name, inspect.Parameter.empty)
        schema = _type_to_schema(ann)
        if param.default is not inspect.Parameter.empty and param.default is not None:
            schema["default"] = param.default
        properties[name] = schema
        if param.default is inspect.Parameter.empty and not _is_optional(ann):
            required.append(name)
    doc = inspect.getdoc(func) or ""
    first_line = doc.split("\n")[0].strip() if doc else func.__name__
    return {"description": first_line, "properties": properties, "required": required}


class BunchOfPythonFunctions:
    def __init__(self, tool_name: str, tool_description: str, ContextType: type = None):
        """
        ContextType -- if set, every function must have it as the first parameter, like FacebookAdsClient.
        """
        self.tool_name = tool_name
        self.tool_description = tool_description
        self._ContextType = ContextType
        self._schemas: Dict[str, dict] = {}
        self._funcs: Dict[str, Callable] = {}

    def add(self, group_name: str, funcs: List[Callable]):
        for func in funcs:
            name = f"{group_name}{func.__name__}"
            self._schemas[name] = _func_schema(func, skip_first=self._ContextType)
            self._funcs[name] = func

    def make_tool(self) -> ckit_cloudtool.CloudTool:
        methods = sorted(self._funcs.keys())
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=self.tool_name,
            description=self.tool_description + " Call with op=\"list\" to see available methods.",
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["list", "help", "call"]},
                    "method": {"type": "string", "description": "Start with op=\"list\" to know possible methods"},
                    "args": {"type": "object"},
                },
                "required": ["op"],
            },
        )

    def _list_functions(self) -> str:
        lines = []
        for name in sorted(self._funcs.keys()):
            lines.append(f"{name} — {self._schemas[name]['description']}")
        lines.append(f"\nUse {self.tool_name}(op=\"help\", method=\"<name>\") to get the exact schema for the arguments.")
        return "\n".join(lines)

    def _method_help(self, method: str) -> str:
        s = self._schemas.get(method)
        if not s:
            return f"Unknown method '{method}'. Use op=\"list\" to see available methods."
        schema = {"type": "object", "properties": s["properties"], "required": s["required"]}
        return s["description"] + "\n\n" + json.dumps(schema, indent=2)

    async def called_by_model(
        self,
        cx,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if self._ContextType is not None:
            assert isinstance(cx, self._ContextType), \
                f"cx must be {self._ContextType.__name__}, got {type(cx).__name__}"
        if not model_produced_args:
            return self._list_functions()
        op = (model_produced_args.get("op") or "").lower()
        method = model_produced_args.get("method") or ""
        if not op or op == "list":
            return self._list_functions()
        if op == "help":
            if not method:
                return "ERROR: method is required for op=\"help\""
            return self._method_help(method)
        if op != "call":
            return f"Unknown op '{op}'. Use: list, help, call."

        # op == "call"
        if not method:
            return "ERROR: method is required for op=\"call\""
        func = self._funcs.get(method)
        if not func:
            return f"Unknown method '{method}'. Use op=\"list\"."

        # model sometimes puts keys at top level instead of inside args
        args = model_produced_args.get("args") or {}
        if isinstance(model_produced_args, dict):
            for k in model_produced_args:
                if k not in ("op", "method", "args") and k not in args:
                    args[k] = model_produced_args[k]
        # model might escape args as json
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except (json.JSONDecodeError, TypeError):
                return "ERROR: args must be an object, got unparseable string"

        # check required parameters exist only top level checked
        schema = self._schemas[method]
        missing = [r for r in schema["required"] if r not in args]
        if missing:
            return f"ERROR: method {method!r} missing required args: {', '.join(missing)}"
        kwargs = {k: v for k, v in args.items() if k in schema["properties"]}
        try:
            if self._ContextType is not None:
                maybe_result = func(cx, **kwargs)
            else:
                maybe_result = func(**kwargs)
            if inspect.isawaitable(maybe_result):
                result = await maybe_result
            else:
                result = maybe_result
            return result
        except OpError as e:
            return f"ERROR: {e}"
        except Exception as e:
            logger.warning("method %s failed: %s", method, e, exc_info=e)
            return f"ERROR: {e}"


if __name__ == "__main__":
    import asyncio

    def add(a: int, b: int) -> str:
        """Add two numbers."""
        return f"{a + b}"

    async def mul(a: int, b: int, verbose: Optional[bool] = None) -> str:
        """Multiply two numbers."""
        return f"{a} * {b} = {a * b}" if verbose else f"{a * b}"

    gi = BunchOfPythonFunctions("super_calc", "Super Duper Calculator")
    gi.add("math.", [add, mul])

    print("=== list ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "list"})))
    print("\n=== help ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "help", "method": "math.mul"})))
    print("\n=== call ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.mul", "args": {"a": 3, "b": 4}})))
    print("\n=== call ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "args": {"a": 3, "b": 4}})))
    print("\n=== recovery1 ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "args": "{\"a\": 3, \"b\": 4}"})))
    print("\n=== recovery2 ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "a": 3, "b": 4})))
    print("\n=== problem1 ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "args": {"a": 3, "hooot": 4}})))
    print("\n=== problem2 ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "args": [4, 5]})))
    print("\n=== problem3 ===")
    print(asyncio.run(gi.called_by_model(None, None, {"op": "call", "method": "math.add", "args": "not a json"})))
