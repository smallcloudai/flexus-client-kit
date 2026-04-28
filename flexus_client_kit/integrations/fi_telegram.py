import re
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_ask_model


# https://core.telegram.org/bots/api#formatting-options
TG_MARKUP_HELP = """
Telegram uses MarkdownV2 markup:

*bold*  _italic_  __underline__  ~strikethrough~
`inline code`
```python
code block
```
[link text](https://example.com)
||spoiler||

> blockquote
> each line must start with >

No bullet lists or tables.
"""


_TG_MD2_SPECIAL = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\<>])")
_TG_MD2_CODE_ESCAPE = re.compile(r"([`\\])")
_TG_MD2_LINK_URL_ESCAPE = re.compile(r"([)\\])")
_TG_MD2_MARKUP = re.compile(
    r"(?sm)"
    r"```.*?```"             # code blocks
    r"|`[^`]+`"              # inline code
    r"|\*[^*\n]+\*"          # bold (no newline crossing)
    r"|(?<!\w)__[^_\n]+__(?!\w)"  # underline (word-boundary, before italic)
    r"|(?<!\w)_[^_\n]+_(?!\w)"    # italic (word-boundary, like Telegram's parser)
    r"|~[^~\n]+~"            # strikethrough
    r"|\|\|[^|\n]+\|\|"     # spoiler
    r"|\[[^\]]+\]\([^)]*(?:\([^)]*\)[^)]*)*\)"  # links (supports one level of parens in URL)
    r"|^>[^\n]*"             # blockquote lines (only at line start)
)


def _escape_markup_match(m: re.Match) -> str:
    s = m.group(0)
    if s.startswith("```"):
        inner = s[3:-3]
        return "```" + _TG_MD2_CODE_ESCAPE.sub(r"\\\1", inner) + "```"
    if s.startswith("`"):
        inner = s[1:-1]
        return "`" + _TG_MD2_CODE_ESCAPE.sub(r"\\\1", inner) + "`"
    if s.startswith("["):
        bracket_end = s.index("](")
        text_part = s[1:bracket_end]
        url_part = s[bracket_end+2:-1]
        return "[" + _TG_MD2_SPECIAL.sub(r"\\\1", text_part) + "](" + _TG_MD2_LINK_URL_ESCAPE.sub(r"\\\1", url_part) + ")"
    if s.startswith(">"):
        return ">" + _TG_MD2_SPECIAL.sub(r"\\\1", s[1:])
    for delim in ("__", "||", "*", "_", "~"):
        if s.startswith(delim) and s.endswith(delim) and len(s) > 2 * len(delim):
            inner = s[len(delim):-len(delim)]
            return delim + _TG_MD2_SPECIAL.sub(r"\\\1", inner) + delim
    return s


def tg_escape_md2(text: str) -> str:
    parts = []
    last = 0
    for m in _TG_MD2_MARKUP.finditer(text):
        if m.start() > last:
            parts.append(_TG_MD2_SPECIAL.sub(r"\\\1", text[last:m.start()]))
        parts.append(_escape_markup_match(m))
        last = m.end()
    if last < len(text):
        parts.append(_TG_MD2_SPECIAL.sub(r"\\\1", text[last:]))
    return "".join(parts)


def _ftm_content_to_text(content: Any) -> str:
    if isinstance(content, list):
        return "\n\n".join(p.get("m_content", "") for p in content if isinstance(p, dict) and p.get("m_type") == "text")
    return content or ""


def ftm_to_mtm(ftm: ckit_ask_model.FThreadMessageOutput) -> Optional[Dict[str, Any]]:
    text = _ftm_content_to_text(ftm.ftm_content)
    for marker in ("TASK_COMPLETED", "NOTHING_TO_SAY"):
        if marker in text and len(text) <= len(marker) + 6:
            return None
        text = text.replace(marker, "")
    if not text.strip():
        return None
    # XXX images in ftm.ftm_content (m_type=image/*) need to be uploaded via chat_image_add and put into attachments.
    return {
        "text": tg_escape_md2(text),
        "attachments": [],
        "reply_to": "",
    }
