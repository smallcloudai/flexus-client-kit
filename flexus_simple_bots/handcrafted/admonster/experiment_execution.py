import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_external_auth
from flexus_client_kit.core import ckit_ask_model
from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_kanban
from flexus_client_kit.integrations.providers.request_response import fi_pdoc
from flexus_client_kit.integrations.providers.request_response.facebook.fi_facebook import IntegrationFacebook
from flexus_client_kit.integrations.providers.request_response.facebook import campaigns as fb_campaigns
from flexus_client_kit.integrations.providers.request_response.facebook import adsets as fb_adsets


logger = logging.getLogger("experiment_execution")


LAUNCH_EXPERIMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="launch_experiment",
    description="Launch Meta campaigns from Owl Strategist tactics document. Creates campaigns in PAUSED status for review.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {
                "type": "string",
                "description": "Experiment ID from tactics path, e.g. hyp001-meta-ads-test",
                "order": 1
            },
            "activate_immediately": {
                "type": "boolean",
                "description": "If true, activate campaigns immediately instead of PAUSED (default: false)",
                "order": 2
            },
        },
        "required": ["experiment_id"]
    },
)

LAUNCH_EXPERIMENT_HELP = """
launch_experiment(experiment_id="dental-samples/private-practice/experiments/meta-ads-test")
    Read tactics-campaigns from /gtm/discovery/{experiment_id}/tactics-campaigns
    Create Facebook campaigns, adsets based on tactics_campaigns.campaigns
    Save runtime state to /gtm/discovery/{experiment_id}/meta-runtime
    Returns summary of created campaigns

launch_experiment(experiment_id="dental-samples/private-practice/experiments/meta-ads-test", activate_immediately=true)
    Same as above but starts campaigns in ACTIVE status
"""


@dataclass
class ExperimentTracking:
    """In-memory tracking for active experiment."""
    experiment_id: str
    task_id: str
    thread_id: str
    start_ts: float
    facebook_campaign_ids: List[str] = field(default_factory=list)
    facebook_adset_ids: List[str] = field(default_factory=list)


class IntegrationExperimentExecution:
    """
    Handles marketing experiment execution lifecycle:
    - Launching campaigns from Owl Strategist tactics
    - Hourly monitoring and optimization based on metrics rules
    - Notifying user about actions taken
    """

    def __init__(
        self,
        pdoc_integration: fi_pdoc.IntegrationPdoc,
        fclient: ckit_client.FlexusClient,
        facebook_integration: Optional[IntegrationFacebook],
    ):
        self.pdoc_integration = pdoc_integration
        self.fclient = fclient
        self.facebook_integration = facebook_integration
        # experiment_id -> ExperimentTracking
        self.tracked_experiments: Dict[str, ExperimentTracking] = {}

    def track_experiment_task(self, task: ckit_kanban.FPersonaKanbanTaskOutput) -> None:
        """
        Called from on_updated_task to track experiments.
        Extracts experiment_id from ktask_details and adds to tracking.
        """
        if not task.ktask_details:
            return
        details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details or "{}")
        experiment_id = details.get("experiment_id")
        if not experiment_id:
            return
        # Only track active tasks (not done)
        if task.ktask_done_ts != 0:
            if experiment_id in self.tracked_experiments:
                del self.tracked_experiments[experiment_id]
                logger.info(f"Stopped tracking experiment {experiment_id} (task done)")
            return
        if experiment_id not in self.tracked_experiments:
            self.tracked_experiments[experiment_id] = ExperimentTracking(
                experiment_id=experiment_id,
                task_id=task.ktask_id,
                thread_id=task.ktask_inprogress_ft_id or "",
                start_ts=details.get("start_ts", time.time()),
                facebook_campaign_ids=details.get("facebook_campaign_ids", []),
                facebook_adset_ids=details.get("facebook_adset_ids", []),
            )
            logger.info(f"Tracking experiment {experiment_id} for task {task.ktask_id}")

    async def launch_experiment(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        args: Dict[str, Any],
    ) -> str:
        """
        Launch Meta campaigns from tactics document.
        Creates campaigns and adsets in Facebook, saves runtime state to pdoc.
        """
        experiment_id = args.get("experiment_id", "")
        activate_immediately = args.get("activate_immediately", False)
        if not experiment_id:
            return f"ERROR: experiment_id required.\n\n{LAUNCH_EXPERIMENT_HELP}"
        if not self.facebook_integration:
            return "ERROR: Facebook integration not available."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(self.pdoc_integration.rcx, toolcall.fcall_ft_id)

        # Read ad_account_id from policy document
        try:
            config_doc = await self.pdoc_integration.pdoc_cat("/company/ad-ops-config", fuser_id)
            ad_account_id = config_doc.pdoc_content.get("facebook_ad_account_id", "")
        except Exception as e:
            return f"ERROR: Could not read /company/ad-ops-config: {e}"
        if not ad_account_id:
            return "ERROR: facebook_ad_account_id not set in /company/ad-ops-config"
        self.facebook_integration.client.ad_account_id = ad_account_id

        # 1. Read tactics-campaigns document (new format: 4 separate docs)
        tactics_path = f"/gtm/discovery/{experiment_id}/tactics-campaigns"
        try:
            tactics_doc = await self.pdoc_integration.pdoc_cat(tactics_path, fuser_id)
            tactics_raw = tactics_doc.pdoc_content
            # Extract from wrapper: {"tactics_campaigns": {"meta": {...}, "campaigns": [...]}}
            tactics = tactics_raw.get("tactics_campaigns", tactics_raw) if isinstance(tactics_raw, dict) else {}
        except Exception as e:
            return f"ERROR: Could not read tactics at {tactics_path}: {e}"
        if not tactics:
            return f"ERROR: Empty tactics document at {tactics_path}"

        # 2. Extract campaigns from tactics (only Meta channel)
        # Note: metrics doc is loaded during monitoring (_check_single_experiment), not at launch
        campaigns_spec = tactics.get("campaigns", [])
        meta_campaigns = [c for c in campaigns_spec if c.get("channel") == "meta"]
        if not meta_campaigns:
            return f"ERROR: No Meta campaigns found in tactics. Available channels: {set(c.get('channel') for c in campaigns_spec)}"

        # 4. Create Facebook campaigns and adsets
        ad_account_id = self.facebook_integration.client.ad_account_id
        if not ad_account_id:
            return "ERROR: Facebook ad_account_id not configured in setup"
        created_campaigns = []
        created_adsets = []
        errors = []
        initial_status = "ACTIVE" if activate_immediately else "PAUSED"
        for camp_spec in meta_campaigns:
            campaign_id_local = camp_spec.get("campaign_id", "unknown")
            campaign_name = f"{experiment_id}_{campaign_id_local}"
            daily_budget_dollars = camp_spec.get("daily_budget", 10)
            # Convert dollars to cents for Facebook API
            daily_budget_cents = int(daily_budget_dollars * 100)
            objective = self._map_objective(camp_spec.get("objective", "traffic"))

            # Create campaign
            try:
                campaign_result = await fb_campaigns.create_campaign(
                    client=self.facebook_integration.client,
                    ad_account_id=ad_account_id,
                    name=campaign_name,
                    objective=objective,
                    status=initial_status,
                    daily_budget=daily_budget_cents,
                )
                # Parse campaign ID from result
                fb_campaign_id = self._extract_id_from_result(campaign_result, "Campaign")
                if fb_campaign_id:
                    created_campaigns.append({
                        "local_id": campaign_id_local,
                        "facebook_id": fb_campaign_id,
                        "name": campaign_name,
                        "daily_budget": daily_budget_cents,
                        "status": initial_status,
                    })
                else:
                    errors.append(f"Campaign {campaign_id_local}: {campaign_result}")
                    continue
            except Exception as e:
                errors.append(f"Campaign {campaign_id_local}: {e}")
                continue

            # Create adsets for this campaign
            for adset_spec in camp_spec.get("adsets", []):
                adset_id_local = adset_spec.get("adset_id", "unknown")
                adset_name = f"{experiment_id}_{adset_id_local}"
                audience = adset_spec.get("audience", {})
                targeting = self._build_targeting(audience)
                optimization_goal = self._map_optimization_goal(adset_spec.get("optimization_goal", "landing_page_views"))
                try:
                    adset_result = await fb_adsets.create_adset(
                        client=self.facebook_integration.client,
                        ad_account_id=ad_account_id,
                        campaign_id=fb_campaign_id,
                        name=adset_name,
                        targeting=targeting,
                        optimization_goal=optimization_goal,
                        status=initial_status,
                    )
                    fb_adset_id = self._extract_id_from_result(adset_result, "Ad Set")
                    if fb_adset_id:
                        created_adsets.append({
                            "local_id": adset_id_local,
                            "facebook_id": fb_adset_id,
                            "campaign_local_id": campaign_id_local,
                            "name": adset_name,
                            "status": initial_status,
                        })
                    else:
                        errors.append(f"Adset {adset_id_local}: {adset_result}")
                except Exception as e:
                    errors.append(f"Adset {adset_id_local}: {e}")

        # 5. Save runtime state to pdoc
        # Wrapped in meta-runtime key with meta object for microfrontend form detection
        runtime_path = f"/gtm/discovery/{experiment_id}/meta-runtime"
        runtime_inner = {
            "meta": {
                "experiment_id": experiment_id,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "microfrontend": "admonster",
            },
            "experiment_status": "active" if activate_immediately else "paused",
            "start_ts": time.time(),
            "current_day": 0,
            "campaigns": {c["local_id"]: c for c in created_campaigns},
            "adsets": {a["local_id"]: a for a in created_adsets},
            "actions_log": [{
                "ts": time.time(),
                "action": "launch",
                "type": "launch",
                "details": f"Created {len(created_campaigns)} campaigns, {len(created_adsets)} adsets",
            }],
            "last_check_ts": time.time(),
            "metrics_history": [],
        }
        runtime_doc = {"meta_runtime": runtime_inner}
        try:
            await self.pdoc_integration.pdoc_overwrite(runtime_path, json.dumps(runtime_doc, indent=2), fuser_id)
        except Exception as e:
            errors.append(f"Failed to save runtime: {e}")

        # 6. Update task details with experiment tracking info
        if toolcall.fcall_ft_id:
            try:
                tasks = await ckit_kanban.get_tasks_by_thread(self.fclient, toolcall.fcall_ft_id)
                for task in tasks:
                    task_details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details or "{}")
                    task_details["experiment_id"] = experiment_id
                    task_details["start_ts"] = runtime_inner["start_ts"]
                    task_details["facebook_campaign_ids"] = [c["facebook_id"] for c in created_campaigns]
                    task_details["facebook_adset_ids"] = [a["facebook_id"] for a in created_adsets]
                    await ckit_kanban.bot_kanban_update_details(self.fclient, task.ktask_id, task_details)
                    logger.info(f"Updated task {task.ktask_id} with experiment {experiment_id}")
            except Exception as e:
                logger.warning(f"Failed to update task details: {e}")

        # 7. Format result
        result = f"Experiment {experiment_id} launched!\n\n"
        result += f"Runtime state: {runtime_path}\n"
        result += f"Status: {initial_status}\n\n"
        if created_campaigns:
            result += f"Created {len(created_campaigns)} campaign(s):\n"
            for c in created_campaigns:
                result += f"  - {c['name']} (FB ID: {c['facebook_id']}, ${c['daily_budget']/100:.2f}/day)\n"
        if created_adsets:
            result += f"\nCreated {len(created_adsets)} adset(s):\n"
            for a in created_adsets:
                result += f"  - {a['name']} (FB ID: {a['facebook_id']})\n"
        if errors:
            result += f"\nErrors ({len(errors)}):\n"
            for e in errors:
                result += f"  - {e}\n"
        if not activate_immediately:
            result += "\nCampaigns are PAUSED. Review and activate with:\n"
            result += 'facebook(op="update_campaign", args={"campaign_id": "...", "status": "ACTIVE"})'
        return result

    async def update_active_experiments(self) -> None:
        """
        Called hourly from main loop.
        For each tracked experiment:
        - Fetches metrics from Facebook
        - Applies stop/accelerate rules from metrics doc
        - Executes actions (pause/unpause/budget changes)
        - Updates runtime doc and notifies user
        """
        if not self.tracked_experiments:
            return
        if not self.facebook_integration:
            logger.warning("Cannot update experiments: Facebook integration not configured")
            return
        for experiment_id, tracking in list(self.tracked_experiments.items()):
            try:
                await self._check_single_experiment(experiment_id, tracking)
            except Exception as e:
                logger.error(f"Error checking experiment {experiment_id}: {e}", exc_info=e)

    async def _check_single_experiment(self, experiment_id: str, tracking: ExperimentTracking) -> None:
        """Check and optimize a single experiment."""
        # Use bot's fuser_id for pdoc access
        fuser_id = self.pdoc_integration.rcx.persona.persona_id

        # 1. Load runtime doc (wrapped in meta-runtime key)
        runtime_path = f"/gtm/discovery/{experiment_id}/meta-runtime"
        try:
            runtime_doc = await self.pdoc_integration.pdoc_cat(runtime_path, fuser_id)
            raw_content = runtime_doc.pdoc_content
            # Extract inner runtime from meta-runtime wrapper
            runtime = raw_content.get("meta_runtime", raw_content) if isinstance(raw_content, dict) else {}
        except Exception as e:
            logger.warning(f"Could not load runtime for {experiment_id}: {e}")
            return
        if not runtime or runtime.get("experiment_status") == "completed":
            return

        # 2. Load metrics doc (for rules)
        metrics_path = f"/gtm/discovery/{experiment_id}/metrics"
        metrics = None
        try:
            metrics_doc = await self.pdoc_integration.pdoc_cat(metrics_path, fuser_id)
            metrics = metrics_doc.pdoc_content
        except Exception:
            pass

        # 3. Load tactics-tracking doc (for iteration_guide)
        tactics_tracking_path = f"/gtm/discovery/{experiment_id}/tactics-tracking"
        tactics_tracking = None
        try:
            tactics_doc = await self.pdoc_integration.pdoc_cat(tactics_tracking_path, fuser_id)
            tactics_raw = tactics_doc.pdoc_content
            # Extract from wrapper: {"tactics_tracking": {"meta": {...}, "iteration_guide": {...}}}
            tactics_tracking = tactics_raw.get("tactics_tracking", tactics_raw) if isinstance(tactics_raw, dict) else {}
        except Exception:
            pass

        # 4. Calculate current day
        start_ts = runtime.get("start_ts", time.time())
        current_day = int((time.time() - start_ts) / 86400) + 1
        runtime["current_day"] = current_day

        # 5. Fetch insights for each campaign
        actions_taken = []
        metrics_summary = {}
        campaigns = runtime.get("campaigns", {})
        for local_id, camp_info in campaigns.items():
            fb_id = camp_info.get("facebook_id")
            if not fb_id:
                continue
            # Get insights from Facebook
            try:
                insights_result = await fb_campaigns.get_insights(
                    self.facebook_integration.client,
                    fb_id,
                    days=current_day,
                )
                camp_metrics = self._parse_insights(insights_result)
                metrics_summary[local_id] = camp_metrics
                camp_info["latest_metrics"] = camp_metrics
            except Exception as e:
                logger.warning(f"Could not get insights for campaign {fb_id}: {e}")
                continue

            # 6. Apply rules
            if metrics:
                rule_actions = await self._apply_rules(
                    camp_info,
                    camp_metrics,
                    metrics.get("stop_rules", []),
                    metrics.get("accelerate_rules", []),
                    current_day,
                )
                actions_taken.extend(rule_actions)

        # 7. Apply iteration_guide rules (from tactics-tracking doc)
        if tactics_tracking:
            iteration_guide = tactics_tracking.get("iteration_guide", {})
            day_key = self._get_day_key(current_day)
            guide_text = iteration_guide.get(day_key, "")
            if guide_text:
                # Log that we're in this phase (actual parsing of guide text for actions could be added)
                actions_taken.append({
                    "type": "iteration_phase",
                    "day_key": day_key,
                    "guide": guide_text[:100] + "..." if len(guide_text) > 100 else guide_text,
                })

        # 8. Update runtime doc
        runtime["last_check_ts"] = time.time()
        if actions_taken:
            for action in actions_taken:
                action["ts"] = time.time()
            runtime.setdefault("actions_log", []).extend(actions_taken)
        # Add to metrics history
        runtime.setdefault("metrics_history", []).append({
            "day": current_day,
            "ts": time.time(),
            "metrics": metrics_summary,
        })
        # Keep only last 30 days of history
        if len(runtime["metrics_history"]) > 30:
            runtime["metrics_history"] = runtime["metrics_history"][-30:]
        # Wrap in meta-runtime for microfrontend compatibility
        runtime_wrapped = {"meta_runtime": runtime}
        try:
            await self.pdoc_integration.pdoc_overwrite(runtime_path, json.dumps(runtime_wrapped, indent=2), fuser_id)
        except Exception as e:
            logger.warning(f"Failed to update runtime for {experiment_id}: {e}")

        # 9. Notify user in thread
        if tracking.thread_id and (actions_taken or current_day % 7 == 0):
            await self._notify_user(tracking, current_day, metrics_summary, actions_taken)

    async def _apply_rules(
        self,
        camp_info: Dict[str, Any],
        camp_metrics: Dict[str, float],
        stop_rules: List[Dict[str, Any]],
        accelerate_rules: List[Dict[str, Any]],
        current_day: int,
    ) -> List[Dict[str, Any]]:
        """Apply stop and accelerate rules, execute actions, return list of actions taken."""
        actions = []
        fb_campaign_id = camp_info.get("facebook_id")
        if not fb_campaign_id:
            return actions

        # Apply stop rules
        for rule in stop_rules:
            metric_name = rule.get("metric", "")
            operator = rule.get("operator", "<")
            threshold = rule.get("threshold", 0)
            min_events = rule.get("min_events", 0)
            action_name = rule.get("action", "pause")
            metric_value = camp_metrics.get(metric_name, 0)
            # Check min_events (use impressions as proxy for events)
            events = camp_metrics.get("impressions", 0)
            if events < min_events:
                continue
            triggered = False
            if operator == "<" and metric_value < threshold:
                triggered = True
            elif operator == ">" and metric_value > threshold:
                triggered = True
            elif operator == "<=" and metric_value <= threshold:
                triggered = True
            elif operator == ">=" and metric_value >= threshold:
                triggered = True
            if triggered:
                # Execute pause action
                if "pause" in action_name.lower() and camp_info.get("status") != "PAUSED":
                    try:
                        await fb_campaigns.update_campaign(
                            self.facebook_integration.client,
                            fb_campaign_id,
                            status="PAUSED",
                        )
                        camp_info["status"] = "PAUSED"
                        actions.append({
                            "type": "stop_rule",
                            "action": action_name,
                            "campaign": camp_info.get("local_id", fb_campaign_id),
                            "reason": f"{metric_name} {operator} {threshold} (value: {metric_value:.4f})",
                        })
                        logger.info(f"Paused campaign {fb_campaign_id} due to {metric_name} {operator} {threshold}")
                    except Exception as e:
                        logger.warning(f"Failed to pause campaign {fb_campaign_id}: {e}")

        # Apply accelerate rules
        for rule in accelerate_rules:
            metric_name = rule.get("metric", "")
            operator = rule.get("operator", ">=")
            threshold = rule.get("threshold", 0)
            min_conversions = rule.get("min_conversions", 0)
            action_name = rule.get("action", "double_budget")
            metric_value = camp_metrics.get(metric_name, 0)
            # For accelerate, check conversions (approximate with clicks for now)
            conversions = camp_metrics.get("clicks", 0)
            if conversions < min_conversions:
                continue
            triggered = False
            if operator == ">=" and metric_value >= threshold:
                triggered = True
            elif operator == ">" and metric_value > threshold:
                triggered = True
            if triggered and "double" in action_name.lower():
                # Double the budget
                current_budget = camp_info.get("daily_budget", 0)
                if current_budget > 0:
                    new_budget = current_budget * 2
                    try:
                        await fb_campaigns.update_campaign(
                            self.facebook_integration.client,
                            fb_campaign_id,
                            daily_budget=new_budget,
                        )
                        camp_info["daily_budget"] = new_budget
                        actions.append({
                            "type": "accelerate_rule",
                            "action": action_name,
                            "campaign": camp_info.get("local_id", fb_campaign_id),
                            "reason": f"{metric_name} {operator} {threshold} (value: {metric_value:.4f})",
                            "budget_change": f"${current_budget/100:.2f} -> ${new_budget/100:.2f}",
                        })
                        logger.info(f"Doubled budget for {fb_campaign_id}: ${current_budget/100:.2f} -> ${new_budget/100:.2f}")
                    except Exception as e:
                        logger.warning(f"Failed to update budget for {fb_campaign_id}: {e}")
        return actions

    async def _notify_user(
        self,
        tracking: ExperimentTracking,
        current_day: int,
        metrics_summary: Dict[str, Dict[str, float]],
        actions: List[Dict[str, Any]],
    ) -> None:
        """Send notification to the task thread about experiment status."""
        message = f"Experiment {tracking.experiment_id} - Day {current_day} check\n\n"
        # Metrics summary
        if metrics_summary:
            message += "Metrics:\n"
            for camp_id, m in metrics_summary.items():
                message += f"  {camp_id}: {m.get('impressions', 0):.0f} imps, {m.get('clicks', 0):.0f} clicks"
                if m.get("ctr"):
                    message += f", CTR {m['ctr']:.2f}%"
                if m.get("spend"):
                    message += f", ${m['spend']:.2f} spent"
                message += "\n"
        # Actions taken
        if actions:
            message += "\nActions taken:\n"
            for a in actions:
                if a["type"] == "stop_rule":
                    message += f"  PAUSED {a['campaign']}: {a['reason']}\n"
                elif a["type"] == "accelerate_rule":
                    message += f"  ACCELERATED {a['campaign']}: {a.get('budget_change', a['reason'])}\n"
                elif a["type"] == "iteration_phase":
                    message += f"  Phase {a['day_key']}: {a['guide']}\n"
        else:
            message += "\nNo actions needed.\n"
        try:
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_add_user_message(
                http=http,
                ft_id=tracking.thread_id,
                content=message,
                who_is_asking="experiment_monitor",
                ftm_alt=100,
            )
            logger.info(f"Sent notification for experiment {tracking.experiment_id}")
        except Exception as e:
            logger.warning(f"Failed to send notification for {tracking.experiment_id}: {e}")

    def _map_objective(self, tactics_objective: str) -> str:
        """Map tactics objective to Facebook objective."""
        mapping = {
            "traffic": "OUTCOME_TRAFFIC",
            "engagement": "OUTCOME_ENGAGEMENT",
            "awareness": "OUTCOME_AWARENESS",
            "leads": "OUTCOME_LEADS",
            "sales": "OUTCOME_SALES",
            "conversions": "OUTCOME_SALES",
            "app_promotion": "OUTCOME_APP_PROMOTION",
        }
        return mapping.get(tactics_objective.lower(), "OUTCOME_TRAFFIC")

    def _map_optimization_goal(self, tactics_goal: str) -> str:
        """Map tactics optimization goal to Facebook optimization goal."""
        mapping = {
            "landing_page_views": "LANDING_PAGE_VIEWS",
            "link_clicks": "LINK_CLICKS",
            "impressions": "IMPRESSIONS",
            "reach": "REACH",
            "conversions": "OFFSITE_CONVERSIONS",
            "website_clicks": "LINK_CLICKS",
        }
        return mapping.get(tactics_goal.lower(), "LINK_CLICKS")

    # Common country name/code mappings for Facebook API
    COUNTRY_CODE_MAP = {
        "UK": "GB", "United Kingdom": "GB", "Britain": "GB",
        "USA": "US", "United States": "US", "America": "US",
        "Canada": "CA", "Deutschland": "DE", "Germany": "DE",
    }

    def _normalize_country_codes(self, countries: List[str]) -> List[str]:
        """Convert country names/codes to ISO 3166-1 alpha-2 codes."""
        return [self.COUNTRY_CODE_MAP.get(c, c) for c in countries]

    def _build_targeting(self, audience: Dict[str, Any]) -> Dict[str, Any]:
        """Build Facebook targeting spec from tactics audience."""
        targeting: Dict[str, Any] = {}
        # Geo locations — normalize country codes
        countries = audience.get("countries", [])
        if countries:
            normalized = self._normalize_country_codes(countries)
            targeting["geo_locations"] = {"countries": normalized}
        # Age range
        age_range = audience.get("age_range", [])
        if age_range and len(age_range) >= 2:
            targeting["age_min"] = age_range[0]
            targeting["age_max"] = age_range[1]
        # Interests (simplified - Facebook interests API is complex)
        interests = audience.get("interests", [])
        if interests:
            # Note: Real implementation would need to look up interest IDs
            # For now, just log that interests were specified
            logger.info(f"Interests specified but not mapped: {interests}")
        return targeting

    def _extract_id_from_result(self, result: str, entity_type: str) -> Optional[str]:
        """Extract ID from Facebook API result string."""
        # Results look like "Campaign created: Name (ID: 123456789)"
        # or "Ad Set created successfully!\nID: 123456789"
        if "ERROR" in result:
            return None
        import re
        # Try "ID: xxx" pattern
        match = re.search(r'ID:\s*(\d+|mock_\w+)', result)
        if match:
            return match.group(1)
        return None

    def _parse_insights(self, insights_result: str) -> Dict[str, float]:
        """Parse Facebook insights result string into metrics dict."""
        metrics = {
            "impressions": 0,
            "clicks": 0,
            "spend": 0,
            "ctr": 0,
            "cpc": 0,
        }
        if "No insights" in insights_result or "ERROR" in insights_result:
            return metrics
        import re
        # Parse "Impressions: 125,000" format
        imp_match = re.search(r'Impressions:\s*([\d,]+)', insights_result)
        if imp_match:
            metrics["impressions"] = float(imp_match.group(1).replace(",", ""))
        clicks_match = re.search(r'Clicks:\s*([\d,]+)', insights_result)
        if clicks_match:
            metrics["clicks"] = float(clicks_match.group(1).replace(",", ""))
        spend_match = re.search(r'Spend:\s*\$([\d,.]+)', insights_result)
        if spend_match:
            metrics["spend"] = float(spend_match.group(1).replace(",", ""))
        ctr_match = re.search(r'CTR:\s*([\d.]+)%', insights_result)
        if ctr_match:
            metrics["ctr"] = float(ctr_match.group(1))
        cpc_match = re.search(r'CPC:\s*\$([\d.]+)', insights_result)
        if cpc_match:
            metrics["cpc"] = float(cpc_match.group(1))
        return metrics

    def _get_day_key(self, current_day: int) -> str:
        """Get iteration_guide key for current day."""
        if current_day <= 3:
            return "day_1_3"
        elif current_day <= 7:
            return "day_4_7"
        elif current_day <= 14:
            return "day_8_14"
        else:
            return "day_15_30"

