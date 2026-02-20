import base64
import json
from dataclasses import dataclass
import dataclasses
from pathlib import Path
from typing import Dict, Union, Optional, List, Any, Tuple
import argparse
import gql

from flexus_client_kit import ckit_client, ckit_cloudtool, gql_utils


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

    def provide_tools(self, tools: list[ckit_cloudtool.CloudTool]) -> "FMarketplaceExpertInput":
        self.fexp_app_capture_tools = json.dumps([t.openai_style_tool() for t in tools])
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
    marketable_daily_budget_default: int,
    marketable_default_inbox_default: int,
    marketable_picture_big_b64: str,
    marketable_picture_small_b64: str,
    marketable_experts: List[Tuple[str, FMarketplaceExpertInput]],
    marketable_tags: List[str] = [],
    marketable_forms: Optional[Dict[str, str]] = None,
    marketable_required_policydocs: List[str] = [],
    marketable_auth_needed: List[str] = [],
    marketable_auth_supported: List[str] = [],
    marketable_auth_scopes: Optional[Dict[str, List[str]]] = None,
) -> FBotInstallOutput:
    assert ws_id, "Set FLEXUS_WORKSPACE environment variable to your workspace ID"
    assert not ws_id.startswith("fx-"), "You can find workspace id in the browser address bar, when visiting for example the statistics page"
    http = await client.use_http()
    async with http as h:
        experts_input = []
        for expert_type, expert in marketable_experts:
            expert_dict = dataclasses.asdict(expert)
            expert_dict["fexp_name"] = f"{marketable_name}_{expert_type}"
            experts_input.append(expert_dict)
        # NOTE: marketable_stage removed from mutation for staging API compatibility
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

