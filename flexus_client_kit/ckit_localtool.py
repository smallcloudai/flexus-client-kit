import time
import asyncio
import json
import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_origin, get_args, Union, List, Dict

import gql

from flexus_client_kit import ckit_expert, ckit_client
from flexus_client_kit import ckit_ask_model


def a_very_complex_tool(*, hello: str, x: int, y: int =13) -> str:
    """
    A sample function that demonstrates how easy it is to write a python function callable by a model.

    :param hello: A greeting string to use
    :param x: First number to add
    :param y: Second number to add
    """
    print("a_very_complex_tool received: hello = %r, x = %d, y = %d" % (hello, x, y))
    return "%s world, x+y equals %d" % (hello, x + y)

@dataclass
class FThreadMessageOutput:
    ftm_belongs_to_ft_id: str
    ftm_role: str
    ftm_num: int
    ftm_alt: int
    ftm_tool_calls: Any


async def call_local_functions_and_upload_results(
    fclient: ckit_client.FlexusClient,
    response: FThreadMessageOutput,
    local_functions: List[Callable]
):
    if not response.ftm_tool_calls:
        return
    assert response.ftm_role == "assistant"
    function_map = {func.__name__: func for func in local_functions}
    tool_results = []
    for i, call in enumerate(response.ftm_tool_calls):
        call_id = call["id"]
        function_name = call["function"]["name"]   # let it crash if that doesn't hold
        if function_name not in function_map:  # other service will process it
            continue
        func = function_map[function_name]
        try:
            function_args = call["function"]["arguments"]
            if isinstance(function_args, str):
                args = json.loads(function_args)
            else:
                args = function_args
            result = func(**args)
            assert isinstance(result, str)

        except Exception as e:
            result = "Error: %s\n%s" % (type(e).__name__, str(e))

        tool_results.append({
            "ftm_belongs_to_ft_id": response.ftm_belongs_to_ft_id,
            "ftm_alt": response.ftm_alt,
            "ftm_num": response.ftm_num + 2 + i,   # kernel in between assistant and tool
            "ftm_prev_alt": response.ftm_alt,
            "ftm_role": "tool",
            "ftm_content": json.dumps(result),
            "ftm_call_id": call_id,
            "ftm_provenance": json.dumps({
                "system_type": fclient.service_name,
                "function_name": function_name,
                "function_file": inspect.getfile(func),
                "function_module": func.__module__,
            }),
        })

    if tool_results:
        http_client = await fclient.use_http()
        async with http_client as h:
            r = await h.execute(
                gql.gql("""mutation ckitUploadToolResults($input: FThreadMultipleMessagesInput!) {
                    thread_messages_create_multiple(input: $input)
                }"""),
                variable_values={
                    "input": {
                        "ftm_belongs_to_ft_id": response.ftm_belongs_to_ft_id,
                        "messages": tool_results,
                    }
                },
            )
            created_cnt = r["thread_messages_create_multiple"]
            assert created_cnt == len(tool_results)


def _openai_style_parameter_description(f: Callable):
    """
    Build an OpenAI-function JSON-schema from type-annotated Python callables.
    Only first-level (non-nested) annotations are processed.
    Supports parameter descriptions from docstrings.
    """
    _type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    def _schema_from_annotation(tp) -> dict:
        origin = get_origin(tp)
        args = get_args(tp)

        # Optional[T] == Union[T, NoneType]
        if origin is Union and type(None) in args:
            non_none = next(a for a in args if a is not type(None))
            schema = _schema_from_annotation(non_none)
            schema["nullable"] = True
            return schema

        # List[T], Dict[K, V], etc.
        if origin in (list, List):
            item_schema = _schema_from_annotation(args[0] if args else Any)
            return {"type": "array", "items": item_schema}
        if origin in (dict, Dict):
            return {"type": "object"}

        # Primitives
        assert tp in _type_map, f"Unsupported type: {tp}"
        json_type = _type_map[tp]
        return {"type": json_type}

    sig = inspect.signature(f)
    properties = {}
    required = []

    param_descriptions = {}
    if f.__doc__:
        lines = f.__doc__.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(':param '):
                # Format: :param param_name: description
                parts = line[7:].split(':', 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    description = parts[1].strip()
                    param_descriptions[param_name] = description

    for name, param in sig.parameters.items():
        assert param.kind is param.VAR_KEYWORD or param.kind is param.KEYWORD_ONLY, "Only keyword parameters are supported"
        assert param.annotation is not inspect._empty, f"Parameter '{name}' lacks a type annotation"
        schema = _schema_from_annotation(param.annotation)

        assert name in param_descriptions, f"Parameter '{name}' has no docstring"
        schema["description"] = param_descriptions[name]

        properties[name] = schema
        if param.default is inspect._empty:
            required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def openai_style_function_description(f: Callable):
    """
    Build a complete OpenAI tool specification from type-annotated Python callables.
    """
    function_description = ""

    if f.__doc__:
        lines = f.__doc__.strip().split('\n')
        description_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith(':param '):
                break  # Stop at first parameter line
            elif line and not line.startswith(':'):
                description_lines.append(line)

        function_description = ' '.join(description_lines).strip()

    parameters_schema = _openai_style_parameter_description(f)

    return {
        "type": "function",
        "function": {
            "name": f.__name__,
            "description": function_description,
            "parameters": parameters_schema
        }
    }


async def test(super: bool):
    inside_fgroup_id = "solar_root"
    system_prompt = "Flexus client kit local call test. Let's call some tools!"
    if not super:
        fclient = ckit_client.FlexusClient("ckit_test", api_key="sk_alice_123456")
        fexp_id = await ckit_expert.make_sure_have_expert(
            fclient,
            system_prompt,
            "",
            "alice@example.com",
            inside_fgroup_id,
            "ckit_test",
        )
    else:
        fclient = ckit_client.FlexusClient("ckit_test", endpoint="/v1/jailed-bot")
        # this will create a global expert
        fexp_id = await ckit_expert.make_sure_have_expert(
            fclient,
            system_prompt,
            "",
            None,
            None,
            "ckit_test",
        )
    print("fexp_id", fexp_id)

    # consequences = await ckit_expert.expert_choice_consequences(fclient, fexp_id, inside_fgroup_id)
    # # XXX mix cloud tools and local tools
    # print("To start thread in %r using expert %r, there are %d cloudtools online, after adding local functions have:" % (inside_fgroup_id, fexp_id, len(consequences.cloudtools)))
    # for c in consequences.cloudtools:
    #     print("  %s" % c.ctool_name)
    #     print("    %s" % c.ctool_description)
    #     print("    %s" % c.ctool_parameters)
    #     print(json.dumps(c.ctool_parameters, indent=2))

    local_functions = [
        a_very_complex_tool,
    ]

    toolset = [openai_style_function_description(x) for x in local_functions]
    # for t in toolset:
    #     print(json.dumps(t, indent=2))

    YYYmmdd_HHMMSS = time.strftime("%Y%m%d %H:%M:%S")
    assistant_says = await ckit_ask_model.ask_model(
        fclient,
        inside_fgroup_id=inside_fgroup_id,
        fexp_id=fexp_id,
        title="Test %s" % YYYmmdd_HHMMSS,
        model="o4-mini",
        who_is_asking="ckit",
        question="Yo dawg, call a_very_complex_tool()",
        toolset=toolset,
    )
    await call_local_functions_and_upload_results(fclient, assistant_says, local_functions)


if __name__ == "__main__":
    asyncio.run(test(False))
