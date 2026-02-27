from flexus_client_kit import ckit_cloudtool


INTEGRATION_REGISTRY: dict[str, dict] = {}


def register(
    name,
    provider,
    scopes,
    tools: list[ckit_cloudtool.CloudTool],
    tool_handler_factory,
):
    INTEGRATION_REGISTRY[name] = {
        "provider": provider,
        "scopes": scopes,
        "tools": tools,
        "tool_handler_factory": tool_handler_factory,
    }
