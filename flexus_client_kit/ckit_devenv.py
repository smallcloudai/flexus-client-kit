import logging
from dataclasses import dataclass
from typing import Any, List, Optional
import gql

from flexus_client_kit import ckit_client, gql_utils

logger = logging.getLogger("devenv")

@dataclass
class FDevEnvironmentOutput:
    owner_fuser_id: str
    owner_shared: bool
    located_fgroup_id: str
    devenv_id: str
    devenv_repo_uri: str
    devenv_setup_script: str
    devenv_env_vars: Optional[Any]
    devenv_docker_image: str
    devenv_auth_id: Optional[str]
    devenv_created_ts: float
    devenv_modified_ts: float

async def dev_environments_list_in_subgroups(
    fclient: ckit_client.FlexusClient,
    fgroup_id: str,
) -> List[FDevEnvironmentOutput]:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(
                f"""query DevEnvListInSubgroups($fgroup_id: String!) {{
                    dev_environments_list_in_subgroups(fgroup_id: $fgroup_id) {{
                        {gql_utils.gql_fields(FDevEnvironmentOutput)}
                    }}
                }}""",
            ),
            variable_values={"fgroup_id": fgroup_id},
        )
    devenv_list = r["dev_environments_list_in_subgroups"]
    return [gql_utils.dataclass_from_dict(devenv, FDevEnvironmentOutput) for devenv in devenv_list]