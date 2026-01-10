import json
import logging
import os
import time
from typing import Dict, Optional

import gql

from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_client

logger = logging.getLogger("gchat")


async def create_guest_accessible_thread_with_crm_context(
    fclient: ckit_client.FlexusClient,
    persona_id: str,
    ws_id: str,
    located_fgroup_id: str,
    contact_id: str,
    platform: str = "web",
    title: Optional[str] = None,
    additional_context: Optional[Dict[str, str]] = None,
    skill: str = "default",
    guest_token_ttl: int = 7 * 24 * 3600,
) -> Dict[str, str]:
    http = await fclient.use_http()

    # Step 1: Load CRM contact data
    contact_data = None
    try:
        async with http as h:
            crm_result = await h.execute(
                gql.gql("""query GetContactForGuestThread(
                    $schema_name: String!,
                    $table_name: String!,
                    $ws_id: String!,
                    $skip: Int!,
                    $limit: Int!,
                    $sort_by: [String!]!,
                    $filters: [String!]!,
                    $include: [String!]!
                ) {
                    erp_table_data(
                        schema_name: $schema_name,
                        table_name: $table_name,
                        ws_id: $ws_id,
                        skip: $skip,
                        limit: $limit,
                        sort_by: $sort_by,
                        filters: $filters,
                        include: $include
                    )
                }"""),
                variable_values={
                    "schema_name": "erp",
                    "table_name": "crm_contact",
                    "ws_id": ws_id,
                    "skip": 0,
                    "limit": 1,
                    "sort_by": [],
                    "filters": [f"contact_id:=:{contact_id}"],
                    "include": [],
                },
            )
        contact_data = crm_result.get("erp_table_data", [])
        if not contact_data:
            logger.warning(f"No CRM contact found for {contact_id}")
    except Exception as e:
        logger.warning(f"Failed to fetch CRM contact {contact_id}: {e}")

    # Step 2: Build context message
    parts = [f"{platform.upper()} GUEST CHAT CONTEXT:"]
    if contact_data:
        logger.info(f"Found CRM contact {contact_id}, data: %s" % json.dumps(contact_data[0], indent=2))
        c = contact_data[0]
        parts.append(f"Contact: {c.get('contact_first_name', 'Unknown')} {c.get('contact_last_name', '(Last name missing)')}")
        if c.get('contact_email'):
            parts.append(f"Email: {c['contact_email']}")
        if c.get('contact_company'):
            parts.append(f"Company: {c['contact_company']}")
        if c.get('contact_phone'):
            parts.append(f"Phone: {c['contact_phone']}")
        parts.append(f"CRM Contact ID: {contact_id}")
    else:
        parts.append(f"CRM Contact ID: {contact_id}")

    if additional_context:
        for k, v in additional_context.items():
            parts.append(f"{k}: {v}")

    parts.append("")
    parts.append("This is a guest user accessing via a web chat link. Greet them professionally and assist with their inquiry.")
    msg = "\n".join(parts)

    if title is None:
        title = f"{platform.capitalize()} Guest Chat"

    ft_id = await ckit_ask_model.bot_activate(
        fclient,
        who_is_asking=f"{platform}_guest_activation",
        persona_id=persona_id,
        skill=skill,
        first_question="",
        cd_instruction=json.dumps(msg),
        title=title,
    )
    logger.info(f"Created thread {ft_id} for guest chat, platform={platform}")

    # Step 5: Mark thread as guest-accessible
    await ckit_ask_model.thread_app_capture_patch(
        http,
        ft_id,
        ft_app_searchable="",
        ft_app_specific=json.dumps({
            "guest_accessible": True,
            "platform": platform,
            "contact_id": contact_id,
            "created_for": "guest_web_chat",
            "created_ts": time.time(),
        }),
    )

    async with http as h:
        token_result = await h.execute(
            gql.gql("""mutation CreateGuestToken($ft_id: String!, $contact_email: String!, $ttl: Int!) {
                create_guest_token(ft_id: $ft_id, contact_email: $contact_email, ttl: $ttl)
            }"""),
            variable_values={
                "ft_id": ft_id,
                "contact_email": contact_data[0].get("contact_email", "") if contact_data else "",
                "ttl": guest_token_ttl,
            },
        )
    guest_token = token_result["create_guest_token"]

    base_url = os.environ.get("FLEXUS_WEB_URL", "https://flexus.team")
    guest_url = f"{base_url}/{located_fgroup_id}/{persona_id}/persona?ft_id={ft_id}&guest_token={guest_token}"

    logger.info(f"Created guest-accessible thread {ft_id} with token, url={guest_url[:80]}...")

    return {
        "ft_id": ft_id,
        "guest_token": guest_token,
        "guest_url": guest_url,
    }


async def generate_guest_chat_invitation_for_outreach(
    fclient: ckit_client.FlexusClient,
    persona_id: str,
    ws_id: str,
    located_fgroup_id: str,
    contact_id: str,
    invitation_context: str = "",
    skill: str = "default",
) -> str:
    additional_ctx = None
    if invitation_context:
        additional_ctx = {"Invitation context": invitation_context}

    result = await create_guest_accessible_thread_with_crm_context(
        fclient,
        persona_id,
        ws_id,
        located_fgroup_id,
        contact_id,
        platform="web",
        title="Outreach - Guest Chat",
        additional_context=additional_ctx,
        skill=skill,
    )

    return result["guest_url"]
