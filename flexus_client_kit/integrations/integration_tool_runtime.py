import importlib
import json
import os
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget


def _known_providers() -> list[str]:
    # Enumerate fi_*.py files in this package — single source of truth now that registry is gone.
    try:
        d = os.path.dirname(__file__)
        return sorted(
            fn[3:-3] for fn in os.listdir(d)
            if fn.startswith("fi_") and fn.endswith(".py")
        )
    except (OSError, ValueError) as e:
        raise RuntimeError(f"Cannot list providers: {e}") from e


def _provider_methods(provider: str) -> list[str]:
    # Load METHOD_IDS directly from fi_{provider}.py — avoids a separate registry file.
    try:
        mod = importlib.import_module(f"flexus_client_kit.integrations.fi_{provider}")
        return list(getattr(mod, "METHOD_IDS", []))
    except ModuleNotFoundError as e:
        raise RuntimeError(f"Unknown provider: {provider}") from e


def _parse_allow_tools(raw: str) -> list[str]:
    try:
        out: list[str] = []
        for item in raw.split(","):
            name = item.strip()
            if name and name not in out:
                out.append(name)
        return out
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot parse allow tools: {e}") from e


def derive_tool_names(prompts_module: Any) -> list[str]:
    try:
        out = [fi_pdoc.POLICY_DOCUMENT_TOOL.name, fi_widget.PRINT_WIDGET_TOOL.name]
        for expert in prompts_module.BOT_EXPERTS:
            for name in _parse_allow_tools(str(expert.get("fexp_allow_tools", ""))):
                if name not in out:
                    out.append(name)
        return out
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot derive tool names: {e}") from e


def _mk_generic_tool(tool_name: str) -> ckit_cloudtool.CloudTool:
    try:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=tool_name,
            description=f"{tool_name}: provider router. Start with op=\"help\".",
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string"},
                    "args": {"type": "object"},
                },
            },
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build generic tool {tool_name}: {e}") from e


def build_tools_from_prompts(prompts_module: Any) -> list[ckit_cloudtool.CloudTool]:
    try:
        out: list[ckit_cloudtool.CloudTool] = []
        for tool_name in derive_tool_names(prompts_module):
            if tool_name == fi_pdoc.POLICY_DOCUMENT_TOOL.name:
                out.append(fi_pdoc.POLICY_DOCUMENT_TOOL)
                continue
            if tool_name == fi_widget.PRINT_WIDGET_TOOL.name:
                out.append(fi_widget.PRINT_WIDGET_TOOL)
                continue
            out.append(_mk_generic_tool(tool_name))
        return out
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build tool objects from prompts: {e}") from e


def _help_text(tool_name: str) -> str:
    try:
        return (
            f"{tool_name}(op=\"help\")\n"
            f"{tool_name}(op=\"status\")\n"
            f"{tool_name}(op=\"list_providers\")\n"
            f"{tool_name}(op=\"list_methods\", args={{\"provider\": \"<provider>\"}})\n"
            f"{tool_name}(op=\"call\", args={{\"method_id\": \"<provider>.<resource>.<action>.v1\", ...}})\n\n"
            "For non-discovery ops, args.method_id is required."
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build help text for {tool_name}: {e}") from e


async def _handle_generated_tool(
    tool_name: str,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    try:
        if not model_produced_args:
            return _help_text(tool_name)

        op = str(model_produced_args.get("op", "help"))
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if op == "help":
            return _help_text(tool_name)

        known = _known_providers()

        if op == "status":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "status": "registered",
                "provider_count": len(known),
            }, indent=2, ensure_ascii=False)

        if op == "list_providers":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "providers": known,
            }, indent=2, ensure_ascii=False)

        if op == "list_methods":
            provider = str(args.get("provider", "")).strip()
            if not provider:
                return "Error: args.provider is required for op=list_methods."
            if provider not in known:
                return "Error: unknown provider."
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "provider": provider,
                "method_ids": _provider_methods(provider),
            }, indent=2, ensure_ascii=False)

        method_id = str(args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id is required."
        if "." not in method_id:
            return "Error: invalid method_id format."

        provider = method_id.split(".", 1)[0]
        if provider not in known:
            return "Error: unknown provider."

        try:
            mod = importlib.import_module(f"flexus_client_kit.integrations.fi_{provider}")
        except ModuleNotFoundError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        class_name = "Integration" + "".join(w.capitalize() for w in provider.split("_"))
        integration_class = getattr(mod, class_name, None)
        if integration_class is None:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        try:
            integration = integration_class()
        except TypeError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        return await integration.called_by_model(toolcall, model_produced_args)
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        return f"Error in {tool_name}: {type(e).__name__}: {e}"


def generated_handler(tool_name: str):
    async def _handler(
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        try:
            return await _handle_generated_tool(tool_name, toolcall, model_produced_args)
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            return f"Error in {tool_name} handler: {type(e).__name__}: {e}"

    return _handler


def register_tool_handlers(rcx: ckit_bot_exec.RobotContext, tool_names: list[str]) -> None:
    try:
        pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

        @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
        async def _toolcall_pdoc(
            toolcall: ckit_cloudtool.FCloudtoolCall,
            model_produced_args: Dict[str, Any],
        ) -> str:
            try:
                return await pdoc_integration.called_by_model(toolcall, model_produced_args)
            except (AttributeError, KeyError, TypeError, ValueError) as e:
                return f"Error in flexus_policy_document: {type(e).__name__}: {e}"

        @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
        async def _toolcall_widget(
            toolcall: ckit_cloudtool.FCloudtoolCall,
            model_produced_args: Dict[str, Any],
        ) -> str:
            try:
                return await fi_widget.handle_print_widget(toolcall, model_produced_args)
            except (AttributeError, KeyError, TypeError, ValueError) as e:
                return f"Error in print_widget: {type(e).__name__}: {e}"

        for tool_name in tool_names:
            if tool_name in (fi_pdoc.POLICY_DOCUMENT_TOOL.name, fi_widget.PRINT_WIDGET_TOOL.name):
                continue
            rcx.on_tool_call(tool_name)(generated_handler(tool_name))
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot register tool handlers: {e}") from e


async def run_event_loop(rcx: ckit_bot_exec.RobotContext) -> None:
    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        pass
