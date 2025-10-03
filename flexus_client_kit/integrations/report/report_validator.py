import json
import re
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup


def validate_html_content(
        content: str,
        validation_rules: Optional[Dict] = None
) -> Tuple[bool, List[str]]:
    """
    Validate HTML content against rules using BeautifulSoup.

    Args:
        content: HTML string to validate
        validation_rules: Dict with validation requirements:
            - expected_elements: List of required HTML tags
            - required_classes: List of required CSS classes
            - min_td_count: Minimum number of td elements
            - required_text: List of text that must appear

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Parse HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        errors.append(f"HTML parsing error: {str(e)}")
        return False, errors

    dangerous_elements = soup.find_all(['iframe', 'object', 'embed'])
    for elem in dangerous_elements:
        if elem.name == 'iframe':
            errors.append(f"Dangerous content detected: <iframe> tag")
        elif elem.name in ['object', 'embed']:
            errors.append(f"Dangerous content detected: <{elem.name}> tag")

    found_tags = set()
    found_classes = set()
    
    for element in soup.find_all():
        found_tags.add(element.name)
        if element.get('class'):
            found_classes.update(element.get('class'))

    if validation_rules:
        if "expected_elements" in validation_rules:
            for element in validation_rules["expected_elements"]:
                if element not in found_tags:
                    errors.append(f"Missing required element: <{element}>")

        if "required_classes" in validation_rules:
            for cls in validation_rules["required_classes"]:
                if cls not in found_classes:
                    errors.append(f"Missing required CSS class: {cls}")

        if "min_td_count" in validation_rules:
            td_elements = soup.find_all('td')
            td_count = len(td_elements)
            if td_count < validation_rules["min_td_count"]:
                errors.append(f"Insufficient <td> elements: found {td_count}, need {validation_rules['min_td_count']}")

        if "required_text" in validation_rules:
            text_content = soup.get_text().lower()
            for required in validation_rules["required_text"]:
                if not required.startswith("{"):
                    if required.lower() not in text_content:
                        errors.append(f"Missing required text: {required}")

    return len(errors) == 0, errors


def sanitize_html(content: str) -> str:
    content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.DOTALL | re.IGNORECASE)
    return content


def validate_json_schema(
        data: Any,
        schema: Dict[str, Any],
        path: str = ""
) -> List[str]:
    """
    Recursively validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: JSON Schema definition (supports type, properties, required, items, etc.)
        path: Current path in the data structure (for error messages)

    Returns:
        List of error messages
    """
    errors = []
    current_path = path or "root"

    # Check type
    if "type" in schema:
        expected_type = schema["type"]
        if expected_type == "object" and not isinstance(data, dict):
            errors.append(f"{current_path}: expected object, got {type(data).__name__}")
            return errors
        elif expected_type == "array" and not isinstance(data, list):
            errors.append(f"{current_path}: expected array, got {type(data).__name__}")
            return errors
        elif expected_type == "string" and not isinstance(data, str):
            errors.append(f"{current_path}: expected string, got {type(data).__name__}")
            return errors
        elif expected_type == "number" and not isinstance(data, (int, float)):
            errors.append(f"{current_path}: expected number, got {type(data).__name__}")
            return errors
        elif expected_type == "boolean" and not isinstance(data, bool):
            errors.append(f"{current_path}: expected boolean, got {type(data).__name__}")
            return errors
        elif expected_type == "integer" and not isinstance(data, int):
            errors.append(f"{current_path}: expected integer, got {type(data).__name__}")
            return errors

    # Validate object properties
    if schema.get("type") == "object" and isinstance(data, dict):
        # Check required properties
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    errors.append(f"{current_path}.{field}: required field missing")
                elif data[field] is None and not schema.get("properties", {}).get(field, {}).get("nullable", False):
                    errors.append(f"{current_path}.{field}: required field is null")

        # Validate each property if schema is defined
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    field_errors = validate_json_schema(
                        data[field],
                        field_schema,
                        f"{current_path}.{field}"
                    )
                    errors.extend(field_errors)

        # Check for additional properties if not allowed
        if schema.get("additionalProperties") is False:
            allowed_props = set(schema.get("properties", {}).keys())
            extra_props = set(data.keys()) - allowed_props
            if extra_props:
                errors.append(f"{current_path}: unexpected properties: {', '.join(extra_props)}")

    # Validate array items
    elif schema.get("type") == "array" and isinstance(data, list):
        if "items" in schema:
            for i, item in enumerate(data):
                item_errors = validate_json_schema(
                    item,
                    schema["items"],
                    f"{current_path}[{i}]"
                )
                errors.extend(item_errors)

        # Check min/max items
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{current_path}: array has {len(data)} items, minimum {schema['minItems']} required")
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{current_path}: array has {len(data)} items, maximum {schema['maxItems']} allowed")

    # Validate enum values
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{current_path}: value '{data}' not in allowed values: {schema['enum']}")

    # Validate string patterns
    if schema.get("type") == "string" and isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{current_path}: string length {len(data)} is less than minimum {schema['minLength']}")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(f"{current_path}: string length {len(data)} exceeds maximum {schema['maxLength']}")
        if "pattern" in schema:
            import re
            if not re.match(schema["pattern"], data):
                errors.append(f"{current_path}: string does not match pattern '{schema['pattern']}'")

    # Validate number constraints
    if schema.get("type") in ["number", "integer"] and isinstance(data, (int, float)):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{current_path}: value {data} is less than minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{current_path}: value {data} exceeds maximum {schema['maximum']}")

    return errors


def validate_json_content(
        content: str,
        validation_rules: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate JSON content against a JSON schema.

    Args:
        content: JSON string to validate
        validation_rules: JSON Schema definition

    Returns:
        Tuple of (is_valid, error_messages)
    """
    # First check if it's valid JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {str(e)}"]
    except Exception as e:
        return False, [f"JSON parsing error: {str(e)}"]

    return True, []
    # If no schema provided, just check JSON validity
    if not validation_rules:
        return True, []

    # Validate against schema
    errors = validate_json_schema(data, validation_rules)

    return len(errors) == 0, errors
