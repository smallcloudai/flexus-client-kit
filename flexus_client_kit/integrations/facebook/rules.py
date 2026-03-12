from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.rules")

RULE_FIELDS = "id,name,status,evaluation_spec,execution_spec,schedule_spec,created_time,updated_time"


async def list_ad_rules(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Ad Rules for {ad_account_id}:\n  Pause on low CTR (ID: 111222) — ENABLED\n  Scale budget on ROAS (ID: 222333) — ENABLED\n"
    data = await client.request(
        "GET", f"{ad_account_id}/adrules_library",
        params={"fields": RULE_FIELDS, "limit": 50},
    )
    rules = data.get("data", [])
    if not rules:
        return f"No ad rules found for {ad_account_id}"
    result = f"Ad Rules for {ad_account_id} ({len(rules)} total):\n\n"
    for rule in rules:
        result += f"  **{rule.get('name', 'Unnamed')}** (ID: {rule['id']})\n"
        result += f"     Status: {rule.get('status', 'N/A')}\n"
        exec_spec = rule.get("execution_spec", {})
        if exec_spec.get("execution_type"):
            result += f"     Action: {exec_spec['execution_type']}\n"
        result += "\n"
    return result


async def create_ad_rule(
    client: "FacebookAdsClient",
    ad_account_id: str,
    name: str,
    evaluation_spec: Dict[str, Any],
    execution_spec: Dict[str, Any],
    schedule_spec: Optional[Dict[str, Any]] = None,
    status: str = "ENABLED",
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not name:
        return "ERROR: name is required"
    if not evaluation_spec:
        return "ERROR: evaluation_spec is required (defines conditions to check)"
    if not execution_spec:
        return "ERROR: execution_spec is required (defines action to take)"
    if client.is_test_mode:
        return f"Ad rule created:\n  Name: {name}\n  ID: mock_rule_123\n  Status: {status}\n"
    data: Dict[str, Any] = {
        "name": name,
        "evaluation_spec": evaluation_spec,
        "execution_spec": execution_spec,
        "status": status,
    }
    if schedule_spec:
        data["schedule_spec"] = schedule_spec
    result = await client.request("POST", f"{ad_account_id}/adrules_library", data=data)
    rule_id = result.get("id")
    if not rule_id:
        return f"Failed to create ad rule. Response: {result}"
    return f"Ad rule created:\n  Name: {name}\n  ID: {rule_id}\n  Status: {status}\n"


async def update_ad_rule(
    client: "FacebookAdsClient",
    rule_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    if not rule_id:
        return "ERROR: rule_id is required"
    if not any([name, status]):
        return "ERROR: At least one field to update is required (name, status)"
    valid_statuses = ["ENABLED", "DISABLED", "DELETED"]
    if status and status not in valid_statuses:
        return f"ERROR: status must be one of: {', '.join(valid_statuses)}"
    if client.is_test_mode:
        updates = []
        if name:
            updates.append(f"name -> {name}")
        if status:
            updates.append(f"status -> {status}")
        return f"Ad rule {rule_id} updated:\n" + "\n".join(f"  - {u}" for u in updates)
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    result = await client.request("POST", rule_id, data=data)
    if result.get("success"):
        return f"Ad rule {rule_id} updated successfully."
    return f"Failed to update ad rule. Response: {result}"


async def delete_ad_rule(
    client: "FacebookAdsClient",
    rule_id: str,
) -> str:
    if not rule_id:
        return "ERROR: rule_id is required"
    if client.is_test_mode:
        return f"Ad rule {rule_id} deleted successfully."
    result = await client.request("DELETE", rule_id)
    if result.get("success"):
        return f"Ad rule {rule_id} deleted successfully."
    return f"Failed to delete ad rule. Response: {result}"


async def execute_ad_rule(
    client: "FacebookAdsClient",
    rule_id: str,
) -> str:
    if not rule_id:
        return "ERROR: rule_id is required"
    if client.is_test_mode:
        return f"Ad rule {rule_id} executed successfully. Actions applied to matching objects."
    result = await client.request("POST", f"{rule_id}/execute", data={})
    if result.get("success"):
        return f"Ad rule {rule_id} executed successfully. Actions applied to matching objects."
    return f"Failed to execute ad rule. Response: {result}"
