import logging
from typing import Any, Dict, Tuple

REPORT_TYPES = {}
logger = logging.getLogger("report")


def register_report(
        report_type: str,
        sections: Dict[str, Any],
        template: str,
        description: str
):
    REPORT_TYPES[report_type] = {
        "sections": sections,
        "template": template,
        "description": description,
    }
    logger.info(f"Registered report type {report_type} with description {description}")


def load_report_config(report_type: str) -> Tuple[Dict[str, Any], str]:
    if report_type not in REPORT_TYPES:
        available = list_available_reports()
        types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
        raise f"Error: Unknown report_type '{report_type}'.\n\nAvailable report types:\n{types_list}"
    return REPORT_TYPES[report_type]["sections"], REPORT_TYPES[report_type]["template"]


def list_available_reports():
    return [(k, v.get("description", "")) for k, v in REPORT_TYPES.items()]
