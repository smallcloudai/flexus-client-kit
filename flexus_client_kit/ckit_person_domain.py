"""
Client-kit GraphQL helpers for the person-centric foundation (U4.5).

Wraps the PersonDomainQuery/PersonDomainMutation GQL API so bot runtime code
can resolve, create, and link persons and applications without direct DB access.

Public API (all are best-effort: log warnings on error, return None/False):
  ensure_person_for_discord_user  - resolve or create person + link discord identity
  application_find_latest         - fetch the most recent application for a person
  application_create_pending      - create a new PENDING application
  application_apply_decision      - update status/decision on an existing application

Style follows existing client-kit GraphQL helper modules: module-level gql constants, module-level async functions,
TransportQueryError + (TypeError, KeyError, ValueError) as the caught exception set.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_erp
from flexus_client_kit import erp_schema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GQL documents
# ---------------------------------------------------------------------------

_GQL_PERSON_BY_IDENTITY = gql.gql(
    """query PersonByPlatformIdentityRuntime(
        $ws_id: String!
        $platform: String!
        $user_id: String!
    ) {
        person_by_platform_identity(
            ws_id: $ws_id
            identity_platform: $platform
            identity_external_user_id: $user_id
        ) {
            person_id
            identity_id
        }
    }""",
)

_GQL_PERSON_CREATE = gql.gql(
    """mutation PersonCreateRuntime($ws_id: String!, $label: String!) {
        person_create(input: { ws_id: $ws_id, person_label: $label }) {
            person_id
        }
    }""",
)

_GQL_IDENTITY_UPSERT = gql.gql(
    """mutation PersonUpsertIdentityRuntime(
        $person_id: String!
        $platform: String!
        $user_id: String!
        $endpoint: String!
    ) {
        person_upsert_identity(input: {
            person_id: $person_id
            identity_platform: $platform
            identity_external_user_id: $user_id
            identity_external_endpoint: $endpoint
        }) {
            identity_id
        }
    }""",
)

_GQL_APPLICATION_LIST = gql.gql(
    """query ApplicationListLatestRuntime($ws_id: String!, $person_id: String!) {
        application_list(ws_id: $ws_id, person_id: $person_id, limit: 1) {
            application_id
            application_status
            application_decision
        }
    }""",
)

_GQL_APPLICATION_CREATE = gql.gql(
    """mutation ApplicationCreateRuntime(
        $ws_id: String!
        $person_id: String
        $status: String!
        $source: String!
        $platform: String!
        $payload: String
        $details: String
    ) {
        application_create(input: {
            ws_id: $ws_id
            person_id: $person_id
            application_status: $status
            application_source: $source
            application_platform: $platform
            application_payload: $payload
            application_details: $details
        }) {
            application_id
            application_status
        }
    }""",
)

_GQL_APPLICATION_UPDATE = gql.gql(
    """mutation ApplicationUpdateRuntime(
        $application_id: String!
        $status: String
        $decision: String
        $details: String
    ) {
        application_update(input: {
            application_id: $application_id
            application_status: $status
            application_decision: $decision
            application_details: $details
        }) {
            application_id
            application_status
            application_decision
        }
    }""",
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

async def ensure_person_for_discord_user(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    discord_user_id: str,
    username: str,
) -> Optional[str]:
    """
    Resolve or create a canonical person for a Discord user and link the identity.

    Returns person_id on success, None on any error.

    Race note: two concurrent joins for the same Discord user could create two person
    records momentarily; the identity unique constraint (ws_id, platform, user_id) means
    the last upsert_identity wins, leaving the earlier person_id orphaned. This is
    accepted as an extremely rare event in practice.
    """
    try:
        async with (await fclient.use_http()) as http:
            r = await http.execute(
                _GQL_PERSON_BY_IDENTITY,
                variable_values={
                    "ws_id": ws_id,
                    "platform": "discord",
                    "user_id": discord_user_id,
                },
            )
        existing = r.get("person_by_platform_identity") if isinstance(r, dict) else None
        if isinstance(existing, dict) and existing.get("person_id"):
            return str(existing["person_id"])

        # No existing identity: create person + link identity
        label = username or ("discord:%s" % discord_user_id)
        async with (await fclient.use_http()) as http:
            rc = await http.execute(
                _GQL_PERSON_CREATE,
                variable_values={"ws_id": ws_id, "label": label},
            )
        person_row = rc.get("person_create") if isinstance(rc, dict) else None
        if not isinstance(person_row, dict) or not person_row.get("person_id"):
            logger.warning(
                "ensure_person_for_discord_user: person_create returned no person_id ws=%s uid=%s",
                ws_id,
                discord_user_id,
            )
            return None
        person_id = str(person_row["person_id"])

        async with (await fclient.use_http()) as http:
            await http.execute(
                _GQL_IDENTITY_UPSERT,
                variable_values={
                    "person_id": person_id,
                    "platform": "discord",
                    "user_id": discord_user_id,
                    "endpoint": "",
                },
            )
        logger.info(
            "ensure_person_for_discord_user created person=%s ws=%s discord_uid=%s",
            person_id,
            ws_id,
            discord_user_id,
        )
        return person_id
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning(
            "ensure_person_for_discord_user GQL error ws=%s uid=%s: %s %s",
            ws_id,
            discord_user_id,
            type(e).__name__,
            e,
        )
        return None
    except (TypeError, KeyError, ValueError) as e:
        logger.warning(
            "ensure_person_for_discord_user parse error ws=%s uid=%s: %s %s",
            ws_id,
            discord_user_id,
            type(e).__name__,
            e,
        )
        return None


async def application_find_latest(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    person_id: str,
) -> Optional[dict]:
    """
    Return the most recent application dict for a person, or None if not found or on error.

    Dict keys: application_id, application_status, application_decision.
    """
    try:
        async with (await fclient.use_http()) as http:
            r = await http.execute(
                _GQL_APPLICATION_LIST,
                variable_values={"ws_id": ws_id, "person_id": person_id},
            )
        rows = r.get("application_list") if isinstance(r, dict) else None
        if not isinstance(rows, list) or not rows:
            return None
        row = rows[0]
        if not isinstance(row, dict) or not row.get("application_id"):
            return None
        return {
            "application_id": str(row["application_id"]),
            "application_status": str(row.get("application_status") or ""),
            "application_decision": str(row.get("application_decision") or ""),
        }
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning(
            "application_find_latest GQL error ws=%s person=%s: %s %s",
            ws_id,
            person_id,
            type(e).__name__,
            e,
        )
        return None
    except (TypeError, KeyError, ValueError) as e:
        logger.warning(
            "application_find_latest parse error ws=%s person=%s: %s %s",
            ws_id,
            person_id,
            type(e).__name__,
            e,
        )
        return None


async def application_create_pending(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    person_id: str,
    *,
    source: str = "discord_bot",
    platform: str = "discord",
    payload: Optional[dict] = None,
) -> Optional[str]:
    """
    Create a new PENDING application for a person. Returns application_id or None on error.

    Used on member_joined to register a durable application record before any gatekeeper decision.
    """
    try:
        payload_json = json.dumps(payload) if payload is not None else None
        async with (await fclient.use_http()) as http:
            r = await http.execute(
                _GQL_APPLICATION_CREATE,
                variable_values={
                    "ws_id": ws_id,
                    "person_id": person_id,
                    "status": "PENDING",
                    "source": source,
                    "platform": platform,
                    "payload": payload_json,
                    "details": None,
                },
            )
        row = r.get("application_create") if isinstance(r, dict) else None
        if not isinstance(row, dict) or not row.get("application_id"):
            logger.warning(
                "application_create_pending: no application_id returned ws=%s person=%s",
                ws_id,
                person_id,
            )
            return None
        app_id = str(row["application_id"])
        logger.info(
            "application_create_pending app=%s ws=%s person=%s",
            app_id,
            ws_id,
            person_id,
        )
        return app_id
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning(
            "application_create_pending GQL error ws=%s person=%s: %s %s",
            ws_id,
            person_id,
            type(e).__name__,
            e,
        )
        return None
    except (TypeError, KeyError, ValueError) as e:
        logger.warning(
            "application_create_pending parse error ws=%s person=%s: %s %s",
            ws_id,
            person_id,
            type(e).__name__,
            e,
        )
        return None


async def ensure_discord_contact(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    discord_user_id: str,
    display_name: str,
) -> Optional[str]:
    """
    Find or create a crm_contact keyed by contact_platform_ids.discord == discord_user_id.

    Returns contact_id on success, None on error.
    Idempotent: existing contacts are returned as-is without modification.
    Called both on member_joined (future joins) and during bootstrap (existing members).
    """
    try:
        rows = await ckit_erp.erp_table_data(
            await fclient.use_http(),
            "crm_contact",
            ws_id,
            erp_schema.CrmContact,
            filters="contact_platform_ids->discord:=:%s" % discord_user_id,
            limit=1,
        )
        if rows:
            return str(rows[0].contact_id)

        name = (display_name or ("discord:%s" % discord_user_id)).strip()
        parts = name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        new_id = await ckit_erp.erp_record_create(
            await fclient.use_http(),
            "crm_contact",
            ws_id,
            {
                "ws_id": ws_id,
                "contact_first_name": first_name,
                "contact_last_name": last_name,
                "contact_platform_ids": {"discord": discord_user_id},
            },
        )
        contact_id = str(new_id) if new_id else ""
        if contact_id:
            logger.info(
                "ensure_discord_contact created contact=%s ws=%s discord_uid=%s",
                contact_id,
                ws_id,
                discord_user_id,
            )
            return contact_id
        logger.warning(
            "ensure_discord_contact: create returned no id ws=%s discord_uid=%s",
            ws_id,
            discord_user_id,
        )
        return None
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning(
            "ensure_discord_contact GQL error ws=%s uid=%s: %s %s",
            ws_id,
            discord_user_id,
            type(e).__name__,
            e,
        )
        return None
    except (TypeError, KeyError, ValueError) as e:
        logger.warning(
            "ensure_discord_contact parse error ws=%s uid=%s: %s %s",
            ws_id,
            discord_user_id,
            type(e).__name__,
            e,
        )
        return None


async def application_apply_decision(
    fclient: ckit_client.FlexusClient,
    application_id: str,
    app_status: str,
    app_decision: str,
    details: Optional[dict] = None,
) -> bool:
    """
    Update an application's status, decision, and optional details. Returns True on success.

    app_status values: PENDING / REVIEWING / DECIDED / CLOSED.
    app_decision values: APPROVED / REJECTED / WAITLISTED / "" (empty clears decision).
    details dict is serialised to JSON and stored in application_details.
    """
    try:
        details_json = json.dumps(details) if details is not None else None
        async with (await fclient.use_http()) as http:
            r = await http.execute(
                _GQL_APPLICATION_UPDATE,
                variable_values={
                    "application_id": application_id,
                    "status": app_status,
                    "decision": app_decision if app_decision else None,
                    "details": details_json,
                },
            )
        row = r.get("application_update") if isinstance(r, dict) else None
        if not isinstance(row, dict) or not row.get("application_id"):
            logger.warning(
                "application_apply_decision: no application_id in response app=%s status=%s",
                application_id,
                app_status,
            )
            return False
        logger.info(
            "application_apply_decision app=%s status=%s decision=%s",
            application_id,
            app_status,
            app_decision,
        )
        return True
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning(
            "application_apply_decision GQL error app=%s: %s %s",
            application_id,
            type(e).__name__,
            e,
        )
        return False
    except (TypeError, KeyError, ValueError) as e:
        logger.warning(
            "application_apply_decision parse error app=%s: %s %s",
            application_id,
            type(e).__name__,
            e,
        )
        return False
