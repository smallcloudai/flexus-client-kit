import asyncio
import json
import logging
import re
import base64
import os
import io
from typing import Dict, Any, List, Union
from pymongo import AsyncMongoClient
import openai
from PIL import Image

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.botticelli import botticelli_install
from flexus_simple_bots.botticelli import botticelli_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_botticelli")


BOT_NAME = "botticelli"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


STYLEGUIDE_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_styleguide",
    description="Create style guide file in pdoc. Saves to /style-guide by default.",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "JSON text of the style guide document. Must match the structure of example_styleguide with exact keys."
            },
            "path": {
                "type": "string",
                "description": "Optional path where to write style guide. Defaults to /style-guide"
            },
        },
        "required": ["text"],
    },
)

GENERATE_PICTURE_TOOL = ckit_cloudtool.CloudTool(
    name="picturegen",
    description="Generate a picture from a text prompt using AI. Saves .png result to MongoDB. Acceptable sizes: '1024x1024' (square), '1024x1536' (portrait), '1536x1024' (landscape)",
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
                "description": "Filename for storing in MongoDB, e.g. '/my-artwork/neon-elephant-at-night--buy-our-elephants.png'"
            }
        },
        "required": ["prompt", "size", "filename"],
    },
)

CROP_IMAGE_TOOL = ckit_cloudtool.CloudTool(
    name="crop_image",
    description="Crop an image into one or more regions. Creates full-size crops plus 0.5x scaled versions. Outputs named with -crop000, -crop001, etc.",
    parameters={
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "Path to source image in MongoDB, e.g. 'pictures/my-image.webp'"
            },
            "crops": {
                "type": "array",
                "description": "List of crop regions as [x, y, width, height] in pixels. Example: [[0, 0, 512, 512], [512, 0, 512, 512]]",
                "items": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 4,
                    "maxItems": 4
                }
            }
        },
        "required": ["source_path", "crops"],
    },
)

CAMPAIGN_BRIEF_TOOL = ckit_cloudtool.CloudTool(
    name="meta_campaign_brief",
    description="Start Meta Ads creative generation with campaign brief. Creates structured campaign with 3 creative variations.",
    parameters={
        "type": "object",
        "properties": {
            "campaign_id": {
                "type": "string",
                "description": "Unique campaign ID (kebab-case, e.g. 'camp001-product-launch')"
            },
            "brand_name": {
                "type": "string",
                "description": "Brand or product name"
            },
            "brand_colors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Brand colors as hex codes (e.g. ['#1A365D', '#0694A2', '#F8FAFC'])"
            },
            "brand_fonts": {
                "type": "string",
                "description": "Brand fonts (e.g. 'Helvetica Neue, Inter, sans-serif')"
            },
            "campaign_objective": {
                "type": "string",
                "enum": ["Awareness", "Traffic", "Engagement", "Leads", "Sales"],
                "description": "Campaign objective"
            },
            "target_audience": {
                "type": "string",
                "description": "Target audience: demographics, psychographics, pain points"
            },
            "key_benefit": {
                "type": "string",
                "description": "Main benefit from FAB (Features-Advantages-Benefits) framework"
            },
            "industry": {
                "type": "string",
                "description": "Industry or category (e.g. 'SaaS', 'E-commerce', 'B2B', 'Local Services')"
            },
            "visual_style": {
                "type": "string",
                "enum": ["photography", "illustration", "3D", "mixed"],
                "description": "Preferred visual style"
            },
            "product_details": {
                "type": "string",
                "description": "Optional: Product/service details, features, unique selling points"
            }
        },
        "required": ["campaign_id", "brand_name", "campaign_objective", "target_audience", "key_benefit", "industry"]
    },
)

TOOLS = [
    STYLEGUIDE_TEMPLATE_TOOL,
    GENERATE_PICTURE_TOOL,
    CROP_IMAGE_TOOL,
    CAMPAIGN_BRIEF_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL
]

async def botticelli_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(botticelli_install.botticelli_setup_schema, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
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

    @rcx.on_tool_call(STYLEGUIDE_TEMPLATE_TOOL.name)
    async def toolcall_styleguide_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "/style-guide")
        text = model_produced_args.get("text", "")

        if not text:
            return "Error: text required"

        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only)"

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
    async def toolcall_generate_picture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> Union[str, List[Dict[str, str]]]:
        prompt = model_produced_args.get("prompt", "")
        size = model_produced_args.get("size", "1024x1024")
        filename = model_produced_args.get("filename", "")

        if not prompt:
            return "Error: prompt required"
        if not filename:
            return "Error: filename required"
        if size not in ["1024x1024", "1024x1536", "1536x1024"]:
            return f"Error: size must be one of: 1024x1024 (square), 1024x1536 (portrait), 1536x1024 (landscape)"

        try:
            filename.encode('ascii')
        except UnicodeEncodeError:
            return "Error: filename must be ASCII only"

        if ' ' in filename:
            return "Error: filename cannot contain spaces"

        if any(ord(c) < 32 or ord(c) == 127 for c in filename):
            return "Error: filename cannot contain control characters"

        if ".." in filename or "\\" in filename:
            return "Error: filename contains invalid path sequences (no .. or backslashes)"

        if not filename.endswith(".png"):
            filename = filename + ".png"
        filename_base = filename.replace(".png", "")

        try:
            logger.info(f"Generating {size} image: {prompt[:50]}...")
            rsp = await openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size,
                response_format="b64_json"
            )

            image_b64 = rsp.data[0].b64_json
            png_bytes = base64.b64decode(image_b64)
            with Image.open(io.BytesIO(png_bytes)) as img:
                img_w, img_h = img.size
                img_w2, img_h2 = img_w // 2, img_h // 2
                webp_buffer = io.BytesIO()
                img_resized = img.resize((img_w2, img_h2), Image.LANCZOS)
                webp_resized_buffer = io.BytesIO()
                img.save(webp_buffer, 'WEBP', quality=85, method=6)
                img_resized.save(webp_resized_buffer, 'WEBP', quality=85, method=6)
                webp_bytes = webp_buffer.getvalue()
                webp_resized_bytes = webp_resized_buffer.getvalue()

            logger.info("Image sizes: PNG %0.1fk, WebP %0.1fk, WebP resized %0.1fk" % (len(png_bytes) / 1024.0,  len(webp_bytes) / 1024.0, len(webp_resized_bytes) / 1024.0))
            webp_p1 = filename.replace(".png", ".webp")
            webp_p2 = f"{filename_base}-{img_w2}x{img_h2}.webp"
            await ckit_mongo.mongo_store_file(personal_mongo, webp_p1, webp_bytes, 90 * 86400)
            await ckit_mongo.mongo_store_file(personal_mongo, webp_p2, webp_resized_bytes, 90 * 86400)
            logger.info(f"Saved to MongoDB: {webp_p1}")
            logger.info(f"Saved to MongoDB: {webp_p2}")
            image_url1 = f"{fclient.base_url_http}/v1/docs/{rcx.persona.persona_id}/{webp_p1}"
            image_url2 = f"{fclient.base_url_http}/v1/docs/{rcx.persona.persona_id}/{webp_p2}"
            result = [
                {"m_type": "text", "m_content": f"Generated image saved to mongodb:\n{webp_p1}\nor 0.5x size:\n{webp_p2}\n\nAccessible via:\n{image_url1}\n{image_url2}\n"},
                {"m_type": "image/webp", "m_content": image_url2}
            ]
            return result

        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            return f"Error generating image: {str(e)}"

    @rcx.on_tool_call(CROP_IMAGE_TOOL.name)
    async def toolcall_crop_image(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> Union[str, List[Dict[str, str]]]:
        source_path = model_produced_args.get("source_path", "")
        crops = model_produced_args.get("crops", [])

        if not source_path:
            return "Error: source_path required"
        if not crops:
            return "Error: crops list required"

        source_doc = await ckit_mongo.mongo_retrieve_file(personal_mongo, source_path)
        if not source_doc:
            return f"Error: source image not found: {source_path}"
        source_bytes = source_doc["data"]

        with Image.open(io.BytesIO(source_bytes)) as src_img:
            src_w, src_h = src_img.size

            for i, crop in enumerate(crops):
                if not isinstance(crop, list) or len(crop) != 4:
                    return f"Error: crop {i} must be [x, y, width, height]"
                x, y, w, h = crop
                if not all(isinstance(v, int) for v in [x, y, w, h]):
                    return f"Error: crop {i} coordinates must be integers"
                if x < 0 or y < 0 or w <= 0 or h <= 0:
                    return f"Error: crop {i} has invalid coordinates: x={x}, y={y}, w={w}, h={h}"
                if x + w > src_w or y + h > src_h:
                    return f"Error: crop {i} exceeds image bounds (image is {src_w}x{src_h}, crop goes to {x+w}x{y+h})"

            base_path = re.sub(r'-\d+x\d+\.webp$', '.webp', source_path)
            base_path = re.sub(r'-crop\d{3}\.webp$', '.webp', base_path)
            base_path = re.sub(r'\.webp$', '', base_path)

            existing_files = set()
            cursor = personal_mongo.find({})
            async for doc in cursor:
                if "filename" in doc:
                    existing_files.add(doc["filename"])

            results = []
            for crop_idx, crop in enumerate(crops):
                x, y, w, h = crop

                crop_num = None
                for num in range(1000):
                    candidate = f"{base_path}-crop{num:03d}.webp"
                    if candidate not in existing_files:
                        crop_num = num
                        existing_files.add(candidate)
                        break

                if crop_num is None:
                    return "Error: no available crop numbers (crop000-crop999 all used)"

                cropped = src_img.crop((x, y, x + w, y + h))

                webp_buffer = io.BytesIO()
                cropped.save(webp_buffer, 'WEBP', quality=85, method=6)
                webp_bytes = webp_buffer.getvalue()

                crop_w2, crop_h2 = w // 2, h // 2
                cropped_resized = cropped.resize((crop_w2, crop_h2), Image.LANCZOS)
                webp_resized_buffer = io.BytesIO()
                cropped_resized.save(webp_resized_buffer, 'WEBP', quality=85, method=6)
                webp_resized_bytes = webp_resized_buffer.getvalue()

                crop_path = f"{base_path}-crop{crop_num:03d}.webp"
                crop_resized_path = f"{base_path}-crop{crop_num:03d}-{crop_w2}x{crop_h2}.webp"

                await ckit_mongo.mongo_store_file(personal_mongo, crop_path, webp_bytes, 90 * 86400)
                await ckit_mongo.mongo_store_file(personal_mongo, crop_resized_path, webp_resized_bytes, 90 * 86400)
                existing_files.add(crop_resized_path)

                logger.info(f"Saved crop {crop_path} ({w}x{h} @ {x},{y})")
                logger.info(f"Saved crop {crop_resized_path}")

                image_url1 = f"{fclient.base_url_http}/v1/docs/{rcx.persona.persona_id}/{crop_path}"
                image_url2 = f"{fclient.base_url_http}/v1/docs/{rcx.persona.persona_id}/{crop_resized_path}"
                results.append({
                    "crop_num": crop_num,
                    "full_path": crop_path,
                    "resized_path": crop_resized_path,
                    "url1": image_url1,
                    "url2": image_url2,
                })

            result_text = f"Cropped {len(crops)} region(s) from {source_path}:\n\n"
            for r in results:
                result_text += f"Crop {r['crop_num']:03d} saved to MongoDB:\n"
                result_text += f"  {r['full_path']}\n"
                result_text += f"  {r['resized_path']}\n"
                result_text += f"  Accessible via:\n"
                result_text += f"    {r['url1']}\n"
                result_text += f"    {r['url2']}\n"

            response = [{"m_type": "text", "m_content": result_text}]
            for r in results:
                response.append({"m_type": "image/webp", "m_content": r["url2"]})
            return response

    @rcx.on_tool_call(CAMPAIGN_BRIEF_TOOL.name)
    async def toolcall_campaign_brief(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        try:
            campaign_id = model_produced_args.get("campaign_id", "")
            if not campaign_id:
                return "Error: campaign_id is required"
            
            # Validate campaign_id format (kebab-case)
            if not all(c.islower() or c.isdigit() or c == "-" for c in campaign_id):
                return "Error: campaign_id must be kebab-case (lowercase letters, numbers, hyphens only)"
            
            # Validate required fields
            required_fields = ["brand_name", "campaign_objective", "target_audience", "key_benefit", "industry"]
            for field in required_fields:
                if not model_produced_args.get(field):
                    return f"Error: {field} is required"
            
            # Save campaign brief to policy document
            brief_path = f"/ad-campaigns/{campaign_id}/brief"
            brief_content = json.dumps(model_produced_args, indent=2)
            
            await pdoc_integration.pdoc_create(brief_path, brief_content, toolcall.fcall_ft_id)
            logger.info(f"Created campaign brief at {brief_path}")
            
            # Prepare context for subchat with campaign brief details
            brief_summary = f"""Campaign Brief: {campaign_id}
Brand: {model_produced_args.get('brand_name')}
Objective: {model_produced_args.get('campaign_objective')}
Target Audience: {model_produced_args.get('target_audience')}
Key Benefit: {model_produced_args.get('key_benefit')}
Industry: {model_produced_args.get('industry')}
Visual Style: {model_produced_args.get('visual_style', 'Not specified')}

Full brief saved to: {brief_path}

"""
            
            context = brief_summary + json.dumps(model_produced_args, indent=2)
            
            # Create subchat for creative generation with meta_ads_creative skill
            subchats = await ckit_ask_model.bot_subchat_create_multiple(
                client=fclient,
                who_is_asking="botticelli_campaign_brief",
                persona_id=rcx.persona.persona_id,
                first_question=[context],
                first_calls=["null"],
                title=[f"Meta Ads Creative: {campaign_id}"],
                fcall_id=toolcall.fcall_id,
                skill="meta_ads_creative",
            )
            
            logger.info(f"Created subchat for campaign {campaign_id} with skill=meta_ads_creative")
            raise ckit_cloudtool.WaitForSubchats(subchats)
            
        except ckit_cloudtool.WaitForSubchats:
            raise
        except Exception as e:
            logger.exception(f"Error in campaign_brief handler: {e}")
            return f"Error: {str(e)}"

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=botticelli_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=botticelli_install.install,
    ))


if __name__ == "__main__":
    main()
