import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
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

async def dev_environment_create(
    fclient: ckit_client.FlexusClient,
    fgroup_id: str,
    repo_uri: str,
    setup_script: str,
    docker_image: str,
    env_vars: Dict[str, str],
    ft_id: str,
) -> FDevEnvironmentOutput:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(gql.gql(f"""
            mutation CreateDevEnv($input: FDevEnvironmentInput!, $ft_id: String) {{
                dev_environment_create(input: $input, ft_id: $ft_id) {{
                    {gql_utils.gql_fields(FDevEnvironmentOutput)}
                }}
            }}"""),
            variable_values={
                "input": {
                    "located_fgroup_id": fgroup_id,
                    "devenv_repo_uri": repo_uri,
                    "devenv_setup_script": setup_script,
                    "devenv_docker_image": docker_image,
                    "devenv_env_vars": json.dumps(env_vars),
                },
                "ft_id": ft_id,
            },
        )
    return gql_utils.dataclass_from_dict(r["dev_environment_create"], FDevEnvironmentOutput)

async def dev_environment_patch(
    fclient: ckit_client.FlexusClient,
    devenv_id: str,
    setup_script: Optional[str],
    docker_image: Optional[str],
    env_vars: Optional[Dict[str, str]],
    ft_id: str,
) -> FDevEnvironmentOutput:
    patch = {}
    if setup_script is not None:
        patch["devenv_setup_script"] = setup_script
    if docker_image is not None:
        patch["devenv_docker_image"] = docker_image
    if env_vars is not None:
        patch["devenv_env_vars"] = json.dumps(env_vars)
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(gql.gql(f"""
            mutation PatchDevEnv($id: String!, $patch: FDevEnvironmentPatch!, $ft_id: String) {{
                dev_environment_patch(id: $id, patch: $patch, ft_id: $ft_id) {{
                    {gql_utils.gql_fields(FDevEnvironmentOutput)}
                }}
            }}"""),
            variable_values={"id": devenv_id, "patch": patch, "ft_id": ft_id},
        )
    return gql_utils.dataclass_from_dict(r["dev_environment_patch"], FDevEnvironmentOutput)

async def dev_environment_delete(fclient: ckit_client.FlexusClient, devenv_id: str, ft_id: str) -> None:
    http = await fclient.use_http()
    async with http as h:
        await h.execute(
            gql.gql("""mutation DeleteDevEnv($id: String!, $ft_id: String) {
                dev_environment_delete(id: $id, ft_id: $ft_id)
            }"""),
            variable_values={"id": devenv_id, "ft_id": ft_id},
        )

async def format_devenv_list(fclient: ckit_client.FlexusClient, fgroup_id: str) -> str:
    devenv_list = await dev_environments_list_in_subgroups(fclient, fgroup_id)
    if devenv_list:
        result = "Available repos:\n"
        for devenv in devenv_list:
            result += f"  - {devenv.devenv_repo_uri}\n"
        result += "And public repositories\n"
        return result
    return "No dev environments configured.\nPublic repositories are available.\n"
