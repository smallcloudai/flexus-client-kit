import json
from dataclasses import dataclass
import dataclasses
from typing import Dict, Union, Optional, List, Any
import gql

from flexus_client_kit import ckit_client, gql_utils


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
    fexp_name: str
    fexp_system_prompt: str
    fexp_python_kernel: str
    fexp_block_tools: str
    fexp_allow_tools: str
    fexp_app_capture_tools: str = ""


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
    marketable_preferred_model_default: str,
    marketable_daily_budget_default: int,
    marketable_default_inbox_default: int,
    marketable_picture_big_b64: str,
    marketable_picture_small_b64: str,
    marketable_expert_default: FMarketplaceExpertInput,
    marketable_expert_todo: Optional[FMarketplaceExpertInput] = None,
    marketable_expert_setup: Optional[FMarketplaceExpertInput] = None,
    marketable_expert_subchat: Optional[FMarketplaceExpertInput] = None,
    marketable_tags: List[str] = [],
    marketable_stage: str = "MARKETPLACE_DEV",
) -> FBotInstallOutput:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation InstallBot($ws: String!, $name: String!, $ver: String!, $title1: String!, $title2: String!, $author: String!, $accent_color: String!, $occupation: String!, $desc: String!, $typical_group: String!, $repo: String!, $run: String!, $setup: String!, $model: String!, $daily: Int!, $inbox: Int!, $e1: FMarketplaceExpertInput!, $e2: FMarketplaceExpertInput, $e3: FMarketplaceExpertInput, $e4: FMarketplaceExpertInput, $schedule: String!, $big: String!, $small: String!, $tags: [String!]!, $stage: String!) {{
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
                    marketable_preferred_model_default: $model,
                    marketable_daily_budget_default: $daily,
                    marketable_default_inbox_default: $inbox,
                    marketable_expert_default: $e1,
                    marketable_expert_todo: $e2,
                    marketable_expert_setup: $e3,
                    marketable_expert_subchat: $e4,
                    marketable_schedule: $schedule,
                    marketable_picture_big_b64: $big,
                    marketable_picture_small_b64: $small,
                    marketable_stage: $stage,
                    marketable_tags: $tags
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
                "occupation": marketable_occupation,
                "desc": marketable_description,
                "typical_group": marketable_typical_group,
                "repo": marketable_github_repo,
                "run": marketable_run_this,
                "setup": json.dumps(marketable_setup_default),
                "model": marketable_preferred_model_default,
                "daily": marketable_daily_budget_default,
                "inbox": marketable_default_inbox_default,
                "e1": dataclasses.asdict(marketable_expert_default),
                "e2": dataclasses.asdict(marketable_expert_todo) if marketable_expert_todo else None,
                "e3": dataclasses.asdict(marketable_expert_setup) if marketable_expert_setup else None,
                "e4": dataclasses.asdict(marketable_expert_subchat) if marketable_expert_subchat else None,
                "schedule": json.dumps(marketable_schedule),
                "tags": marketable_tags,
                "stage": marketable_stage,
                "big": marketable_picture_big_b64,
                "small": marketable_picture_small_b64,
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

