import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

import gql

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("email_template")

COMPONENTS_DIR = Path(__file__).parent / "components"

EMAIL_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="email_template",
    description="Render email templates from JSON components. Use op='help' for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["help", "components", "render", "preview"],
                "description": "Operation to perform",
                "order": 1,
            },
            "args": {
                "type": "object",
                "description": "Arguments for the operation",
                "order": 2,
            },
        },
        "required": ["op"],
    },
)


HELP_TEXT = """
# Email Template Tool

Renders email templates from JSON components for Scout outreach.

## Operations

### help
Show this help text.

### components
List available email components with their parameters.

### render
Render template JSON to HTML.
```
email_template(op="render", args={
    "template_json": {...},  # Template JSON object or path like "/communications/email-template"
    "variables": {...}       # Variable values to substitute
})
```

### preview
Render and prepare for popup preview.
```
email_template(op="preview", args={
    "template_json": {...},
    "variables": {...}
})
```
Then call print_widget(t="open-form-popup", ...) with the returned data.

## Template Storage

Templates are stored as policy documents. Use flexus_policy_document to:
- List templates: `flexus_policy_document(op="list", args={p: "/communications"})`
- Read template: `flexus_policy_document(op="cat", args={p: "/communications/email-template"})`
- Create/update: `flexus_policy_document(op="create", args={p: "/communications/my-template", text: "..."})`

## Template JSON Format

```json
{
  "subject": "Quick question about {{hypothesis_segment}}",
  "components": [
    {"type": "header", "params": {"brand_color": "#4A90D9"}},
    {"type": "greeting", "params": {"style": "casual"}, "content": "Hey {{contact_first_name}}!"},
    {"type": "paragraph", "content": "{{main_message}}"},
    {"type": "cta_button", "params": {"text": "{{cta_text}}", "url": "{{cta_url}}"}},
    {"type": "incentive_box", "condition": "{{has_incentive}}", "params": {"title": "Thanks!", "description": "{{incentive}}"}},
    {"type": "signature", "params": {"name": "{{sender_name}}", "title": "{{sender_title}}"}},
    {"type": "footer"}
  ]
}
```

## Variables

| Variable | Description |
|----------|-------------|
| {{contact_first_name}} | Contact's first name |
| {{contact_email}} | Contact's email |
| {{source}} | How they found us (UTM) |
| {{hypothesis_segment}} | Target segment from hypothesis |
| {{main_message}} | Personalized message body |
| {{cta_text}} | Button text |
| {{cta_url}} | Button URL |
| {{incentive}} | Perk description |
| {{sender_name}} | Your name |
| {{sender_title}} | Your title |
"""


def _load_component(component_type: str) -> Optional[str]:
    path = COMPONENTS_DIR / f"{component_type}.html"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _list_components() -> List[Dict[str, Any]]:
    result = []
    for path in COMPONENTS_DIR.glob("*.html"):
        name = path.stem
        content = path.read_text(encoding="utf-8")
        params_match = re.search(r'<!-- Params: (.+?) -->', content)
        params = params_match.group(1) if params_match else ""
        result.append({"name": name, "params": params})
    return result


def _substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    result = text
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value) if value else "")
    return result


def _process_param_defaults(text: str) -> str:
    def replace_default(match):
        parts = match.group(1).split("|default:")
        if len(parts) == 2:
            return parts[1]
        return match.group(0)
    return re.sub(r'\{\{([^}]+)\}\}', replace_default, text)


def _process_conditionals(text: str) -> str:
    def process_if(match):
        condition_var = match.group(1)
        content = match.group(2)
        if f"{{{{{condition_var}}}}}" in content or not condition_var.strip():
            return ""
        return content
    return re.sub(r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}', process_if, text, flags=re.DOTALL)


def _render_component(component: Dict[str, Any], variables: Dict[str, Any]) -> str:
    component_type = component.get("type", "")
    template = _load_component(component_type)
    if not template:
        return f"<!-- Unknown component: {component_type} -->"

    params = component.get("params", {})
    content = component.get("content", "")

    all_vars = {**variables, **params, "content": content}
    rendered = _substitute_variables(template, all_vars)
    rendered = _process_param_defaults(rendered)
    rendered = _process_conditionals(rendered)

    return rendered


def render_template(template_json: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, str]:
    subject = template_json.get("subject", "")
    subject = _substitute_variables(subject, variables)

    components = template_json.get("components", [])
    body_parts = []

    for comp in components:
        condition = comp.get("condition", "")
        if condition:
            condition_value = _substitute_variables(condition, variables)
            if not condition_value or condition_value == condition:
                continue
        body_parts.append(_render_component(comp, variables))

    body_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td>
                            {"".join(body_parts)}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return {"subject": subject, "body_html": body_html}


class IntegrationEmailTemplate:
    def __init__(self, rcx, pdoc_integration, fclient):
        self.rcx = rcx
        self.pdoc = pdoc_integration
        self.fclient = fclient

    async def handle_email_template(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_args: Dict[str, Any],
    ) -> str:
        op = model_args.get("op", "help").lower()
        args = model_args.get("args", {})

        try:
            if op == "help":
                return HELP_TEXT

            if op == "components":
                return self._handle_components()

            if op == "render":
                return await self._handle_render(args)

            if op == "preview":
                return await self._handle_preview(toolcall, args)

            return f"❌ Unknown operation: {op}. Use 'help' for usage."

        except Exception as e:
            logger.error("email_template error: %s", e, exc_info=e)
            return f"❌ Error: {e}"

    def _handle_components(self) -> str:
        components = _list_components()
        if not components:
            return "❌ No components found. Check components/ directory."

        lines = ["# Available Email Components\n"]
        for c in components:
            lines.append(f"## {c['name']}")
            lines.append(f"Parameters: {c['params']}\n")
        return "\n".join(lines)

    async def _handle_render(self, args: Dict[str, Any]) -> str:
        template_json = args.get("template_json")
        variables = args.get("variables", {})

        if not template_json:
            return "❌ Missing required argument: template_json"

        # If template_json is a path, read from pdoc
        if isinstance(template_json, str):
            if template_json.startswith("/"):
                try:
                    doc = await self.pdoc.pdoc_cat(template_json)
                    template_json = json.loads(doc.text)
                except Exception as e:
                    return f"❌ Failed to read template from {template_json}: {e}"
            else:
                try:
                    template_json = json.loads(template_json)
                except json.JSONDecodeError as e:
                    return f"❌ Invalid template_json: {e}"

        result = render_template(template_json, variables)
        return f"Subject: {result['subject']}\n\n---\n\n{result['body_html']}"

    async def _handle_preview(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        args: Dict[str, Any],
    ) -> str:
        template_json = args.get("template_json")
        variables = args.get("variables", {})

        if not template_json:
            return """❌ Missing template_json for preview. Usage:
email_template(op="preview", args={
    "template_json": {...} or "/path/to/template",
    "variables": {...}
})"""

        # If template_json is a path, read from pdoc
        if isinstance(template_json, str):
            if template_json.startswith("/"):
                try:
                    doc = await self.pdoc.pdoc_cat(template_json)
                    template_json = json.loads(doc.text)
                except Exception as e:
                    return f"❌ Failed to read template from {template_json}: {e}"
            else:
                try:
                    template_json = json.loads(template_json)
                except json.JSONDecodeError as e:
                    return f"❌ Invalid template_json: {e}"

        result = render_template(template_json, variables)

        # Call backend mutation to create preview URL
        http = await self.fclient.use_http()
        async with http as h:
            r = await h.execute(
                gql.gql("""
                    mutation ScoutEmailPreview($input: EmailPreviewCreateInput!) {
                        email_preview_create(input: $input) {
                            preview_url
                            preview_token
                        }
                    }"""),
                variable_values={
                    "input": {
                        "html": result["body_html"],
                        "subject": result["subject"],
                    }
                },
            )

        preview_url = r["email_preview_create"]["preview_url"]
        base_url = self.fclient.base_url_http.rstrip("/")
        full_url = f"{base_url}{preview_url}"

        return f"""✅ Email preview created!

**Open preview:** {full_url}

Subject: {result['subject']}"""
