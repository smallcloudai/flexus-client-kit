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
    name="record_validation_result",
    description="Record validation result that YOU determined. YOU must validate artifact against criteria (see prompt), this tool only RECORDS your validation result.",
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
                "description": "Type of artifact validated"
            },
            "status": {
                "type": "string",
                "enum": ["pass", "pass-with-warnings", "fail"],
                "description": "Validation status YOU determined"
            },
            "issues": {
                "type": "array",
                "description": "Issues YOU found. Each: {severity: 'critical'|'warning', criterion: 'C1'|'W1', description, location}",
                "items": {"type": "object"}
            }
        },
        "required": ["artifact_path", "artifact_type", "status", "issues"]
    }
)

GENERATE_PROBLEM_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    name="write_problem_hypotheses",
    description="**USE THIS TOOL** to write Problem Hypothesis List that YOU generated. YOU must generate hypotheses based on Idea Framing Sheet analysis, this tool only WRITES them to storage. Path: /customer-research/{idea-name}/hypotheses/problem-list",
    parameters={
        "type": "object",
        "properties": {
            "idea_name": {
                "type": "string",
                "description": "Idea name in kebab-case (e.g. 'slack-microwave')"
            },
            "hypotheses": {
                "type": "array",
                "description": "List of hypotheses YOU generated. Each hypothesis: {hypothesis_id, formulation, segment, goal, barrier, reason}",
                "items": {
                    "type": "object",
                    "properties": {
                        "hypothesis_id": {"type": "string"},
                        "formulation": {"type": "string"},
                        "segment": {"type": "string"},
                        "goal": {"type": "string"},
                        "barrier": {"type": "string"},
                        "reason": {"type": "string"}
                    }
                }
            }
        },
        "required": ["idea_name", "hypotheses"]
    }
)

PRIORITIZE_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    name="update_hypotheses_scores",
    description="Update Problem Hypothesis List with ICE scores that YOU calculated. YOU must score each hypothesis (Impact 0-5, Evidence 0-5, Feasibility 0-5), this tool only UPDATES the file with your scores.",
    parameters={
        "type": "object",
        "properties": {
            "problem_list_path": {
                "type": "string",
                "description": "Path to Problem Hypothesis List (e.g. /customer-research/slack-microwave/hypotheses/problem-list)"
            },
            "scores": {
                "type": "array",
                "description": "Scores YOU calculated for each hypothesis. Array of {hypothesis_id, impact, evidence, feasibility, weighted_score}",
                "items": {
                    "type": "object",
                    "properties": {
                        "hypothesis_id": {"type": "string"},
                        "impact": {"type": "number"},
                        "evidence": {"type": "number"},
                        "feasibility": {"type": "number"},
                        "weighted_score": {"type": "number"}
                    }
                }
            }
        },
        "required": ["problem_list_path", "scores"]
    }
)

TOOLS = [
    FIRST_PRINCIPLES_CANVAS_TOOL,
    IDEA_FRAMING_SHEET_TOOL,
    GENERATE_PROBLEM_HYPOTHESES_TOOL,
    PRIORITIZE_HYPOTHESES_TOOL,
    VALIDATE_ARTIFACT_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def product_lion_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    from datetime import datetime
    
    setup = ckit_bot_exec.official_setup_mixing_procedure(product_lion_install.product_lion_setup_schema, rcx.persona.persona_setup)

    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.located_fgroup_id)

    @rcx.on_tool_call(FIRST_PRINCIPLES_CANVAS_TOOL.name)
    async def toolcall_create_first_principles_canvas(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        idea_name = model_produced_args.get("idea_name", "")
        if not idea_name:
            return "Error: idea_name required"
        
        # Validate kebab-case
        if not all(c.islower() or c.isdigit() or c == "-" for c in idea_name):
            return f"Error: idea_name '{idea_name}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'slack-microwave'"
        
        # Construct path: /customer-research/{idea-name}/canvas
        path = f"/customer-research/{idea_name}/canvas"
        
        # First Principles Canvas structure with sections matching sidebar parser format
        canvas = {
            "canvas": {
                "meta": {
                    "author": "",
                    "date": datetime.utcnow().isoformat(),
                    "version": "v0"
                },
                "section01": {
                    "section_title": "Core Truth & Value",
                    "question01": {
                        "q": "What is fundamentally broken in current reality? (observable fact/data)",
                        "a": ""
                    },
                    "question02": {
                        "q": "What is the atomic unit of value we create? (measurable benefit)",
                        "a": ""
                    },
                    "question03": {
                        "q": "One-sentence idea statement: We help [WHO] achieve [WHAT] within [CONSTRAINTS] by [APPROACH]",
                        "a": ""
                    }
                },
                "section02": {
                    "section_title": "Constraints & Context",
                    "question01": {
                        "q": "What external factors limit the user? (time, money, skills, access)",
                        "a": ""
                    },
                    "question02": {
                        "q": "How do people solve this problem today? Why does it suck?",
                        "a": ""
                    }
                },
                "section03": {
                    "section_title": "Validation Path",
                    "question01": {
                        "q": "Minimum end-to-end scenario: Step-by-step path from problem to value",
                        "a": ""
                    },
                    "question02": {
                        "q": "Critical assumptions: What MUST be true for this to work?",
                        "a": ""
                    },
                    "question03": {
                        "q": "Success metrics: How do we know it's working? (order of magnitude, not exact)",
                        "a": ""
                    }
                }
            }
        }

        await pdoc_integration.pdoc_write(path, json.dumps(canvas, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created First Principles Canvas at {path}")
        return f"Canvas created at {path}\n\nFirst Principles Canvas ready: 3 sections with 8 questions for decomposing raw idea into fundamental truths, constraints, and testable assumptions."

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
        
        # If sheet_data provided, use it; otherwise create template in section format
        if not sheet_data:
            sheet_data = {
                "sheet": {
                    "meta": {
                        "author": "",
                        "date": datetime.utcnow().isoformat(),
                        "version": version,
                        "validation_status": "pending"
                    },
                    "section01": {
                        "section_title": "Idea Summary",
                        "question01": {
                            "q": "Title: Short, memorable name for the idea",
                            "a": ""
                        },
                        "question02": {
                            "q": "One-sentence pitch: We help [WHO] achieve [WHAT] by [HOW]",
                            "a": ""
                        },
                        "question03": {
                            "q": "Why now? What changed to make this possible/urgent today?",
                            "a": ""
                        }
                    },
                    "section02": {
                        "section_title": "Target Segment",
                        "question01": {
                            "q": "Who are they? (specific persona/role)",
                            "a": ""
                        },
                        "question02": {
                            "q": "Key characteristics: What defines them? (behaviors, context, constraints)",
                            "a": ""
                        },
                        "question03": {
                            "q": "Market size estimate: Order of magnitude (100s, 1000s, millions?)",
                            "a": ""
                        }
                    },
                    "section03": {
                        "section_title": "Core Problem",
                        "question01": {
                            "q": "Problem description: What pain/friction exists?",
                            "a": ""
                        },
                        "question02": {
                            "q": "Current impact: How does this hurt them today? (time, money, stress)",
                            "a": ""
                        },
                        "question03": {
                            "q": "Frequency: How often does this problem occur?",
                            "a": ""
                        }
                    },
                    "section04": {
                        "section_title": "Value Proposition",
                        "question01": {
                            "q": "Atomic value: What's the smallest measurable benefit we deliver?",
                            "a": ""
                        },
                        "question02": {
                            "q": "Differentiation: Why is this better than alternatives?",
                            "a": ""
                        }
                    },
                    "section05": {
                        "section_title": "Assumptions & Constraints",
                        "question01": {
                            "q": "Key assumptions: What must be true for this to work?",
                            "a": ""
                        },
                        "question02": {
                            "q": "Constraints: What limits us? (resources, regulations, tech, access)",
                            "a": ""
                        }
                    }
                }
            }
        else:
            # Ensure meta fields are set
            if "sheet" in sheet_data and "meta" in sheet_data["sheet"]:
                sheet_data["sheet"]["meta"]["version"] = version
                sheet_data["sheet"]["meta"]["date"] = datetime.utcnow().isoformat()
        
        await pdoc_integration.pdoc_write(path, json.dumps(sheet_data, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created Idea Framing Sheet at {path} ({version})")
        return f"Sheet created at {path} ({version})\n\nIdea Framing Sheet ready: 5 sections with 11 questions covering idea summary, target segment, problem, value prop, assumptions, and constraints."

    @rcx.on_tool_call(GENERATE_PROBLEM_HYPOTHESES_TOOL.name)
    async def toolcall_write_problem_hypotheses(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        idea_name = model_produced_args.get("idea_name", "")
        hypotheses_list = model_produced_args.get("hypotheses", [])
        
        if not idea_name:
            return "Error: idea_name required"
        
        if not hypotheses_list:
            return "Error: hypotheses array is empty. Generate at least 3 hypotheses."
        
        # Validate kebab-case
        if not all(c.islower() or c.isdigit() or c == "-" for c in idea_name):
            return f"Error: idea_name '{idea_name}' must use kebab-case"
        
        # Construct Problem Hypothesis List in section format
        problem_list = {
            "hypotheses": {
                "meta": {
                    "author": "",
                    "date": datetime.utcnow().isoformat(),
                    "version": "v0",
                    "source_sheet": f"/customer-research/{idea_name}/sheet"
                }
            }
        }
        
        # Add each hypothesis as a section
        for i, hyp in enumerate(hypotheses_list, start=1):
            section_key = f"section{i:02d}"
            problem_list["hypotheses"][section_key] = {
                "section_title": f"Hypothesis {hyp.get('hypothesis_id', f'H{i}')}",
                "question01": {
                    "q": "Formulation: Complete hypothesis statement",
                    "a": hyp.get("formulation", "")
                },
                "question02": {
                    "q": "Target segment: Who specifically?",
                    "a": hyp.get("segment", "")
                },
                "question03": {
                    "q": "Goal: What outcome do they want?",
                    "a": hyp.get("goal", "")
                },
                "question04": {
                    "q": "Barrier: What can't they do?",
                    "a": hyp.get("barrier", "")
                },
                "question05": {
                    "q": "Reason: Why is this barrier there?",
                    "a": hyp.get("reason", "")
                },
                "question06": {
                    "q": "ICE Score (after prioritization): Impact × Evidence × Feasibility",
                    "a": ""
                },
                "question07": {
                    "q": "Priority rank (after prioritization): 1=highest",
                    "a": ""
                }
            }
        
        # Write to path
        output_path = f"/customer-research/{idea_name}/hypotheses/problem-list"
        await pdoc_integration.pdoc_write(output_path, json.dumps(problem_list, indent=2), toolcall.fcall_ft_id)
        
        logger.info(f"Wrote {len(hypotheses_list)} problem hypotheses to {output_path}")
        
        return f"Problem Hypothesis List written to {output_path}\n\n{len(hypotheses_list)} hypotheses saved. Next: prioritize using update_hypotheses_scores tool."

    @rcx.on_tool_call(PRIORITIZE_HYPOTHESES_TOOL.name)
    async def toolcall_update_hypotheses_scores(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        from datetime import datetime
        
        problem_list_path = model_produced_args.get("problem_list_path", "")
        scores = model_produced_args.get("scores", [])
        
        if not problem_list_path:
            return "Error: problem_list_path required"
        
        if not scores:
            return "Error: scores array is empty"
        
        # Read Problem Hypothesis List
        try:
            list_content = await pdoc_integration.pdoc_read(problem_list_path, toolcall.fcall_ft_id)
            problem_list = json.loads(list_content)
        except Exception as e:
            return f"Error reading Problem Hypothesis List: {str(e)}"
        
        # Extract hypotheses container
        hypotheses_container = problem_list.get("hypotheses", {})
        
        # Filter section keys (section01, section02, etc)
        section_keys = [k for k in hypotheses_container.keys() if k.startswith("section")]
        
        if not section_keys:
            return "Error: No hypothesis sections found in list"
        
        # Update scores for each hypothesis
        updated_count = 0
        for score_item in scores:
            hypothesis_id = score_item.get("hypothesis_id", "")
            impact = score_item.get("impact", 0)
            evidence = score_item.get("evidence", 0)
            feasibility = score_item.get("feasibility", 0)
            weighted_score = score_item.get("weighted_score", 0)
            
            # Find section with this hypothesis_id
            for section_key in section_keys:
                section = hypotheses_container[section_key]
                if hypothesis_id in section.get("section_title", ""):
                    # Update ICE score in question06
                    ice_score_text = f"I:{impact} E:{evidence} F:{feasibility} = {round(weighted_score, 2)}"
                    section["question06"]["a"] = ice_score_text
                    updated_count += 1
                    break
        
        # Sort sections by weighted_score (need to match hypothesis_id to score)
        scored_sections = []
        for section_key in section_keys:
            section = hypotheses_container[section_key]
            # Extract score from question06
            ice_text = section.get("question06", {}).get("a", "")
            # Parse weighted score
            ws = 0.0
            if "=" in ice_text:
                ws = float(ice_text.split("=")[1].strip())
            scored_sections.append({
                "section_key": section_key,
                "weighted_score": ws,
                "section_data": section
            })
        
        # Sort by weighted_score descending
        scored_sections.sort(key=lambda x: x["weighted_score"], reverse=True)
        
        # Update priority rank in question07
        for rank, item in enumerate(scored_sections, start=1):
            item["section_data"]["question07"]["a"] = str(rank)
        
        # Update sections in hypotheses_container
        for item in scored_sections:
            hypotheses_container[item["section_key"]] = item["section_data"]
        
        # Update meta
        if "meta" in hypotheses_container:
            hypotheses_container["meta"]["prioritization_date"] = datetime.utcnow().isoformat()
        
        # Write back
        await pdoc_integration.pdoc_write(problem_list_path, json.dumps(problem_list, indent=2), toolcall.fcall_ft_id)
        
        logger.info(f"Updated scores for {updated_count} hypotheses at {problem_list_path}")
        
        return f"Scores updated for {updated_count} hypotheses at {problem_list_path}. Ranked by priority."

    @rcx.on_tool_call(VALIDATE_ARTIFACT_TOOL.name)
    async def toolcall_record_validation_result(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        artifact_path = model_produced_args.get("artifact_path", "")
        artifact_type = model_produced_args.get("artifact_type", "")
        status = model_produced_args.get("status", "")
        issues = model_produced_args.get("issues", [])
        
        if not artifact_path or not artifact_type or not status:
            return "Error: artifact_path, artifact_type, and status required"
        
        if status not in ["pass", "pass-with-warnings", "fail"]:
            return f"Error: status must be 'pass', 'pass-with-warnings', or 'fail', got '{status}'"
        
        # Format human-readable response
        response = f"Validation Status: {status.upper()}\n\n"
        
        if issues:
            issues_text = "\n".join([
                f"  [{i.get('severity', 'unknown').upper()}] {i.get('criterion', '?')}: {i.get('description', 'no description')} (at {i.get('location', 'unknown')})"
                for i in issues
            ])
            response += f"Issues:\n{issues_text}\n\n"
        
        logger.info(f"Recorded validation for {artifact_path}: {status}")
        return response

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group, scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=product_lion_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
    ))


if __name__ == "__main__":
    main()
