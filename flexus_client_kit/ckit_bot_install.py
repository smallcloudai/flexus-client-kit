import base64
import fnmatch
import json
import logging
import pprint
import re
from dataclasses import dataclass
import dataclasses
from pathlib import Path
from typing import Dict, Union, Optional, List, Any, Tuple
import gql
import gql.transport.exceptions

from flexus_simple_bots import prompts_common
from flexus_client_kit import ckit_client, ckit_cloudtool, ckit_integrations_db, ckit_skills, gql_utils

logger = logging.getLogger("btins")


@dataclass
class FBotInstallOutput:
    marketable_name: str
    marketable_version: int


@dataclass
class FMarketplaceExpertInput:
    fexp_system_prompt: str
    fexp_python_kernel: str
    fexp_allow_tools: str
    fexp_nature: str  # NATURE_INTERACTIVE NATURE_SEMI_AUTONOMOUS NATURE_AUTONOMOUS NATURE_NO_TASK
    fexp_inactivity_timeout: int = 0
    fexp_app_capture_tools: str = ""
    fexp_description: str = ""
    fexp_model_class: str = ""
    fexp_subchat_only: bool = False
    fexp_builtin_skills: str = "[]"  # [{"name", "description"}, ...]
    fexp_activation_options: str = "{}"

    def _tool_allowed(self, name: str) -> bool:
        allow = [p.strip() for p in self.fexp_allow_tools.split(",") if p.strip()]
        if not allow:
            return True
        return any(fnmatch.fnmatch(name, p) for p in allow)

    def filter_tools(self, tools: list[ckit_cloudtool.CloudTool]) -> "FMarketplaceExpertInput":
        local_names = {t.name for t in tools}
        for p in [p.strip() for p in self.fexp_allow_tools.split(",") if p.strip()]:
            matches_known = any(fnmatch.fnmatch(name, p) for name in ckit_cloudtool.CLOUDTOOLS_ALL_KNOWN)
            matches_local = any(fnmatch.fnmatch(name, p) for name in local_names)
            if not matches_known and not matches_local and (not "*" in p):
                raise ValueError(f"fexp_allow_tools pattern {p!r} doesn't match any known cloud tool or local tool")
            if "*" in p and matches_known:
                raise ValueError(f"fexp_allow_tools pattern {p!r} with wildcard matches cloud tools — use exact names for cloud tools")
        filtered = [t for t in tools if self._tool_allowed(t.name) and t.name != "flexus_fetch_skill"]
        if self.fexp_builtin_skills != "[]":
            filtered.append(ckit_skills.FETCH_SKILL_TOOL)
        self.fexp_app_capture_tools = json.dumps([t.openai_style_tool() for t in filtered])
        return self


async def marketplace_upsert_dev_bot(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_dir: Path,
    marketable_title1: str,
    marketable_title2: str,
    marketable_author: str,
    marketable_accent_color: str,
    marketable_occupation: str,
    marketable_description: str,
    marketable_typical_group: str,
    marketable_github_repo: str,
    marketable_run_this: str,
    marketable_schedule: List[Dict[str, Any]],
    marketable_setup_default: List[Dict[str, Union[str, int, float, bool]]],
    marketable_featured_actions: List[Dict[str, Any]],
    marketable_intro_message: str,
    marketable_preferred_model_expensive: str,
    marketable_preferred_model_cheap: str,
    marketable_picture_big_b64: str,
    marketable_picture_small_b64: str,
    marketable_experts: List[Tuple[str, FMarketplaceExpertInput]],
    marketable_tags: List[str] = [],
    marketable_daily_budget_default: int = 1_000_000,  # one dollar in microdollars, serves as a guardrail against overspending, user can change later
    marketable_default_inbox_default: int = 100_000,   # limit for 1 task
    marketable_max_inprogress: int = 2,
    marketable_forms: Optional[Dict[str, str]] = None,
    marketable_required_policydocs: List[str] = [],
    marketable_auth_needed: List[str] = [],
    marketable_auth_supported: List[str] = [],
    marketable_auth_scopes: Optional[Dict[str, List[str]]] = None,
    marketable_features: List[str] = [],
    add_integrations_into_expert_system_prompt: Optional[List[ckit_integrations_db.IntegrationRecord]] = None,
) -> FBotInstallOutput:
    assert ws_id, "Set FLEXUS_WORKSPACE environment variable to your workspace ID"
    assert not ws_id.startswith("fx-"), "You can find workspace id in the browser address bar, when visiting for example the statistics page"
    for w in list(bot_dir.glob("*-*x*.webp")):
        if not marketable_picture_small_b64 and "-256x256" in w.name:
            marketable_picture_small_b64 = base64.b64encode(w.read_bytes()).decode("ascii")
        elif not marketable_picture_big_b64 and any(f"-{bw}x{bh}" in w.name for bw, bh in [(1024, 1536), (832, 1248), (896, 1152)]):
            marketable_picture_big_b64 = base64.b64encode(w.read_bytes()).decode("ascii")
    marketable_name = bot_dir.name
    version_file = bot_dir.parent / "VERSION"
    marketable_version = version_file.read_text().strip()

    experts_input = []
    for expert_name, expert in marketable_experts:
        for p in expert.fexp_allow_tools.split(","):
            p = p.strip()
            if p == "*":
                raise ValueError(f"Expert {expert_name!r}: bare '*' in fexp_allow_tools is not allowed, use empty string for all tools")
        has_a2a = expert._tool_allowed("flexus_hand_over_task")
        sections = [expert.fexp_system_prompt]
        sections.append("# Flexus Environment")
        sections.append(prompts_common.PROMPT_KANBAN)
        if has_a2a:
            sections.append(prompts_common.PROMPT_A2A_COMMUNICATION)
        included_integr = []
        if add_integrations_into_expert_system_prompt:
            for r in add_integrations_into_expert_system_prompt:
                # Good debugging opportunity 1
                # has_prompt = bool(r.integr_prompt)
                # already_in = any(r.integr_prompt in s for s in sections) if has_prompt else False
                # tool_allowed = any(expert._tool_allowed(t.name) for t in r.integr_tools)
                # print("Q"*35, [t.name for t in r.integr_tools], f"has_prompt={has_prompt} already_in={already_in} tool_allowed={tool_allowed}")
                if r.integr_prompt and not any(r.integr_prompt in s for s in sections) and any(expert._tool_allowed(t.name) for t in r.integr_tools):
                    sections.append(r.integr_prompt)
                    included_integr.append(r.integr_name)
        sections.append(prompts_common.PROMPT_HERE_GOES_SETUP)
        sections = [s.strip() for s in sections]
        prompt = "\n\n\n".join(sections) + "\n"
        skill_names = [s["name"] for s in json.loads(expert.fexp_builtin_skills)]
        tool_names = [t["function"]["name"] for t in json.loads(expert.fexp_app_capture_tools)] if expert.fexp_app_capture_tools else []
        allow_sorted = sorted(expert.fexp_allow_tools.split(","))
        summary = (
            f"  {marketable_name} expert {expert_name!r}\n"
            + _super_nice_list(allow_sorted, "    allow=", f" has_a2a={has_a2a}") + "\n"
            + _super_nice_list(tool_names, "    built-in-tools=") + "\n"
            + _super_nice_list(skill_names, "    built-in-skills=") + "\n"
            + f"    prompt sections from integrations: {', '.join(included_integr)}\n"
            f"    len(prompt)={len(prompt)}"
        )
        print(summary)
        # Good debugging opportunity 2
        # print(prompt)
        # exit(0)
        prepared = dataclasses.replace(expert, fexp_system_prompt=prompt)
        expert_dict = dataclasses.asdict(prepared)
        expert_dict["fexp_name"] = f"{marketable_name}_{expert_name}"
        experts_input.append(expert_dict)

    mutation = gql.gql(f"""mutation InstallBot($ws: String!, $name: String!, $ver: String!, $title1: String!, $title2: String!, $author: String!, $accent_color: String!, $occupation: String!, $desc: String!, $typical_group: String!, $repo: String!, $run: String!, $setup: String!, $featured: [FFeaturedActionInput!]!, $intro: String!, $model_expensive: String!, $model_cheap: String!, $daily: Int!, $inbox: Int!, $experts: [FMarketplaceExpertInput!]!, $schedule: String!, $big: String!, $small: String!, $tags: [String!]!, $forms: String, $required_policydocs: [String!]!, $auth_needed: [String!]!, $auth_supported: [String!]!, $auth_scopes: String, $max_inprogress: Int!, $features: [String!]!) {{
        marketplace_upsert_dev_bot(
            ws_id: $ws,
            marketable_name: $name,
            marketable_version: $ver,
            marketable_title1: $title1,
            marketable_title2: $title2,
            marketable_author: $author,
            marketable_accent_color: $accent_color,
            marketable_occupation: $occupation,
            marketable_description: $desc,
            marketable_typical_group: $typical_group,
            marketable_github_repo: $repo,
            marketable_run_this: $run,
            marketable_setup_default: $setup,
            marketable_featured_actions: $featured,
            marketable_intro_message: $intro,
            marketable_preferred_model_expensive: $model_expensive,
            marketable_preferred_model_cheap: $model_cheap,
            marketable_daily_budget_default: $daily,
            marketable_default_inbox_default: $inbox,
            marketable_experts: $experts,
            marketable_schedule: $schedule,
            marketable_picture_big_b64: $big,
            marketable_picture_small_b64: $small,
            marketable_tags: $tags,
            marketable_forms: $forms,
            marketable_required_policydocs: $required_policydocs,
            marketable_auth_needed: $auth_needed,
            marketable_auth_supported: $auth_supported,
            marketable_auth_scopes: $auth_scopes,
            marketable_max_inprogress: $max_inprogress,
            marketable_features: $features
        ) {{
            {gql_utils.gql_fields(FBotInstallOutput)}
        }}
    }}""")
    variables = {
        "ws": ws_id,
        "name": marketable_name,
        "ver": marketable_version,
        "title1": marketable_title1,
        "title2": marketable_title2,
        "author": marketable_author,
        "accent_color": marketable_accent_color,
        "occupation": marketable_occupation,
        "desc": marketable_description,
        "typical_group": marketable_typical_group,
        "repo": marketable_github_repo,
        "run": marketable_run_this,
        "setup": json.dumps(marketable_setup_default),
        "featured": [{"feat_expert": "default", "feat_depends_on_setup": [], **fa} for fa in marketable_featured_actions],
        "intro": marketable_intro_message,
        "model_expensive": marketable_preferred_model_expensive,
        "model_cheap": marketable_preferred_model_cheap,
        "daily": marketable_daily_budget_default,
        "inbox": marketable_default_inbox_default,
        "experts": experts_input,
        "schedule": json.dumps(marketable_schedule),
        "tags": marketable_tags,
        "big": marketable_picture_big_b64,
        "small": marketable_picture_small_b64,
        "forms": json.dumps(marketable_forms or {}),
        "required_policydocs": marketable_required_policydocs,
        "auth_needed": marketable_auth_needed,
        "auth_supported": marketable_auth_supported,
        "auth_scopes": json.dumps(marketable_auth_scopes) if marketable_auth_scopes else None,
        "max_inprogress": marketable_max_inprogress,
        "features": marketable_features,
    }
    http = await client.use_http_on_behalf("", "")
    async with http as h:
        try:
            r = await h.execute(mutation, variable_values=variables)
        except gql.transport.exceptions.TransportQueryError as e:
            m = re.search(r"must be higher than existing version (\d+)", str(e))
            if not m:
                raise
            existing_int = int(m.group(1))
            old_version = marketable_version
            marketable_version = ckit_client.marketplace_version_as_str(existing_int + 1)
            variables["ver"] = marketable_version
            version_file.write_text(marketable_version + "\n")
            logger.info("Version conflict, bumped %s -> %s", old_version, marketable_version)
            r = await h.execute(mutation, variable_values=variables)
        return gql_utils.dataclass_from_dict(r["marketplace_upsert_dev_bot"], FBotInstallOutput)


@dataclass
class InstallationResult:
    fgroup_id: str
    persona_id: str


async def bot_install_from_marketplace(
    client: ckit_client.FlexusClient,
    ws_id: str,
    inside_fgroup: Optional[str],
    persona_marketable_name: str,
    persona_name: str,
    new_setup: Dict[str, Union[str, int, bool]],
    install_dev_version: bool = False,
    persona_id: Optional[str] = None,
    specific_version: Optional[int] = None,
) -> InstallationResult:
    # Typically used by scenario to create a tmp bot, with predefined persona_id so it's easier to interact later
    http = await client.use_http_on_behalf("", "")
    assert isinstance(new_setup, dict)
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation PersonaUpsert($ws: String!, $g: String, $mn: String!, $id: String, $name: String!, $setup: String!, $v: Int, $dev: Boolean!) {
                bot_install_from_marketplace(
                    ws_id: $ws,
                    inside_fgroup_id: $g,
                    persona_marketable_name: $mn,
                    persona_id: $id,
                    persona_name: $name,
                    new_setup: $setup,
                    specific_version: $v,
                    install_dev_version: $dev,
                ) {
                    fgroup_id
                    persona_id
                }
            }"""),
            variable_values={
                "ws": ws_id,
                "g": inside_fgroup,
                "mn": persona_marketable_name,
                "id": persona_id,
                "name": persona_name,
                "setup": json.dumps(new_setup),
                "v": specific_version,
                "dev": install_dev_version,
            },
        )
        return gql_utils.dataclass_from_dict(r["bot_install_from_marketplace"], InstallationResult)


def load_form_bundles_from_dir(forms_dir: Path) -> Dict[str, str]:
    bundles = {}
    if forms_dir.exists():
        for f in forms_dir.iterdir():
            if f.suffix in ('.html', '.json'):
                bundles[f.name] = base64.b64encode(f.read_bytes()).decode("ascii")
    return bundles


def load_form_bundles(install_file: str) -> Dict[str, str]:
    return load_form_bundles_from_dir(Path(install_file).parent / "forms")


def _super_nice_list(items, prefix, suffix=""):
    line = prefix + ", ".join(items) + suffix
    if len(line) <= 120:
        return line
    indent = " " * 6
    lines = [prefix]
    cur = indent
    for i, item in enumerate(items):
        addition = item + (", " if i < len(items) - 1 else suffix)
        if cur == indent:
            cur += addition
        elif len(cur) + len(addition) > 120:
            lines.append(cur)
            cur = indent + addition
        else:
            cur += addition
    if cur.strip():
        lines.append(cur)
    return "\n".join(lines)
