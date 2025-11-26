import asyncio
import json
import logging
import re
import base64
import os
from typing import Dict, Any, List, Union
from pymongo import AsyncMongoClient
import openai

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.botticelli import botticelli_install
from flexus_simple_bots.botticelli import botticelli_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_botticelli")


BOT_NAME = "botticelli"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


CAT_PICTURE_TOOL = ckit_cloudtool.CloudTool(
    name="get_cat_picture",
    description="Returns a picture of a cat as base64 encoded image.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

STYLEGUIDE_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_styleguide",
    description="Create style guide file in pdoc. Path format: /design/{project-name}-styleguide",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write style guide. Should be /design/{project-name}-styleguide using kebab-case: '/design/myproject-styleguide'"
            },
            "text": {
                "type": "string",
                "description": "JSON text of the style guide document. Must match the structure of example_styleguide with exact keys."
            },
        },
        "required": ["path", "text"],
    },
)

GENERATE_PICTURE_TOOL = ckit_cloudtool.CloudTool(
    name="generate_picture",
    description="Generate a picture from a text prompt using AI. Saves the result to MongoDB. Acceptable sizes: '1024x1024' (square), '1024x1536' (portrait), '1536x1024' (landscape)",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate"
            },
            "size": {
                "type": "string",
                "enum": ["1024x1024", "1024x1536", "1536x1024"],
                "description": "Image dimensions. Options: '1024x1024' (square), '1024x1536' (portrait), '1536x1024' (landscape)"
            },
            "filename": {
                "type": "string",
                "description": "Filename for storing in MongoDB (e.g., 'ad-campaign/hero-image.png'). Use kebab-case."
            }
        },
        "required": ["prompt", "size", "filename"],
    },
)

TOOLS = [CAT_PICTURE_TOOL, STYLEGUIDE_TEMPLATE_TOOL, GENERATE_PICTURE_TOOL, fi_pdoc.POLICY_DOCUMENT_TOOL]

CAT_PIC = "R0lGODlhAAQAA4QRAP//zMyZZplmMwAAAGYzM8zMmWYzAGZmZpmZmTMAAP/MmTMzM8zMzMxmM2ZmM5mZZplmZv///////////////////////////////////////////////////////////yH5BAEKAB8ALAAAAAAABAADAAX+ICCOZGmeaKqubOu+cCzPdG3feK7vfO//wKBwSCwaj8ikcslsOp/QqHRKrVqv2Kx2y+16v+CweEwum8/otHrNbrvf8Lh8Tq/b7/i8fs/v+/+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wADChxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyj+U6pcybKly5cwY8qcSbOmzZs4c+rcybOnz59AgwodSrSo0aNIkypdyrSp06dQo0qdSrWq1atYs2rdyrWr169gw4odS7as2bNo06pdy7at27dw48qdS7eu3bt48+rdy7ev37+AAwseTLiw4cOIEytezLix48eQI0ueTLmy5cuYM2vezLmz58+gQ4seTbq06dOoU6tezbq169ewY8ueTbu27du4c+vezbu379/AgwsfTry48ePIkytfzry58+fQo0ufTr269evYs2vfzr279+/gw4sfT768+fPo06tfz769+/fw48ufT7++/fv48+vfz7+///8ABijggAQWaOCBCCb+qOCCDDbo4IMQRijhhBRWaOGFGGao4YYcdujhhyCGKOKIJJZo4okopqjiiiy26OKLMMYo44w01mjjjTjmqOOOPPbo449ABinkkEQWaeSRSCap5JJMNunkk1BGKeWUVFZp5ZVYZqnlllx26eWXYIYp5phklmnmmWimqeaabLbp5ptwxinnnHTWaeedeOap55589unnn4AGKuighBZq6KGIJqrooow26uijkEYq6aSUVmrppZhmqummnHbq6aeghirqqKSWauqpqKaq6qqsturqq7DGKuustNZq66245qrrrrz26uuvwAYr7LDEFmvsscgmq+yyzDbr7LPQRivttNT+Vmvttdhmq+223Hbr7bfghivuuOSWa+656Kar7rrstuvuu/DGK++89NZr77345qvvvvz26++/AAcs8MAEF2zwwQgnrPDCDDfs8MMQRyzxxBRXbPHFGGes8cYcd+zxxyCHLPLIJJds8skop6zyyiy37PLLMMcs88w012zzzTjnrPPOPPfs889ABy300EQXbfTRSCet9NJMN+3001BHLfXUVFdt9dVYZ6311lx37fXXYIctNn0FDDAAAzIwYDbaYwdTAAICCPAAAjAggMAActPd9i8HEBBAAAIMUMALAywgAOAD7M23338HQIDeKpSdwOGIK+7LAQY0DjgEkJ9QwAH+eFMe+OCW74K55ogzUMDqrLN+wAIGUI446aXncroCCvwduNm892424wHkPnrtuvQdPO6AC0BA3AYQsLzyz/+N/PDE42I88o3HDrgBmSsft/TTC1699X5jr/vhAjQP+PKN4y68+OPbYjzqyQfAfffa0099/LT0/b3m30tf92QHQAPAj3+zOEAC8qc/7hEQdc07IAJf8TkCZI5+GMyg7gZwALZN0BVl+9/5HghAEZ5vAZ374CpCiDrekfBvvENd3B6nQhAOYHn5c2EGY7i9+yUghTVERQjjRrkEmO2FAeAhEWcIxCCagoWaMyLedlg4DNLQiak4AOic9z8Cmm0BC2j+HBFH6LzCHYB2WCSF3UJnQjEWDolLJAAHEYDGNI4CihqcogY1N4Am2hEUrzPbAh8oxwEgTo8FjGAf/2gKuyHAfy8UXSSVZ0Q6MhIV89vjHpVntjpekhRlQ6QmxVhIP35yFHdj3yiT17xKnnIVCziiJol4PwMk4IyvTMUCVKlB6DVvifvLpSjeZsFRAnOJzbObMO84AAauMnnMs6UEl9mJIT7zbw3o4f3k6ElqZgKP12QeMKfpzW+K8pnpI2ID4kbOcl7CmteEZgC56U5OlM2ZqxxjNAlwAFPWMxJl4yUGSRhAAXLvlv805zn1Bzh5RlOACE3oO28YOxM6II6hq6j+Q5V3AIlO1HkOXOIgZxg69q2zoTPsqEcrEUoLco8Au4QeSOU4Q2A2YJ22VOlKJ9FSaHLRcEukKPto+dKI7lQSLY3jAicXVJcec4a37OZRFxHKBAyVAEvdJ0VrCUxptnOqiUgq+grJRnbyzoLPI+IN6QnWRrxtjLor5ANGOICLPnWGFvxqWwvhP+nF1WzHU2sJ04nV++l1r4NAwPIgIMlCjtCIg4Vq83CJ2EUggLEEcEDysApYx6VPlhvFKj/9WdlBhNJ3qE2tag9bWtO27rWwjW0BGEDb2kq1tbjNrW53y9ve+va3wA2ucIdL3OIa97jITa5yl8vc5jr3udCNrnT+p0vd6lr3utjNrna3y93ueve74A2veMdL3vKa97zoTa9618ve9rr3vfCNr3znS9/62ve++M2vfvfL3/76978ADrCAB0zgAhv4wAhOsIIXzOAGO/jBEI6whCdM4Qpb+MIYzrCGN8zhDnv4wyAOsYhHTOISm/jEKE6xilfM4ha7+MUwjrGMZ0zjGtv4xjjOsY53zOMe+/jHQA6ykIdM5CIb+chITrKSl8zkJjv5yVCOspSnTOUqW/nKWM6ylrfM5S57+ctgDrOYx0zmMpv5zGhOs5rXzOY2u/nNcI6znOdM5zrb+c54zrOe98znPvv5z4AOtKAHTehCG/rQiE60ohfRzehGO/rRkI60pCdN6Upb+tKYzrSmN83pTnv606AOtahHTepSm/rUqE61qlfN6la7+tWwjrWsZ03rWtv61rjOta53zete+/rXwA62sIdN7GIb+9jITrayl83sZjv72dCOtrSnTe1qW/va2M62trfN7W57+9vgDre4x03ucpv73OhOt7rXze52u/vd8I63vOdN73rb+974zre+983vfvv73wAPuMAHTvCCG/zgCE+4whfO8IY7/OEQj7jEJ07xilv84hjPuMY3zvGOe/zjIJ9aCAAAOw=="

async def botticelli_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(botticelli_install.botticelli_setup_schema, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    mongo_conn_str = await ckit_mongo.get_mongodb_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def validate_styleguide_structure(provided: Dict, expected: Dict, path: str = "root") -> str:
        if type(provided) != type(expected):
            return f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(provided).__name__}"
        if isinstance(expected, dict):
            expected_keys = set(expected.keys())
            provided_keys = set(provided.keys())
            if expected_keys != provided_keys:
                missing = expected_keys - provided_keys
                extra = provided_keys - expected_keys
                errors = []
                if missing:
                    errors.append(f"missing keys: {missing}")
                if extra:
                    errors.append(f"unexpected keys: {extra}")
                return f"Key mismatch at {path}: {', '.join(errors)}"
            for key in expected_keys:
                if key == "q":
                    continue
                if key == "a":
                    continue
                if key == "t":
                    continue
                if key == "title":
                    continue
                error = validate_styleguide_structure(provided[key], expected[key], f"{path}.{key}")
                if error:
                    return error
        return ""

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_tool_call(CAT_PICTURE_TOOL.name)
    async def toolcall_get_cat_picture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> Union[str, List[Dict[str, str]]]:
        result = [
            {"m_type": "text", "m_content": "Here is the picture:"},
            {"m_type": "image/gif", "m_content": CAT_PIC}
        ]
        return result

    @rcx.on_tool_call(STYLEGUIDE_TEMPLATE_TOOL.name)
    async def toolcall_styleguide_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        text = model_produced_args.get("text", "")
        if not path:
            return "Error: path required"
        if not text:
            return "Error: text required"
        if not path.startswith("/design/"):
            return "Error: path must start with /design/ (e.g. /design/myproject-styleguide)"
        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'myproject-styleguide'"

        try:
            styleguide_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"

        validation_error = validate_styleguide_structure(styleguide_doc, botticelli_prompts.example_styleguide)
        if validation_error:
            return f"Error: Structure validation failed: {validation_error}"

        await pdoc_integration.pdoc_create(path, json.dumps(styleguide_doc, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created style guide at {path}")
        return f"✍️ {path}\n\n✓ Created style guide document"

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_policy_document(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(GENERATE_PICTURE_TOOL.name)
    async def toolcall_generate_picture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        prompt = model_produced_args.get("prompt", "")
        size = model_produced_args.get("size", "1024x1024")
        filename = model_produced_args.get("filename", "")

        if not prompt:
            return "Error: prompt required"
        if not filename:
            return "Error: filename required"
        if size not in ["1024x1024", "1024x1536", "1536x1024"]:
            return f"Error: size must be one of: 1024x1024 (square), 1024x1536 (portrait), 1536x1024 (landscape)"

        if not filename.endswith(".png"):
            filename = filename + ".png"

        try:
            logger.info(f"Generating image: {prompt[:50]}... size={size}")
            rsp = await openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size,
                response_format="b64_json"
            )

            image_b64 = rsp.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)

            await ckit_mongo.store_file(personal_mongo, filename, image_bytes)
            logger.info(f"Saved generated image to MongoDB: {filename}")

            return f"created {filename}"

        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            return f"Error generating image: {str(e)}"

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
        bot_main_loop=botticelli_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
    ))


if __name__ == "__main__":
    main()
