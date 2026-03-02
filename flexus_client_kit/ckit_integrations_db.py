from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from flexus_client_kit import ckit_cloudtool


@dataclass
class IntegrationRecord:
    integr_name: str
    integr_tools: list[ckit_cloudtool.CloudTool]
    integr_init: Callable[..., Awaitable[Any]]
    integr_setup_handlers: Callable
    integr_provider: str = ""
    integr_scopes: list[str] = field(default_factory=list)


def static_integrations_load(bot_dir: Path, allowlist: list[str], builtin_skills: list[str]) -> list[IntegrationRecord]:
    # static means designed to save into constant on top level of a bot file
    # logger is not yet initilized here, no logs possible
    result = []
    for name in allowlist:
        if name == "skills":
            if len(builtin_skills) > 0:
                from flexus_client_kit import ckit_skills
                async def _init_skills(rcx, setup):
                    return None
                result.append(IntegrationRecord(
                    integr_name=name,
                    integr_tools=[ckit_skills.FETCH_SKILL_TOOL],
                    integr_init=_init_skills,
                    integr_setup_handlers=lambda obj, rcx, _d=bot_dir, _s=builtin_skills: [
                        rcx.on_tool_call("flexus_fetch_skill")(lambda tc, args: ckit_skills.called_by_model(tc, args, _d, _s))
                    ],
                ))

        elif name == "flexus_policy_document":
            from flexus_client_kit.integrations import fi_pdoc
            async def _init_pdoc(rcx, setup):
                return fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_pdoc.POLICY_DOCUMENT_TOOL],
                integr_init=_init_pdoc,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("flexus_policy_document")(obj.called_by_model)],
            ))

        elif name == "print_widget":
            from flexus_client_kit.integrations import fi_widget
            async def _init_widget(rcx, setup):
                return None
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_widget.PRINT_WIDGET_TOOL],
                integr_init=_init_widget,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("print_widget")(fi_widget.handle_print_widget)],
            ))

        elif name == "gmail":
            from flexus_client_kit.integrations import fi_gmail
            async def _init_gmail(rcx, setup):
                return fi_gmail.IntegrationGmail(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_gmail.GMAIL_TOOL],
                integr_init=_init_gmail,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("gmail")(obj.called_by_model)],
                integr_provider="google",
                integr_scopes=fi_gmail.GMAIL_SCOPES,
            ))

        elif name == "google_calendar":
            from flexus_client_kit.integrations import fi_google_calendar
            async def _init_gcal(rcx, setup):
                return fi_google_calendar.IntegrationGoogleCalendar(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_google_calendar.GOOGLE_CALENDAR_TOOL],
                integr_init=_init_gcal,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("google_calendar")(obj.called_by_model)],
                integr_provider="google",
                integr_scopes=fi_google_calendar.REQUIRED_SCOPES,
            ))

        elif name == "jira":
            from flexus_client_kit.integrations import fi_jira
            async def _init_jira(rcx, setup):
                url = (setup or {}).get("jira_instance_url", "")
                return fi_jira.IntegrationJira(rcx.fclient, rcx, jira_instance_url=url)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_jira.JIRA_TOOL],
                integr_init=_init_jira,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("jira")(obj.called_by_model)],
                integr_provider="atlassian",
                integr_scopes=fi_jira.REQUIRED_SCOPES,
            ))

        elif name.startswith("facebook"):   # "facebook[account, adset]"
            # In manifest.json, it's not possible to write [] brackets (according to the json schema), but in a
            # bot defined by code, you can
            from flexus_client_kit.integrations import fi_facebook2
            fb_bunch = fi_facebook2.make_facebook_bunch(_parse_bracket_list(name))
            fb_tool = fb_bunch.make_tool()
            async def _init_facebook(rcx, setup, _bunch=fb_bunch):
                return fi_facebook2.IntegrationFacebook2(rcx.fclient, rcx, _bunch)
            result.append(IntegrationRecord(
                integr_name="facebook",
                integr_tools=[fb_tool],
                integr_init=_init_facebook,
                integr_setup_handlers=lambda obj, rcx, _t=fb_tool: [rcx.on_tool_call(_t.name)(obj.called_by_model)],
                integr_provider="facebook",
            ))

        else:
            raise ValueError(f"Unknown integration {name!r}")
    return result


def _parse_bracket_list(name: str) -> list[str] | None:
    if "[" not in name:
        return None
    return [g.strip() for g in name.split("[", 1)[1].rstrip("]").split(",")]


async def main_loop_integrations_init(records: list[IntegrationRecord], rcx, setup: dict = None) -> dict[str, Any]:
    result = {}
    for rec in records:
        obj = await rec.integr_init(rcx, setup)
        rec.integr_setup_handlers(obj, rcx)
        result[rec.integr_name] = obj
    return result
