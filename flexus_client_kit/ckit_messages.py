import json
import yaml
from typing import Optional, TypeVar

_M = TypeVar("_M")


def linearize_thread_messages(messages: list[_M], target_alt: int, target_num: int) -> list[_M]:
    by_key = {(m.ftm_alt, m.ftm_num): m for m in messages}
    chain, alt, num = [], target_alt, target_num
    while (alt, num) in by_key and num >= 0:
        m = by_key[(alt, num)]
        chain.append(m)
        alt, num = m.ftm_prev_alt, num - 1
    return list(reversed(chain))


def _truncate_content(raw_content: str, max_chars: int) -> str:
    def _truncate_mid(text):
        if not max_chars or len(text) <= max_chars:
            return text
        head = int(max_chars * 0.6)
        tail = max_chars - head
        return text[:head] + "\n\n...(truncated)...\n\n" + text[-tail:]

    def _format_img(item):
        src = item.get("source", {})
        media = src.get("media_type") or item.get("m_type") or "?"
        data_len = len(src.get("data", "") or item.get("m_content", ""))
        alt = item.get("alt", "")
        s = f"image ({media}, {data_len} bytes)"
        return s + f" alt={alt}" if alt else s

    try:
        content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
    except (json.JSONDecodeError, TypeError):
        return _truncate_mid(str(raw_content))
    if not isinstance(content, list):
        return _truncate_mid(str(content))
    parts = []
    for item in content:
        t = item.get("type") or item.get("m_type")
        if t == "text":
            parts.append(_truncate_mid(str(item.get("text", "") or item.get("m_content", ""))))
        elif t and t.startswith("image"):
            parts.append("[" + _format_img(item) + "]")
        else:
            parts.append(f"[{t}]")
    return "\n".join(parts)


def _truncate_tool_calls(raw_tool_calls: str | list, max_arg_chars: int) -> list[dict]:
    try:
        tcs = json.loads(raw_tool_calls) if isinstance(raw_tool_calls, str) else raw_tool_calls
    except (json.JSONDecodeError, TypeError):
        return []
    out = []
    for tc in tcs:
        fn = tc.get("function", {})
        name = fn.get("name", "?")
        args = fn.get("arguments", "")
        if max_arg_chars and len(args) > max_arg_chars:
            head = int(max_arg_chars * 0.6)
            tail = max_arg_chars - head
            args = args[:head] + "...(truncated)..." + args[-tail:]
        out.append({"name": name, "arguments": args})
    return out


def _represent_multiline_str(dumper: yaml.Dumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def yaml_dump_with_multiline(data) -> str:
    dumper = yaml.Dumper
    dumper.add_representer(str, _represent_multiline_str)
    return yaml.dump(data, Dumper=dumper, default_flow_style=False, allow_unicode=True, width=100, sort_keys=False)


# limits keys: "user", "assistant", "tool" for content truncation, "tool_args" for tool call arguments
def fmessages_to_yaml(messages: list, *, limits: Optional[dict[str, int]] = None) -> str:
    limits = limits or {}
    out = []
    for msg in messages:
        m = {"role": msg.ftm_role}
        if getattr(msg, "ftm_author_label1", ""):
            m["author_label1"] = msg.ftm_author_label1
        if getattr(msg, "ftm_author_label2", ""):
            m["author_label2"] = msg.ftm_author_label2
        if msg.ftm_content and msg.ftm_content != "null":
            max_chars = limits.get(msg.ftm_role)
            if max_chars:
                m["content"] = _truncate_content(msg.ftm_content, max_chars)
            else:
                m["content"] = msg.ftm_content
        if msg.ftm_tool_calls and msg.ftm_tool_calls not in ("null", "[]"):
            arg_max = limits.get("tool_args")
            if arg_max:
                m["tool_calls"] = _truncate_tool_calls(msg.ftm_tool_calls, arg_max)
            else:
                m["tool_calls"] = msg.ftm_tool_calls
        if msg.ftm_call_id:
            m["call_id"] = msg.ftm_call_id
        out.append(m)
    return yaml_dump_with_multiline({"messages": out})
