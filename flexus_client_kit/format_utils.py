"""Formatting utilities for displaying file content with proper truncation and image support."""

import json
import base64
import logging
from io import BytesIO
from pathlib import Path
from re import Pattern
from typing import Union, Optional, List, Dict, Any, Tuple

from PIL import Image
from genson import SchemaBuilder

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

DEFAULT_SAFETY_VALVE = 50

def get_json_schema(data: Union[dict, list]) -> Optional[str]:
    """Generate a JSON schema for the given data."""
    try:
        builder = SchemaBuilder()
        builder.add_object(data)
        schema = builder.to_schema()
        schema_str = json.dumps(schema, indent=2)
        max_schema_lines = 200
        schema_lines = schema_str.split('\n')
        if len(schema_lines) > max_schema_lines:
            schema_lines = schema_lines[:max_schema_lines] + ['  ...', '}']
            schema_str = '\n'.join(schema_lines)
        
        return f"Schema:\n{schema_str}"
    except Exception as e:
        logger.debug(f"Failed to generate schema: {e}")
        return None


def process_image_to_base64(image_data: bytes) -> Optional[str]:
    """Convert image bytes to base64 string for display."""
    try:
        with Image.open(BytesIO(image_data)) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            
            img.thumbnail((600, 600), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=80, optimize=True)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode('utf-8')
    except Exception as e:
        logger.debug(f"Failed to process image: {e}")
        return None


def format_json_output(
    path: str,
    data: Union[dict, list],
    safety_valve: str = "50k"
) -> Tuple[str, bool]:
    """Format JSON data for display with truncation if needed."""
    if safety_valve.lower().endswith('k'):
        safety_valve_kb = int(safety_valve[:-1])
    else:
        safety_valve_kb = 50
    
    content_str = json.dumps(data, indent=2)
    data_type = "JSON"
    schema = get_json_schema(data)
    
    size_bytes = len(content_str.encode('utf-8'))
    size_kb = size_bytes / 1024
    
    header_lines = [
        f"📄 File: {path}",
        f"   Type: {data_type}",
        f"   Size: {size_bytes:,} bytes ({size_kb:.1f} KB)"
    ]
    
    if isinstance(data, list):
        header_lines.append(f"   Items: {len(data)}")
    elif isinstance(data, dict):
        header_lines.append(f"   Keys: {len(data)}")
    
    if schema:
        header_lines.append(f"   {schema}")
    
    truncated = False
    if size_kb > safety_valve_kb:
        max_chars = safety_valve_kb * 1024
        preview = content_str[:max_chars]
        last_newline = preview.rfind('\n')
        if last_newline > 0:
            preview = preview[:last_newline]
        preview += "\n\n... (truncated)"
        truncated = True
        header_lines.append(f"   ⚠️ Truncated to {safety_valve_kb} KB (safety_valve={safety_valve})")
    else:
        preview = content_str
    
    result = "\n".join(header_lines)
    result += "\n" + "─" * 50 + "\n"
    result += preview
    
    if truncated:
        result += f"\n\n💡 To see full content, download the file or increase safety_valve"
    
    return result, truncated


def format_text_output(
    path: str,
    content: str,
    lines_range: str,
    safety_valve: str = "50k"
) -> Tuple[str, bool]:
    """Format text data for display with truncation if needed."""
    if safety_valve.lower().endswith('k'):
        safety_valve_kb = int(safety_valve[:-1])
    else:
        safety_valve_kb = DEFAULT_SAFETY_VALVE
    size_bytes = len(content.encode('utf-8'))
    size_kb = size_bytes / 1024    
    header_lines = [
        f"📄 File: {path}",
        f"   Type: Text",
        f"   Size: {size_bytes:,} bytes ({size_kb:.1f} KB)"
    ]
    ctx_left = safety_valve_kb * 1024
    lines = content.splitlines()
    if ":" in lines_range:
        start_str, end_str = lines_range.split(":", 1)
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else len(lines)
    else:
        start = end = int(lines_range)
    start = max(0, start)
    end = min(len(lines), end)
    result = []
    for i in range(start, end):
        line = lines[i]
        if len(line.encode('utf-8')) > ctx_left:
            truncated_line = line.encode('utf-8')[:ctx_left].decode('utf-8', errors="ignore") # ingore partial chars
            header_lines.append(f"   ⚠️ Truncated to {safety_valve_kb} KB (safety_valve={safety_valve})")
            result.append(truncated_line + ("\n\n... (truncated)"))
            break
        else:
            result.append(line)

    result = header_lines + result
    return "\n".join(result)
def format_binary_output(
    path: str,
    data: bytes,
    safety_valve: str = "50k"
) -> Tuple[str, bool]:
    """Format binary data for display, with special handling for images."""
    size_bytes = len(data)
    size_kb = size_bytes / 1024
    
    file_ext = Path(path).suffix.lower()
    is_image = file_ext in IMAGE_EXTENSIONS
    
    header_lines = [
        f"📄 File: {path}",
        f"   Type: Binary {'Image' if is_image else 'File'}",
        f"   Size: {size_bytes:,} bytes ({size_kb:.1f} KB)"
    ]
    
    result = "\n".join(header_lines)
    result += "\n" + "─" * 50 + "\n"
    
    if is_image:
        base64_image = process_image_to_base64(data)
        if base64_image:
            result += f"![Image]({path})\n"
            result += f"<image base64>\n{base64_image}\n</image base64>"
            return result
    
    try:
        text_content = data.decode('utf-8')
        return format_text_output(path, text_content, safety_valve)
    except UnicodeDecodeError:
        pass
    
    if b'\x00' in data[:1000]:
        result += "Binary file (contains null bytes)\n"
        result += "Cannot be displayed as text\n\n"
    else:
        try:
            text_content = data.decode('utf-8', errors='replace')
            preview = text_content[:1024]
            if len(text_content) > 1024:
                preview += "\n... (binary preview truncated)"
            result += "Binary file (displayed with error replacement):\n\n"
            result += preview
        except Exception:
            result += "Binary file (cannot be displayed)\n"
    
    return result, False


def format_cat_output(
    path: str,
    file_data: Union[bytes, str, list, dict],
    safety_valve: str = "50k"
) -> str:
    """Main function to format file data for display."""
    if file_data is None:
        return f"Error: File {path} has no content"
    
    if isinstance(file_data, bytes):
        return format_binary_output(path, file_data, safety_valve)[0]
    elif isinstance(file_data, str):
        return format_text_output(path, file_data, safety_valve)[0]
    else:
        return format_json_output(path, file_data, safety_valve)[0]
    

def grep_output(
    path: str, # just for print
    content: str,
    pattern: Pattern[str],
    context: int
) -> str:
    match_lines = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines):
        if pattern.search(line):
            prev_num = -1 if not match_lines else match_lines[-1]
            eff_start = max(prev_num + 1, line_num - context)
            eff_end = min(len(lines), line_num + context + 1)
            match_lines.extend(range(eff_start, eff_end))
    if match_lines:
        result = [f"\n=== {path} ==="] + [f"{line_num:4d}: {lines[line_num].strip()}" for line_num in match_lines]
        return "\n".join(result)
    return ""
        
