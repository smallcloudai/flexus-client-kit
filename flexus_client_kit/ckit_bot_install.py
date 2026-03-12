import base64
import fnmatch
import json
from dataclasses import dataclass
import dataclasses
from pathlib import Path
from typing import Dict, Union, Optional, List, Any, Tuple
import gql

from flexus_simple_bots import prompts_common
from flexus_client_kit import ckit_client, ckit_cloudtool, ckit_integrations_db, ckit_skills, gql_utils


def load_form_bundles_from_dir(forms_dir: Path) -> Dict[str, str]:
    bundles = {}
    if forms_dir.exists():
        for f in forms_dir.iterdir():
            if f.suffix in ('.html', '.json'):
                bundles[f.name] = base64.b64encode(f.read_bytes()).decode("ascii")
    return bundles


def load_form_bundles(install_file: str) -> Dict[str, str]:
    return load_form_bundles_from_dir(Path(install_file).parent / "forms")


@dataclass
class FBotInstallOutput:
    marketable_name: str
    marketable_version: int

@dataclass
class InstallationResult:
    fgroup_id: str
    persona_id: str

@dataclass
class FMarketplaceExpertInput:
    fexp_system_prompt: str
    fexp_python_kernel: str
    fexp_block_tools: str
    fexp_allow_tools: str
    fexp_inactivity_timeout: int = 0
    fexp_app_capture_tools: str = ""
    fexp_description: str = ""
    fexp_preferred_model_default: str = ""
    fexp_subchat_only: bool = False
    fexp_builtin_skills: str = "[]"  # [{"name", "description"}, ...]

    def _tool_allowed(self, name: str) -> bool:
        block = [p.strip() for p in self.fexp_block_tools.split(",") if p.strip()]
        allow = [p.strip() for p in self.fexp_allow_tools.split(",") if p.strip()]
        if allow:
            return any(fnmatch.fnmatch(name, p) for p in allow)
        return not any(fnmatch.fnmatch(name, p) for p in block)

    def filter_tools(self, tools: list[ckit_cloudtool.CloudTool]) -> "FMarketplaceExpertInput":
        filtered = [t for t in tools if self._tool_allowed(t.name) and t.name != "flexus_fetch_skill"]
        if self.fexp_builtin_skills != "[]":
            filtered.append(ckit_skills.FETCH_SKILL_TOOL)
        self.fexp_app_capture_tools = json.dumps([t.openai_style_tool() for t in filtered])
        return self


async def marketplace_upsert_dev_bot(
    client: ckit_client.FlexusClient,
    ws_id: str,
    marketable_name: str,
    marketable_version: str,
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
    marketable_preferred_model_default: str,
    marketable_picture_big_b64: str,
    marketable_picture_small_b64: str,
    marketable_experts: List[Tuple[str, FMarketplaceExpertInput]],
    marketable_tags: List[str] = [],
    marketable_daily_budget_default: int = 1_000_000,  # one dollar in microdollars, serves as a guardrail against overspending, user can change later
    marketable_default_inbox_default: int = 100_000,   # limit for 1 task
    marketable_forms: Optional[Dict[str, str]] = None,
    marketable_required_policydocs: List[str] = [],
    marketable_auth_needed: List[str] = [],
    marketable_auth_supported: List[str] = [],
    marketable_auth_scopes: Optional[Dict[str, List[str]]] = None,
    add_integrations_into_expert_system_prompt: Optional[List[ckit_integrations_db.IntegrationRecord]] = None,
) -> FBotInstallOutput:
    assert ws_id, "Set FLEXUS_WORKSPACE environment variable to your workspace ID"
    assert not ws_id.startswith("fx-"), "You can find workspace id in the browser address bar, when visiting for example the statistics page"

    experts_input = []
    for expert_name, expert in marketable_experts:
        has_a2a = expert._tool_allowed("flexus_hand_over_task")
        sections = [expert.fexp_system_prompt]
        sections.append("# Flexus Environment")
        sections.append(prompts_common.PROMPT_KANBAN)
        if has_a2a:
            sections.append(prompts_common.PROMPT_A2A_COMMUNICATION)
        included_integr = []
        if add_integrations_into_expert_system_prompt:
            for r in add_integrations_into_expert_system_prompt:
                if r.integr_prompt and any(expert._tool_allowed(t.name) for t in r.integr_tools):
                    sections.append(r.integr_prompt)
                    included_integr.append(r.integr_name)
        sections.append(prompts_common.PROMPT_HERE_GOES_SETUP)
        sections = [s.strip() for s in sections]
        prompt = "\n\n\n".join(sections) + "\n"
        skill_names = [s["name"] for s in json.loads(expert.fexp_builtin_skills)]
        tool_names = [t["function"]["name"] for t in json.loads(expert.fexp_app_capture_tools)] if expert.fexp_app_capture_tools else []
        summary = (
            f"  {marketable_name} expert {expert_name!r}\n"
            f"    allow={expert.fexp_allow_tools!r} block={expert.fexp_block_tools!r} has_a2a={has_a2a}\n"
            f"    built-in-tools={tool_names}\n"
            f"    built-in-skills={skill_names}\n"
            f"    prompt sections from integrations: {', '.join(included_integr)}\n"
            f"    len(prompt)={len(prompt)}"
        )
        print(summary)
        # Good debugging opportunity:
        # print(prompt)
        # exit(0)
        prepared = dataclasses.replace(expert, fexp_system_prompt=prompt)
        expert_dict = dataclasses.asdict(prepared)
        expert_dict["fexp_name"] = f"{marketable_name}_{expert_name}"
        experts_input.append(expert_dict)

    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation InstallBot($ws: String!, $name: String!, $ver: String!, $title1: String!, $title2: String!, $author: String!, $accent_color: String!, $occupation: String!, $desc: String!, $typical_group: String!, $repo: String!, $run: String!, $setup: String!, $featured: [FFeaturedActionInput!]!, $intro: String!, $model: String!, $daily: Int!, $inbox: Int!, $experts: [FMarketplaceExpertInput!]!, $schedule: String!, $big: String!, $small: String!, $tags: [String!]!, $forms: String, $required_policydocs: [String!]!, $auth_needed: [String!]!, $auth_supported: [String!]!, $auth_scopes: String) {{
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
                    marketable_preferred_model_default: $model,
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
                    marketable_auth_scopes: $auth_scopes
                ) {{
                    {gql_utils.gql_fields(FBotInstallOutput)}
                }}
            }}"""),
            variable_values={
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
                "featured": marketable_featured_actions,
                "intro": marketable_intro_message,
                "model": marketable_preferred_model_default,
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
            },
        )
        return gql_utils.dataclass_from_dict(r["marketplace_upsert_dev_bot"], FBotInstallOutput)


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
    http = await client.use_http()
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


async def post_install_create_knowledge_eds(
    client: ckit_client.FlexusClient,
    located_fgroup_id: str,
    eds_name: str,
    persona_id: Optional[str] = None,
) -> str:
    """Create a default knowledge EDS for a bot after installation.

    This creates an empty "knowledge_store" EDS that serves as the bot's
    knowledge base. Users can populate it by:
    - Uploading documents through the Flexus UI
    - Asking the bot to crawl a website URL
    - Telling the bot facts to remember (via create_knowledge)

    If persona_id is provided, also writes the EDS ID into the persona's
    setup as ``knowledge_eds_ids`` so that vector search is scoped to
    this bot's knowledge base.

    Returns the eds_id of the created data source.
    """
    http = await client.use_http()
    async with http as h:
        result = await h.execute(
            gql.gql("""mutation CreateKnowledgeEds($input: FExternalDataSourceInput!) {
                external_data_source_create(input: $input) { eds_id }
            }"""),
            variable_values={
                "input": {
                    "located_fgroup_id": located_fgroup_id,
                    "eds_name": eds_name,
                    "eds_type": "knowledge_store",
                    "eds_json": json.dumps({
                        "auto_created": True,
                        "purpose": "Default knowledge base for bot",
                    }),
                }
            },
        )
    eds_id = result["external_data_source_create"]["eds_id"]

    if persona_id:
        try:
            async with http as h:
                await h.execute(
                    gql.gql("""mutation PersonaSetupSetKey($persona_id: String!, $set_key: String!, $set_val: String) {
                        persona_setup_set_key(
                            persona_id: $persona_id,
                            set_key: $set_key,
                            set_val: $set_val
                        )
                    }"""),
                    variable_values={
                        "persona_id": persona_id,
                        "set_key": "knowledge_eds_ids",
                        "set_val": eds_id,
                    },
                )
        except Exception:
            import logging
            logging.getLogger("ckit_bot_install").warning(
                "Failed to write knowledge_eds_ids to persona %s setup", persona_id, exc_info=True,
            )

    return eds_id
