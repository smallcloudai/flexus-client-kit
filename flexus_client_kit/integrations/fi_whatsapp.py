from typing import Any, Dict, Optional

from flexus_client_kit import ckit_ask_model


# https://faq.whatsapp.com/539178204879377
WA_MARKUP_HELP = """
WhatsApp uses simple inline markup:

*bold*  _italic_  ~strikethrough~
```monospace```

No links with custom text, no headers, no tables, no bullet lists.
"""


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
    # XXX images in ftm.ftm_content (m_type=image/*) need upload via /messages with type=image link.
    return {
        "text": text,
        "attachments": [],
        "reply_to": "",
    }
