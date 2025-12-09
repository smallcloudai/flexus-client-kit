#!/usr/bin/env python3

import asyncio
import json
import time
from pathlib import Path
from flexus_backend.db_connections.dbconn_prisma import my_prisma

TEST_DOCS_DIR = Path(__file__).parent

async def main():
    await my_prisma.connect()

    try:
        ws_id = "solarsystem"
        fgroup_id = "solar_root"
        persona_id = "productman_test"

        idea_path = "customer_research.dentist_samples.idea"
        hypothesis_path = "customer_research.dentist_samples.private_practice_dentists.hypothesis"

        print("Cleaning up previous test data...")

        await my_prisma.flexus_persona_kanban_task.delete_many(
            where={"persona_id": persona_id}
        )
        print(f"Deleted tasks for persona {persona_id}")

        await my_prisma.flexus_persona.delete_many(
            where={"persona_id": persona_id}
        )
        print(f"Deleted persona {persona_id}")

        await my_prisma.execute_raw(
            """DELETE FROM flexus_policydoc WHERE pdoc_path IN ($1::ltree, $2::ltree)""",
            idea_path,
            hypothesis_path,
        )
        print("Deleted test policy documents")
        
        print("\nStarting fresh installation...")
        
        ws = await my_prisma.flexus_workspace.find_unique(where={"ws_id": ws_id})
        if not ws:
            print(f"Workspace {ws_id} not found")
            return
            
        marketplace_rec = await my_prisma.flexus_marketplace.find_first(
            where={
                "marketable_name": "productman",
                "marketable_stage": {"in": ["MARKETPLACE_STABLE", "MARKETPLACE_BETA", "MARKETPLACE_DEV"]}
            },
            order=[{"marketable_version": "desc"}]
        )
        
        if not marketplace_rec:
            print("Productman not found in marketplace")
            return
            
        print(f"Found productman version {marketplace_rec.marketable_version}")
        
        persona_setup = {
            "featured_tools": ["survey"],
            "survey_enabled": True,
        }

        await my_prisma.flexus_persona.upsert(
            where={"persona_id": persona_id},
            data={
                "create": {
                    "persona_id": persona_id,
                    "owner_fuser_id": "alice@example.com",
                    "located_fgroup_id": fgroup_id,
                    "persona_name": "Test Productman",
                    "persona_setup": json.dumps(persona_setup),
                    "persona_enabled": True,
                    "persona_marketable_name": "productman",
                    "persona_marketable_version": marketplace_rec.marketable_version,
                    "persona_preferred_model": marketplace_rec.marketable_preferred_model_default,
                    "persona_daily_budget": marketplace_rec.marketable_daily_budget_default,
                    "persona_inbox_budget": marketplace_rec.marketable_default_inbox_default,
                    "persona_auto_upgrade": False,
                    "persona_prerelease": False,
                },
                "update": {
                    "persona_setup": json.dumps(persona_setup),
                    "persona_marketable_version": marketplace_rec.marketable_version,
                    "persona_preferred_model": marketplace_rec.marketable_preferred_model_default,
                    "persona_daily_budget": marketplace_rec.marketable_daily_budget_default,
                    "persona_inbox_budget": marketplace_rec.marketable_default_inbox_default,
                },
            },
        )
        print(f"Created/updated persona {persona_id}")
        
        await my_prisma.flexus_persona_schedule.delete_many(
            where={"sched_persona_id": persona_id}
        )
        
        schedule_data = [
            {
                "sched_persona_id": persona_id,
                "sched_type": "SCHED_TODO",
                "sched_when": "EVERY:1m",
                "sched_first_question": "Check todo tasks",
                "sched_enable": True,
                "sched_marketplace": True
            },
            {
                "sched_persona_id": persona_id,
                "sched_type": "SCHED_TASK_SORT",
                "sched_when": "EVERY:1m",
                "sched_first_question": "Sort inbox tasks",
                "sched_enable": True,
                "sched_marketplace": True
            }
        ]
        
        for sched in schedule_data:
            await my_prisma.flexus_persona_schedule.create(data=sched)
        
        print(f"Created schedule records for {persona_id}")

        idea_content = json.loads((TEST_DOCS_DIR / "example_idea.json").read_text())
        hypothesis_content = json.loads((TEST_DOCS_DIR / "example_hypothesis.json").read_text())

        idea_path_display = "/customer-research/dentist-samples/idea"
        hypothesis_path_display = "/customer-research/dentist-samples/private-practice-dentists/hypothesis"
        
        existing_idea = await my_prisma.query_raw(
            """SELECT * FROM flexus_policydoc WHERE pdoc_path = $1::ltree""",
            idea_path
        )
        
        if existing_idea:
            await my_prisma.execute_raw(
                """UPDATE flexus_policydoc SET pdoc_content = $1::jsonb, pdoc_modified_ts = EXTRACT(EPOCH FROM NOW()) WHERE pdoc_path = $2::ltree""",
                json.dumps(idea_content),
                idea_path
            )
        else:
            await my_prisma.execute_raw(
                """INSERT INTO flexus_policydoc (owner_fuser_id, located_fgroup_id, pdoc_path, pdoc_content) 
                   VALUES ($1, $2, $3::ltree, $4::jsonb)""",
                "alice@example.com",
                fgroup_id,
                idea_path,
                json.dumps(idea_content)
            )
        print(f"Created/updated idea document at {idea_path_display}")
        
        existing_hypothesis = await my_prisma.query_raw(
            """SELECT * FROM flexus_policydoc WHERE pdoc_path = $1::ltree""",
            hypothesis_path
        )
        
        if existing_hypothesis:
            await my_prisma.execute_raw(
                """UPDATE flexus_policydoc SET pdoc_content = $1::jsonb, pdoc_modified_ts = EXTRACT(EPOCH FROM NOW()) WHERE pdoc_path = $2::ltree""",
                json.dumps(hypothesis_content),
                hypothesis_path
            )
        else:
            await my_prisma.execute_raw(
                """INSERT INTO flexus_policydoc (owner_fuser_id, located_fgroup_id, pdoc_path, pdoc_content) 
                   VALUES ($1, $2, $3::ltree, $4::jsonb)""",
                "alice@example.com",
                fgroup_id,
                hypothesis_path,
                json.dumps(hypothesis_content)
            )
        print(f"Created/updated hypothesis document at {hypothesis_path_display}")
        
        task_details = {
            "from_bot": "Productman",
            "description": "Run survey validation for dentist-samples hypothesis targeting private-practice-dentists. Use the hypothesis document for all details on segment, pains, solution, and validation metrics.\n\nBoss modification: Approved as it aligns with hypothesis-driven product development.",
            "hypothesis_name": "private-practice-dentists",
            "hypothesis_path": hypothesis_path_display,
            "hypothesis": hypothesis_path_display,
            "policy_documents": [hypothesis_path_display],
        }
        
        experts = marketplace_rec.marketable_experts
        if "survey" not in experts:
            print("Warning: survey skill not found in experts, using default")
            skill = "default"
        else:
            skill = "survey"
        
        expert_id = experts.get(skill, experts.get("default"))
        expert = await my_prisma.flexus_expert.find_unique(where={"fexp_id": expert_id})
        
        current_time = time.time()
        task_data = {
            "persona_id": persona_id,
            "ktask_title": "Survey: private-practice-dentists validation",
            "ktask_skill": skill,
            "ktask_inbox_ts": current_time - 60,
            "ktask_inbox_provenance": json.dumps({
                "message": "Test survey task for dentist samples idea",
                "system": "test_script",
            }),
            "ktask_inactivity_timeout": expert.fexp_inactivity_timeout if expert else 3600,
            "ktask_budget": 100000,
            "ktask_todo_ts": current_time,
            "ktask_inprogress_ts": 0,
            "ktask_done_ts": 0,
            "ktask_details": json.dumps(task_details),
        }
        
        task = await my_prisma.flexus_persona_kanban_task.create(data=task_data)
        print(f"Created kanban task {task.ktask_id}")
        
        print("\nSetup complete!")
        print(f"- Persona: {persona_id}")
        print(f"- Idea: {idea_path_display}")
        print(f"- Hypothesis: {hypothesis_path_display}")
        print(f"- Task: {task.ktask_id} (skill: {skill})")
        
    finally:
        await my_prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
