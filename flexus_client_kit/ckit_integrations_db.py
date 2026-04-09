import importlib
import inspect
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_cloudtool, ckit_scenario

GOOGLE_OAUTH_BASE_SCOPES = ["openid", "email", "profile"]


def _should_fake_in_scenario(integr_name: str, integr_provider: str = "") -> bool:
    return bool(integr_provider) or integr_name in {"erp", "crm"}


def _register_tool_handler(
    rcx,
    tool_name: str,
    handler,
    fake_in_scenario: bool = False,
):
    async def _wrapped(toolcall, *args, **kwargs):
        if fake_in_scenario and rcx.running_test_scenario:
            source = Path(p).read_text() if (p := inspect.getsourcefile(handler)) else ""
            return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, source)
        return await handler(toolcall, *args, **kwargs)
    return rcx.on_tool_call(tool_name)(_wrapped)


@dataclass
class IntegrationRecord:
    integr_name: str
    integr_tools: list[ckit_cloudtool.CloudTool]
    integr_init: Callable[..., Awaitable[Any]]
    integr_setup_handlers: Callable
    integr_provider: str = ""
    integr_scopes: list[str] = field(default_factory=list)
    integr_prompt: str = ""
    integr_is_messenger: bool = False
    integr_need_mongo: bool = False


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
                integr_prompt=fi_pdoc.POLICY_DOCUMENT_PROMPT,
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
                integr_prompt=fi_widget.PRINT_WIDGET_PROMPT,
            ))

        elif name == "gmail":
            from flexus_client_kit.integrations import fi_gmail
            async def _init_gmail(rcx, setup):
                return fi_gmail.IntegrationGmail(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_gmail.GMAIL_TOOL],
                integr_init=_init_gmail,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "gmail", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="gmail",
                integr_scopes=fi_gmail.GMAIL_SCOPES,
                integr_prompt=fi_gmail.GMAIL_PROMPT,
            ))

        elif name == "google_calendar":
            from flexus_client_kit.integrations import fi_google_calendar
            async def _init_gcal(rcx, setup):
                return fi_google_calendar.IntegrationGoogleCalendar(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_google_calendar.GOOGLE_CALENDAR_TOOL],
                integr_init=_init_gcal,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "google_calendar", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="google_calendar",
                integr_scopes=fi_google_calendar.REQUIRED_SCOPES,
                integr_prompt="",
            ))

        elif name == "google_business":
            from flexus_client_kit.integrations import fi_google_business
            async def _init_gb(rcx, setup):
                return fi_google_business.IntegrationGoogleBusiness(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_google_business.GOOGLE_BUSINESS_TOOL],
                integr_init=_init_gb,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "google_business", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="google_business",
                integr_scopes=fi_google_business.GOOGLE_BUSINESS_SCOPES,
                integr_prompt=fi_google_business.GOOGLE_BUSINESS_PROMPT,
            ))

        elif name == "google_ads":
            from flexus_client_kit.integrations import fi_google_ads
            async def _init_gads(rcx, setup):
                auth = rcx.external_auth.get("google_ads") or {}
                cf = auth.get("connect_fields") or {}
                return fi_google_ads.IntegrationGoogleAds(
                    rcx.fclient, rcx,
                    developer_token=cf.get("developer_token", ""),
                    customer_id=cf.get("customer_id", ""),
                    login_customer_id=cf.get("login_customer_id", ""),
                )
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_google_ads.GOOGLE_ADS_TOOL],
                integr_init=_init_gads,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "google_ads", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="google_ads",
                integr_scopes=fi_google_ads.GOOGLE_ADS_SCOPES,
            ))

        elif name == "google_sheets":
            from flexus_client_kit.integrations import fi_google_sheets
            async def _init_gsheets(rcx, setup):
                return fi_google_sheets.IntegrationGoogleSheets(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_google_sheets.GOOGLE_SHEETS_TOOL],
                integr_init=_init_gsheets,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "google_sheets", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="google",
                integr_scopes=fi_google_sheets.REQUIRED_SCOPES,
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
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "jira", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="atlassian",
                integr_scopes=fi_jira.REQUIRED_SCOPES,
                integr_prompt="",
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
                integr_setup_handlers=lambda obj, rcx, _t=fb_tool: [_register_tool_handler(rcx, _t.name, obj.called_by_model, fake_in_scenario=True)],
                integr_provider="facebook",
                integr_prompt="",
            ))

        elif name == "linkedin":
            from flexus_client_kit.integrations import fi_linkedin
            async def _init_linkedin(rcx, setup):
                return fi_linkedin.IntegrationLinkedIn(rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_linkedin.LINKEDIN_TOOL],
                integr_init=_init_linkedin,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "linkedin", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="linkedin",
                integr_scopes=[
                    "openid",
                    "profile",
                    "email",
                    "w_member_social",
                ],
                integr_prompt="",
            ))

        elif name == "linkedin_b2b":
            from flexus_client_kit.integrations import fi_linkedin_b2b
            async def _init_linkedin_b2b(rcx, setup):
                return fi_linkedin_b2b.IntegrationLinkedinB2B(
                    rcx,
                    ad_account_id=(setup or {}).get("ad_account_id", ""),
                    organization_id=(setup or {}).get("organization_id", ""),
                    linkedin_api_version=(setup or {}).get("linkedin_api_version", "202509"),
                )
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_linkedin_b2b.LINKEDIN_B2B_TOOL],
                integr_init=_init_linkedin_b2b,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "linkedin_b2b", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="linkedin",
                integr_scopes=[
                    "r_ads",
                    "rw_ads",
                    "r_ads_reporting",
                    "r_organization_admin",
                    "rw_organization_admin",
                    "r_organization_social",
                    "w_organization_social",
                    "r_organization_social_feed",
                    "w_organization_social_feed",
                    "r_organization_followers",
                    "r_events",
                    "rw_events",
                    "r_marketing_leadgen_automation",
                    "rw_conversions",
                    "r_member_profileAnalytics",
                    "r_member_postAnalytics",
                    "rw_dmp_segments",
                ],
            ))

        elif name == "github":
            from flexus_client_kit.integrations import fi_github
            async def _init_github(rcx, setup):
                return fi_github.IntegrationGitHub(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_github.GITHUB_TOOL],
                integr_init=_init_github,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "github", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="github",
                integr_prompt="",
            ))

        elif name == "slack":
            from flexus_client_kit.integrations import fi_slack, fi_messenger
            async def _init_slack(rcx, setup):
                bot_name = (setup or {}).get("slack_bot_name", "") or rcx.persona.persona_name
                bot_icon_url = (setup or {}).get("slack_bot_icon_url", "")
                if not bot_icon_url:
                    # Auto-fill from marketplace avatar, must be public URL (Slack fetches it server-side)
                    # Also must be PNG via ?format=png — Slack doesn't support WebP
                    pub_url = os.environ.get("FLEXUS_WEB_URL", rcx.fclient.base_url_http).rstrip("/")
                    bot_icon_url = "%s/v1/marketplace/%s/%s/small.webp?format=png" % (
                        pub_url, rcx.persona.persona_marketable_name, rcx.persona.persona_marketable_version)
                obj = fi_slack.IntegrationSlack(rcx.fclient, rcx, bot_name=bot_name, bot_icon_url=bot_icon_url)
                await obj.load_workspace_maps()
                return obj
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_slack.SLACK_TOOL],
                integr_init=_init_slack,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "slack", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="slack",
                integr_is_messenger=True,
                integr_scopes=[
                    "channels:read",
                    "chat:write",
                    "chat:write.customize",
                    "files:read",
                    "users:read",
                    "im:read",
                ],
                integr_prompt=fi_messenger.MESSENGER_PROMPT,
            ))

        elif name == "telegram":
            from flexus_client_kit.integrations import fi_telegram, fi_messenger
            async def _init_telegram(rcx, setup):
                obj = fi_telegram.IntegrationTelegram(rcx.fclient, rcx)
                await obj.initialize()
                return obj
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_telegram.TELEGRAM_TOOL],
                integr_init=_init_telegram,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "telegram", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="telegram",
                integr_is_messenger=True,
                integr_prompt=fi_messenger.MESSENGER_PROMPT,
            ))

        elif name == "discord":
            from flexus_client_kit.integrations import fi_discord2, fi_messenger
            async def _init_discord(rcx, setup):
                obj = fi_discord2.IntegrationDiscord(
                    rcx.fclient, rcx,
                    watch_channels=(setup or {}).get("discord_watch_channels", ""),
                )
                await obj.start_reactive()
                return obj
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_discord2.DISCORD_TOOL],
                integr_init=_init_discord,
                integr_setup_handlers=lambda obj, rcx: [_register_tool_handler(rcx, "discord", obj.called_by_model, fake_in_scenario=True)],
                integr_provider="discord_manual",
                integr_is_messenger=True,
                integr_prompt=fi_messenger.MESSENGER_PROMPT,
            ))

        elif name == "magic_desk":
            from flexus_client_kit.integrations import fi_magic_desk
            async def _init_magic_desk(rcx, setup):
                return fi_magic_desk.IntegrationMagicDesk(rcx.fclient, rcx)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_magic_desk.MAGIC_DESK_TOOL],
                integr_init=_init_magic_desk,
                integr_setup_handlers=lambda obj, rcx: [rcx.on_tool_call("magic_desk")(obj.called_by_model)],
                integr_is_messenger=True,
                integr_prompt="",
            ))

        elif name == "resend":
            from flexus_client_kit.integrations import fi_resend
            async def _init_resend(rcx, setup):
                domains = (rcx.persona.persona_setup or {}).get("DOMAINS", {})
                return fi_resend.IntegrationResend(rcx.fclient, rcx, domains)
            result.append(IntegrationRecord(
                integr_name=name,
                integr_tools=[fi_resend.RESEND_SEND_TOOL, fi_resend.RESEND_REPLY_TOOL, fi_resend.RESEND_SETUP_TOOL],
                integr_init=_init_resend,
                integr_setup_handlers=lambda obj, rcx: [
                    _register_tool_handler(rcx, "email_send", obj.send_called_by_model, fake_in_scenario=True),
                    _register_tool_handler(rcx, "email_reply", obj.reply_called_by_model, fake_in_scenario=True),
                    _register_tool_handler(rcx, "email_setup_domain", obj.setup_called_by_model, fake_in_scenario=True),
                ],
                integr_provider="resend",
                integr_prompt="",
            ))

        elif name.startswith("erp"):   # "erp[meta, data]" or "erp[meta, data, crud, csv_import]"
            from flexus_client_kit.integrations import fi_erp
            subset = _parse_bracket_list(name)
            tool_map = {
                "meta": (fi_erp.ERP_TABLE_META_TOOL, "handle_erp_meta"),
                "data": (fi_erp.ERP_TABLE_DATA_TOOL, "handle_erp_data"),
                "crud": (fi_erp.ERP_TABLE_CRUD_TOOL, "handle_erp_crud"),
                "csv_import": (fi_erp.ERP_CSV_IMPORT_TOOL, "handle_csv_import"),
            }
            if subset is None:
                subset = list(tool_map.keys())
            tools_and_methods = [(tool_map[s][0], tool_map[s][1]) for s in subset]
            async def _init_erp(rcx, setup):
                return fi_erp.IntegrationErp(rcx)
            def _setup_erp(obj, rcx, _tam=tools_and_methods):
                for tool, method_name in _tam:
                    _register_tool_handler(rcx, tool.name, getattr(obj, method_name), fake_in_scenario=True)
            result.append(IntegrationRecord(
                integr_name="erp",
                integr_tools=[t for t, _ in tools_and_methods],
                integr_init=_init_erp,
                integr_setup_handlers=_setup_erp,
                integr_need_mongo=True,
            ))

        elif name.startswith("crm"):   # "crm[contact_info, manage_deal, verify_email]"
            from flexus_client_kit.integrations import fi_crm
            subset = _parse_bracket_list(name)
            tool_map = {
                "contact_info": (fi_crm.CRM_CONTACT_INFO_TOOL, "handle_crm_contact_info"),
                "manage_deal": (fi_crm.MANAGE_CRM_DEAL_TOOL, "handle_manage_crm_deal"),
                "verify_email": (fi_crm.VERIFY_EMAIL_TOOL, "handle_verify_email"),
            }
            if subset is None:
                subset = list(tool_map.keys())
            tools_and_methods = [(tool_map[s][0], tool_map[s][1]) for s in subset]
            async def _init_crm(rcx, setup):
                return fi_crm.IntegrationCrm(rcx)
            def _setup_crm(obj, rcx, _tam=tools_and_methods):
                for tool, method_name in _tam:
                    _register_tool_handler(rcx, tool.name, getattr(obj, method_name), fake_in_scenario=True)
            result.append(IntegrationRecord(
                integr_name="crm",
                integr_tools=[t for t, _ in tools_and_methods],
                integr_init=_init_crm,
                integr_setup_handlers=_setup_crm,
                integr_prompt="",
            ))

        else:
            # Import fi_{name}.py at runtime by name (e.g. "reddit" -> fi_reddit.py).
            # We can't do this at the top of the file because the name is only known at call time.
            mod = importlib.import_module(f"flexus_client_kit.integrations.fi_{name}")

            # The c.__module__ == mod.__name__ guard skips classes that were *imported into* the
            # module from elsewhere (e.g. base classes), keeping only the one defined there.
            integration_class = next(
                (c for _, c in inspect.getmembers(mod, inspect.isclass)
                 if c.__name__.startswith("Integration") and c.__module__ == mod.__name__),
                None,
            )
            if integration_class is None:
                raise ValueError(f"No Integration* class found in fi_{name}.py")

            # fi_*.py defines PROVIDER_NAME = "reddit" (may differ from the file name fi_x.py -> "x").
            provider_name = getattr(mod, "PROVIDER_NAME", name)

            # All fi_*.py integrations speak the same op=help|status|list_methods|call protocol,
            # so one tool schema covers all of them.
            generic_tool = ckit_cloudtool.CloudTool(
                strict=True,
                name=provider_name,
                description=f"{provider_name}: data provider. op=help|status|list_methods|call",
                parameters={
                    "type": "object",
                    "properties": {
                        "op": {"type": "string", "enum": ["help", "status", "list_methods", "call"]},
                        "args": {"type": ["object", "null"]},
                    },
                    "required": ["op", "args"],
                    "additionalProperties": False,
                },
            )

            # Avoid a classic Python loop-capture bug: without it, every closure would share the last
            # iteration's integration_class after the loop completes.
            def _make_generic_init(klass):
                async def _init(rcx, setup, _cls=klass):
                    # XXX: fi_*.py constructors are inconsistent: some accept (rcx), some accept
                    # nothing. Try the more common (rcx) first; fall back to () on TypeError.
                    try:
                        return _cls(rcx)
                    except TypeError:
                        return _cls()
                return _init

            result.append(IntegrationRecord(
                integr_name=provider_name,
                integr_tools=[generic_tool],
                integr_init=_make_generic_init(integration_class),
                # _t=generic_tool captures the current tool into the lambda for the same reason
                # as _make_generic_init above: without it all lambdas would share the last tool.
                integr_setup_handlers=lambda obj, rcx, _t=generic_tool, _f=_should_fake_in_scenario(provider_name): [
                    _register_tool_handler(rcx, _t.name, obj.called_by_model, fake_in_scenario=_f)
                ],
            ))
    return result


def _parse_bracket_list(name: str) -> list[str] | None:
    if "[" not in name:
        return None
    return [g.strip() for g in name.split("[", 1)[1].rstrip("]").split(",")]


async def main_loop_integrations_init(records: list[IntegrationRecord], rcx: ckit_bot_exec.RobotContext, setup: dict | None = None) -> dict[str, Any]:
    from flexus_client_kit.integrations import fi_messenger
    rcx.messengers.clear()
    if any(rec.integr_need_mongo for rec in records) and rcx.personal_mongo is None:
        from pymongo import AsyncMongoClient
        from flexus_client_kit import ckit_mongo
        mongo_conn_str = await ckit_mongo.mongo_fetch_creds(rcx.fclient, rcx.persona.persona_id)
        mongo = AsyncMongoClient(mongo_conn_str)
        rcx.personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    result = {}
    for rec in records:
        obj = await rec.integr_init(rcx, setup)
        rec.integr_setup_handlers(obj, rcx)
        result[rec.integr_name] = obj
        if rec.integr_is_messenger:
            assert isinstance(obj, fi_messenger.FlexusMessenger), f"{rec.integr_name} has integr_is_messenger=True but {type(obj).__name__} doesn't inherit FlexusMessenger"
            rcx.messengers.append(obj)
            @rcx.on_emessage(obj.emessage_type)
            async def _emessage_handler(emsg, _m=obj):
                await _m.handle_emessage(emsg)

    if rcx.messengers:
        @rcx.on_updated_message
        async def _messenger_updated_message(msg: ckit_ask_model.FThreadMessageOutput):
            # Don't worry, you can override it. The default reaction to assistant messages is to get it past messengers:
            for m in rcx.messengers:
                await m.look_assistant_might_have_posted_something(msg)
                await m.look_user_message_got_confirmed(msg)

    return result
