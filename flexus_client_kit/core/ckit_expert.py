import asyncio
from typing import Optional, Any, List
from dataclasses import dataclass
import gql

from flexus_client_kit.core import ckit_client, gql_utils


@dataclass
class FModelItem:
    provm_name: str


@dataclass
class FCloudTool:
    owner_fuser_id: Optional[str]
    located_fgroup_id: Optional[str]
    ctool_id: str
    ctool_name: str
    ctool_description: str
    ctool_confirmed_exists_ts: Optional[float]
    ctool_parameters: Any


@dataclass
class FExpertChoiceConsequences:
    models: List[FModelItem]
    cloudtools: List[FCloudTool]


async def make_sure_have_expert(
    client: ckit_client.FlexusClient,
    system_prompt: str,
    python_kernel: str,
    owner_fuser_id: Optional[str],
    fgroup_id: Optional[str],
    fexp_name: str,
) -> str:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(
                """mutation MakeSure($sp: String!, $pk: String!, $o: String, $g: String, $n: String!) {
                    make_sure_have_expert(
                        system_prompt: $sp,
                        python_kernel: $pk,
                        owner_fuser_id: $o,
                        fgroup_id: $g,
                        fexp_name: $n
                    )
                }"""
            ),
            variable_values={
                "sp": system_prompt,
                "pk": python_kernel,
                "o": owner_fuser_id,
                "g": fgroup_id,
                "n": fexp_name,
            },
        )
        return r["make_sure_have_expert"]


async def expert_choice_consequences(
    client: ckit_client.FlexusClient,
    fexp_id: str,
    inside_fgroup_id: str,
) -> FExpertChoiceConsequences:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(
                f"""query Conseq2($e: String!, $g: String!) {{
                    expert_choice_consequences(
                        fexp_id: $e,
                        inside_fgroup_id: $g
                    ) {{
                        {gql_utils.gql_fields(FExpertChoiceConsequences)}
                    }}
                }}"""
            ),
            variable_values={"e": fexp_id, "g": inside_fgroup_id},
        )
        return gql_utils.dataclass_from_dict(
            r["expert_choice_consequences"], FExpertChoiceConsequences
        )


async def test(super: bool):
    inside_fgroup_id = "solar_root"
    fexp_id = "id:edit:1"
    if not super:
        client = ckit_client.FlexusClient("ckit_test", api_key="sk_alice_123456")
    else:
        client = ckit_client.FlexusClient("ckit_test")
    consequences = await expert_choice_consequences(client, fexp_id, inside_fgroup_id)
    print("To start a thread in %r using expert %r I'd have a choice of %d models:" % (inside_fgroup_id, fexp_id, len(consequences.models)))
    for c in consequences.models:
        print("  %s" % c.provm_name)
    print("And %d cloudtools:" % len(consequences.cloudtools))
    for c in consequences.cloudtools:
        print("  %s" % c.ctool_name)
    print("Full response:", consequences)


if __name__ == "__main__":
    asyncio.run(test(False))

