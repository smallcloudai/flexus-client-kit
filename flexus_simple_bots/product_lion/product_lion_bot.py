import asyncio
import logging
import json
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.product_lion import product_lion_install, product_lion_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_product_lion")


BOT_NAME = "product_lion"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


FIRST_PRINCIPLES_CANVAS_TOOL = ckit_cloudtool.CloudTool(
    name="create_first_principles_canvas",
    description="**USE THIS TOOL** to create First Principles Canvas. Do NOT write Canvas JSON manually in chat. Call this tool immediately when user brings raw idea. Decomposes raw idea into fundamental truths, constraints, and testable assumptions. Path: /customer-research/{idea-name}/canvas",
    parameters={
        "type": "object",
        "properties": {
            "idea_name": {
                "type": "string",
                "description": "Idea name in kebab-case (e.g. 'slack-microwave')"
            }
        },
        "required": ["idea_name"]
    }
)

HYPOTHESIS_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_hypothesis",
    description="Create skeleton hypothesis file in pdoc. Hypotheses explore specific customer segments or approaches for an idea. Path format: /customer-research/{idea-name}-hypotheses/{hypothesis-name}",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write hypothesis template, such as '/customer-research/unicorn-horn-car-hypotheses/social-media-influencers'"
            },
        },
        "required": ["path"],
    },
)

IDEA_FRAMING_SHEET_TOOL = ckit_cloudtool.CloudTool(
    name="create_idea_framing_sheet",
    description="**USE THIS TOOL** to create Idea Framing Sheet. Do NOT write Sheet JSON manually in chat. Creates structured validated summary of an idea synthesized from Canvas. Path: /customer-research/{idea-name}/sheet",
    parameters={
        "type": "object",
        "properties": {
            "idea_name": {
                "type": "string",
                "description": "Idea name in kebab-case"
            },
            "sheet_data": {
                "type": "object",
                "description": "Sheet content (optional, for updates). If empty, creates blank template."
            }
        },
        "required": ["idea_name"]
    }
)

VALIDATE_ARTIFACT_TOOL = ckit_cloudtool.CloudTool(
    name="validate_artifact",
    description="Validate artifact (Canvas, Sheet, or Problem Hypothesis List) against quality criteria. Returns status (pass/pass-with-warnings/fail) with issues and suggestions.",
    parameters={
        "type": "object",
        "properties": {
            "artifact_path": {
                "type": "string",
                "description": "Path to artifact (e.g. /customer-research/slack-microwave/sheet)"
            },
            "artifact_type": {
                "type": "string",
                "enum": ["canvas", "sheet", "problem-hypothesis-list"],
                "description": "Type of artifact to validate"
            }
        },
        "required": ["artifact_path", "artifact_type"]
    }
)

GENERATE_PROBLEM_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    name="generate_problem_hypotheses",
    description="**USE THIS TOOL** to generate Problem Hypothesis List. Do NOT write hypotheses manually in chat. Extracts core problems and assumptions from Idea Framing Sheet, formulates testable hypotheses. Path: /customer-research/{idea-name}/hypotheses/problem-list",
    parameters={
        "type": "object",
        "properties": {
            "idea_name": {
                "type": "string",
                "description": "Idea name in kebab-case (e.g. 'slack-microwave')"
            },
            "sheet_path": {
                "type": "string",
                "description": "Path to Idea Framing Sheet (optional, defaults to /customer-research/{idea-name}/sheet)"
            }
        },
        "required": ["idea_name"]
    }
)

PRIORITIZE_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    name="prioritize_hypotheses",
    description="Prioritize problem hypotheses using ICE matrix (Impact × Evidence × Feasibility). Scores each hypothesis 0-5 on each criterion, calculates weighted score.",
    parameters={
        "type": "object",
        "properties": {
            "problem_list_path": {
                "type": "string",
                "description": "Path to Problem Hypothesis List (e.g. /customer-research/slack-microwave/hypotheses/problem-list)"
            }
        },
        "required": ["problem_list_path"]
    }
)

TOOLS = [
    FIRST_PRINCIPLES_CANVAS_TOOL,
    IDEA_FRAMING_SHEET_TOOL,
    GENERATE_PROBLEM_HYPOTHESES_TOOL,
    PRIORITIZE_HYPOTHESES_TOOL,
    HYPOTHESIS_TEMPLATE_TOOL,  # Keep for solution hypotheses (A3)
    VALIDATE_ARTIFACT_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def productman_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    from datetime import datetime
    
    setup = ckit_bot_exec.official_setup_mixing_procedure(product_lion_install.product_lion_setup_schema, rcx.persona.persona_setup)

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.located_fgroup_id)
    
    # Helper function to record sanction when user chooses "proceed-as-is"
    async def record_sanction_for_sheet(idea_name: str, warnings: list, user_reasoning: str = "User acknowledged warnings and chose to proceed") -> str:
        """Record sanction metadata when user accepts warnings and proceeds"""
        base_path = f"/customer-research/{idea_name}/sheet"
        
        try:
            # Find latest version
            sheet_content = await pdoc_integration.pdoc_read(base_path, "")
            sheet_data = json.loads(sheet_content)
            
            # Get current version
            current_version = sheet_data.get("meta", {}).get("version", "v0")
            if current_version != "v0":
                path = f"{base_path}-{current_version}"
            else:
                path = base_path
            
            # Add sanction metadata
            if "meta" not in sheet_data:
                sheet_data["meta"] = {}
            
            sheet_data["meta"]["validation_status"] = "proceed-as-is"
            sheet_data["meta"]["sanction"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged_warnings": [f"{w.get('criterion', '?')}: {w.get('description', 'no description')}" for w in warnings],
                "user_reasoning": user_reasoning
            }
            
            # Write updated sheet
            await pdoc_integration.pdoc_write(path, json.dumps(sheet_data, indent=2), "")
            logger.info(f"Recorded sanction for {path}")
            return f"Sanction recorded. Status updated to 'proceed-as-is'. Ready to move forward."
            
        except Exception as e:
            logger.error(f"Failed to record sanction: {e}")
            return f"Error recording sanction: {str(e)}"

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(FIRST_PRINCIPLES_CANVAS_TOOL.name)
    async def toolcall_create_first_principles_canvas(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        idea_name = model_produced_args.get("idea_name", "")
        if not idea_name:
            return "Error: idea_name required"
        
        # Validate kebab-case
        if not all(c.islower() or c.isdigit() or c == "-" for c in idea_name):
            return f"Error: idea_name '{idea_name}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'slack-microwave'"
        
        # Construct path: /customer-research/{idea-name}/canvas
        path = f"/customer-research/{idea_name}/canvas"
        
        # First Principles Canvas structure with 8 fields
        canvas = {
            "fundamental_truth": "",
            "atomic_value": "",
            "constraints": [],
            "current_workarounds": "",
            "minimum_end_to_end_scenario": [],
            "critical_assumptions": [],
            "success_metrics": {
                "metric_name": "",
                "order_of_magnitude": ""
            },
            "one_sentence_statement": "",
            "meta": {
                "created": "",
                "version": "v0"
            }
        }

        await pdoc_integration.pdoc_write(path, json.dumps(canvas, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created First Principles Canvas at {path}")
        return f"Canvas created at {path}\n\nFirst Principles Canvas with 8 fields ready for decomposing raw idea into fundamental truths, constraints, and testable assumptions."

    @rcx.on_tool_call(IDEA_FRAMING_SHEET_TOOL.name)
    async def toolcall_create_idea_framing_sheet(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        idea_name = model_produced_args.get("idea_name", "")
        sheet_data = model_produced_args.get("sheet_data", {})
        
        if not idea_name:
            return "Error: idea_name required"
        
        # Validate kebab-case
        if not all(c.islower() or c.isdigit() or c == "-" for c in idea_name):
            return f"Error: idea_name '{idea_name}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'slack-microwave'"
        
        # Check for existing versions and determine next version
        base_path = f"/customer-research/{idea_name}/sheet"
        version = "v0"
        path = base_path
        
        try:
            # Try to read existing sheet to determine versioning
            existing_content = await pdoc_integration.pdoc_read(base_path, toolcall.fcall_ft_id)
            existing_data = json.loads(existing_content)
            
            # If sheet exists, increment version
            if "meta" in existing_data and "version" in existing_data["meta"]:
                current_version = existing_data["meta"]["version"]
                version_num = int(current_version.replace("v", ""))
                version = f"v{version_num + 1}"
                path = f"{base_path}-{version}"
            else:
                # Old sheet without version, make it v1
                version = "v1"
                path = f"{base_path}-{version}"
        except:
            # No existing sheet, use v0
            pass
        
        # If sheet_data provided, use it; otherwise create template
        if not sheet_data:
            sheet_data = {
                "title": "",
                "one_sentence_pitch": "",
                "target_segment": {
                    "who": "",
                    "characteristics": [],
                    "size_estimate": ""
                },
                "core_problem": {
                    "description": "",
                    "current_impact": "",
                    "frequency": ""
                },
                "value_proposition": {
                    "atomic_value": "",
                    "differentiation": ""
                },
                "key_assumptions": [],
                "constraints": [],
                "why_now": "",
                "meta": {
                    "version": version,
                    "validation_status": "pending",
                    "created": datetime.utcnow().isoformat()
                }
            }
        else:
            # Ensure meta.version is set
            if "meta" not in sheet_data:
                sheet_data["meta"] = {}
            sheet_data["meta"]["version"] = version
            sheet_data["meta"]["created"] = datetime.utcnow().isoformat()
        
        await pdoc_integration.pdoc_write(path, json.dumps(sheet_data, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created Idea Framing Sheet at {path} ({version})")
        return f"Sheet created at {path} ({version})\n\nIdea Framing Sheet with structured validated summary ready (title, pitch, target segment, problem, value prop, assumptions, constraints)."

    @rcx.on_tool_call(GENERATE_PROBLEM_HYPOTHESES_TOOL.name)
    async def toolcall_generate_problem_hypotheses(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        idea_name = model_produced_args.get("idea_name", "")
        sheet_path = model_produced_args.get("sheet_path", f"/customer-research/{idea_name}/sheet")
        
        if not idea_name:
            return "Error: idea_name required"
        
        # Validate kebab-case
        if not all(c.islower() or c.isdigit() or c == "-" for c in idea_name):
            return f"Error: idea_name '{idea_name}' must use kebab-case"
        
        # Read Idea Framing Sheet
        try:
            sheet_content = await pdoc_integration.pdoc_read(sheet_path, toolcall.fcall_ft_id)
            sheet_data = json.loads(sheet_content)
        except Exception as e:
            return f"Error reading Idea Framing Sheet: {str(e)}"
        
        # Extract relevant fields
        target_segment = sheet_data.get("target_segment", {})
        core_problem = sheet_data.get("core_problem", {})
        key_assumptions = sheet_data.get("key_assumptions", [])
        constraints = sheet_data.get("constraints", [])
        
        # Construct generation prompt
        generation_prompt = f"""Generate 3-5 problem hypotheses from this Idea Framing Sheet.

Target Segment:
{json.dumps(target_segment, indent=2)}

Core Problem:
{json.dumps(core_problem, indent=2)}

Key Assumptions:
{json.dumps(key_assumptions, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}

Generate hypotheses in this EXACT format:
"Our customer [specific segment] wants [outcome goal], but cannot [action], because [single reason]"

Rules:
- Each hypothesis has ONLY ONE reason (no "and", no multiple assumptions)
- Goal is outcome, not method (e.g. "achieve 5% response rate", not "use AI")
- Reason is testable/falsifiable (can design experiment)
- Cover different angles: time, skill, access, cost

Return JSON array:
[
  {{
    "hypothesis_id": "H1",
    "formulation": "Our customer...",
    "segment": "extracted segment",
    "goal": "extracted goal",
    "barrier": "extracted barrier",
    "reason": "extracted reason"
  }},
  ...
]"""
        
        try:
            # Generate hypotheses via LLM
            hypotheses_result = await rcx.ask_model_raw(
                prompt=generation_prompt,
                model_name="gpt-4o",
            )
            
            # Parse hypotheses
            hypotheses_list = json.loads(hypotheses_result)
            
            # Construct Problem Hypothesis List structure
            problem_list = {
                "source_idea_framing_sheet_id": sheet_path,
                "hypotheses": hypotheses_list,
                "prioritization_date": None,  # Will be set after prioritization
                "selected_hypothesis_id": None,
                "meta": {
                    "created": datetime.utcnow().isoformat(),
                    "version": "v0"
                }
            }
            
            # Write to path
            output_path = f"/customer-research/{idea_name}/hypotheses/problem-list"
            await pdoc_integration.pdoc_write(output_path, json.dumps(problem_list, indent=2), toolcall.fcall_ft_id)
            
            logger.info(f"Generated {len(hypotheses_list)} problem hypotheses at {output_path}")
            
            # Format response
            hypotheses_text = "\n".join([f"{h['hypothesis_id']}: {h['formulation']}" for h in hypotheses_list])
            return f"Problem Hypothesis List created at {output_path}\n\nGenerated {len(hypotheses_list)} hypotheses:\n{hypotheses_text}\n\nNext steps:\n1. Review hypotheses for clarity\n2. Prioritize hypotheses using prioritize_hypotheses tool"
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse hypotheses: {e}")
            return f"Error: Failed to parse hypotheses (got non-JSON response). Try again."
        except Exception as e:
            logger.error(f"Error generating hypotheses: {e}")
            return f"Error generating hypotheses: {str(e)}"

    @rcx.on_tool_call(PRIORITIZE_HYPOTHESES_TOOL.name)
    async def toolcall_prioritize_hypotheses(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        problem_list_path = model_produced_args.get("problem_list_path", "")
        
        if not problem_list_path:
            return "Error: problem_list_path required"
        
        # Read Problem Hypothesis List
        try:
            list_content = await pdoc_integration.pdoc_read(problem_list_path, toolcall.fcall_ft_id)
            problem_list = json.loads(list_content)
        except Exception as e:
            return f"Error reading Problem Hypothesis List: {str(e)}"
        
        hypotheses = problem_list.get("hypotheses", [])
        
        if not hypotheses:
            return "Error: No hypotheses found in list"
        
        # Get ICE scoring criteria from prompts module
        ice_criteria = product_lion_prompts.ICE_PRIORITIZATION_CRITERIA
        
        # Score each hypothesis
        scored_hypotheses = []
        
        for hyp in hypotheses:
            scoring_prompt = f"""Score this problem hypothesis using ICE matrix (Impact × Evidence × Feasibility).

Hypothesis: {hyp.get('formulation', '')}

Criteria:
{ice_criteria}

Return JSON:
{{
  "impact": 0-5,
  "evidence": 0-5,
  "feasibility": 0-5,
  "reasoning": {{
    "impact": "why this score",
    "evidence": "why this score",
    "feasibility": "why this score"
  }}
}}"""
            
            try:
                score_result = await rcx.ask_model_raw(
                    prompt=scoring_prompt,
                    model_name="gpt-4o-mini",
                )
                
                scores = json.loads(score_result)
                
                # Calculate weighted score
                weighted_score = (
                    0.4 * scores.get("impact", 0) +
                    0.4 * scores.get("evidence", 0) +
                    0.2 * scores.get("feasibility", 0)
                )
                
                # Update hypothesis with scores
                hyp["priority_scores"] = {
                    "impact": scores.get("impact", 0),
                    "evidence": scores.get("evidence", 0),
                    "feasibility": scores.get("feasibility", 0),
                    "weighted_score": round(weighted_score, 2),
                    "reasoning": scores.get("reasoning", {})
                }
                
                scored_hypotheses.append(hyp)
                
            except Exception as e:
                logger.error(f"Failed to score {hyp.get('hypothesis_id', '?')}: {e}")
                # Add default scores if scoring fails
                hyp["priority_scores"] = {
                    "impact": 3,
                    "evidence": 3,
                    "feasibility": 3,
                    "weighted_score": 3.0,
                    "reasoning": {"error": str(e)}
                }
                scored_hypotheses.append(hyp)
        
        # Sort by weighted_score descending
        scored_hypotheses.sort(key=lambda h: h.get("priority_scores", {}).get("weighted_score", 0), reverse=True)
        
        # Update problem list
        problem_list["hypotheses"] = scored_hypotheses
        problem_list["prioritization_date"] = datetime.utcnow().isoformat()
        
        # Write back
        await pdoc_integration.pdoc_write(problem_list_path, json.dumps(problem_list, indent=2), toolcall.fcall_ft_id)
        
        logger.info(f"Prioritized {len(scored_hypotheses)} hypotheses at {problem_list_path}")
        
        # Format response as table
        response = f"Prioritization complete!\n\nTop 3 Problem Hypotheses:\n\n"
        
        for i, hyp in enumerate(scored_hypotheses[:3], 1):
            scores = hyp.get("priority_scores", {})
            response += f"{i}. {hyp.get('hypothesis_id', '?')} (Score: {scores.get('weighted_score', 0)})\n"
            response += f"   Impact: {scores.get('impact', 0)}, Evidence: {scores.get('evidence', 0)}, Feasibility: {scores.get('feasibility', 0)}\n"
            response += f"   {hyp.get('formulation', '')}\n\n"
        
        response += f"Next steps:\n"
        response += f"1. Review top hypotheses\n"
        response += f"2. Optional: Validate hypothesis list\n"
        response += f"3. Select one hypothesis for solution design (A3)"
        
        return response

    @rcx.on_tool_call(HYPOTHESIS_TEMPLATE_TOOL.name)
    async def toolcall_hypothesis_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        if not path:
            return "Error: path required"
        if not path.startswith("/customer-research/"):
            return "Error: path must start with /customer-research/ (e.g. /customer-research/my-idea-hypotheses/segment-name)"
        if "-hypotheses/" not in path:
            return "Error: hypothesis path must include '-hypotheses/' (e.g. /customer-research/unicorn-horn-car-hypotheses/social-media-influencers)"
        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'social-media-influencers'"

        skeleton = {
            "hypothesis": {
                "meta": {
                    "author": "",
                    "date": "",
                },
                "section01": {
                    "section_title": "Ideal Customer Profile",
                    "question01": {
                        "q": "Who are the clients?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What do they want to accomplish?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What can't they do today?",
                        "a": ""
                    },
                    "question04": {
                        "q": "Why can't they do it?",
                        "a": ""
                    }
                },
                "section02": {
                    "section_title": "Customer Context",
                    "question01": {
                        "q": "Where do they hang out (channels)?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What are their pains and frustrations?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What outcomes do they desire?",
                        "a": ""
                    },
                    "question04": {
                        "q": "Geography and languages?",
                        "a": ""
                    }
                },
                "section03": {
                    "section_title": "Solution Hypothesis",
                    "question01": {
                        "q": "What is the minimum viable solution for this segment?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What value metric matters most to them?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What would make them choose this over alternatives?",
                        "a": ""
                    }
                },
                "section04": {
                    "section_title": "Validation Strategy",
                    "question01": {
                        "q": "How can we test this hypothesis quickly?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What evidence would prove/disprove this?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What is the success metric?",
                        "a": ""
                    }
                }
            }
        }

        await pdoc_integration.pdoc_write(path, json.dumps(skeleton, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created hypothesis template at {path}")
        return f"✍🏻 {path}\n\n✓ Created hypothesis template for specific customer segment"

    @rcx.on_tool_call(VALIDATE_ARTIFACT_TOOL.name)
    async def toolcall_validate_artifact(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        artifact_path = model_produced_args.get("artifact_path", "")
        artifact_type = model_produced_args.get("artifact_type", "")
        
        if not artifact_path or not artifact_type:
            return "Error: artifact_path and artifact_type required"
        
        # Read artifact
        try:
            artifact_content = await pdoc_integration.pdoc_read(artifact_path, toolcall.fcall_ft_id)
            artifact_data = json.loads(artifact_content)
        except Exception as e:
            return f"Error reading artifact: {str(e)}"
        
        # Get validation criteria from prompts module
        if artifact_type == "sheet":
            criteria = product_lion_prompts.IDEA_FRAMING_SHEET_VALIDATION_CRITERIA
        elif artifact_type == "canvas":
            criteria = product_lion_prompts.FIRST_PRINCIPLES_CANVAS_VALIDATION_CRITERIA
        elif artifact_type == "problem-hypothesis-list":
            criteria = product_lion_prompts.PROBLEM_HYPOTHESIS_LIST_VALIDATION_CRITERIA
        else:
            return f"Error: artifact_type must be 'canvas', 'sheet', or 'problem-hypothesis-list', got '{artifact_type}'"
        
        # Call LLM for validation
        validation_prompt = f"""Validate this {artifact_type} against criteria.

Artifact:
{json.dumps(artifact_data, indent=2)}

Criteria:
{criteria}

Return JSON with this exact structure:
{{
  "status": "pass | pass-with-warnings | fail",
  "issues": [
    {{"severity": "critical|warning|info", "criterion": "C1/W1/etc", "description": "what is wrong", "location": "field.path"}}
  ],
  "suggestions": [
    {{"issue_ref": 0, "fix": "how to fix it"}}
  ]
}}

Rules:
- status is "fail" if ANY critical issues
- status is "pass-with-warnings" if NO critical but >=1 warning
- status is "pass" if NO issues at all
- Check ALL criteria thoroughly
- Be specific in descriptions and locations"""
        
        try:
            # Use simple model call for validation
            validation_result = await rcx.ask_model_raw(
                prompt=validation_prompt,
                model_name="gpt-4o-mini",
            )
            
            # Parse result
            result = json.loads(validation_result)
            status = result.get("status", "fail")
            issues = result.get("issues", [])
            suggestions = result.get("suggestions", [])
            
            # Format human-readable response
            response = f"Validation Status: {status.upper()}\n\n"
            
            if issues:
                issues_text = "\n".join([
                    f"  [{i.get('severity', 'unknown').upper()}] {i.get('criterion', '?')}: {i.get('description', 'no description')} (at {i.get('location', 'unknown')})"
                    for i in issues
                ])
                response += f"Issues:\n{issues_text}\n\n"
            
            if suggestions:
                suggestions_text = "\n".join([f"  - {s.get('fix', 'no suggestion')}" for s in suggestions])
                response += f"Suggestions:\n{suggestions_text}"
            
            logger.info(f"Validated {artifact_path}: {status}")
            return response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation result: {e}")
            return f"Error: Validation failed to parse (got non-JSON response). Try again."
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return f"Error during validation: {str(e)}"

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=productman_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
