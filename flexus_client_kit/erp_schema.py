import dataclasses
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Type, List


@dataclass
class CrmContact:
    ws_id: str
    contact_first_name: str = field(metadata={"importance": 1, "display_name": "First Name"})
    contact_last_name: str = field(metadata={"importance": 1, "display_name": "Last Name"})
    contact_email: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Email"})
    contact_phone: str = field(default="", metadata={"display_name": "Phone"})
    contact_id: str = field(default="", metadata={"pkey": True, "display_name": "Contact ID"})
    contact_notes: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes"})
    contact_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "description": "Custom JSON data: BANT qualification reasons, social profiles, preferences, custom attributes"})
    contact_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    contact_address_line1: str = field(default="", metadata={"display_name": "Address Line 1"})
    contact_address_line2: str = field(default="", metadata={"display_name": "Address Line 2"})
    contact_address_city: str = field(default="", metadata={"display_name": "City"})
    contact_address_state: str = field(default="", metadata={"display_name": "State"})
    contact_address_zip: str = field(default="", metadata={"display_name": "ZIP Code"})
    contact_address_country: str = field(default="", metadata={"importance": 1, "display_name": "Country"})
    contact_utm_first_source: str = field(default="", metadata={"importance": 1, "display_name": "UTM Source (first touch)", "description": "First marketing interaction that brought this contact"})
    contact_utm_first_medium: str = field(default="", metadata={"display_name": "UTM Medium (first touch)"})
    contact_utm_first_campaign: str = field(default="", metadata={"display_name": "UTM Campaign (first touch)"})
    contact_utm_first_term: str = field(default="", metadata={"display_name": "UTM Term (first touch)"})
    contact_utm_first_content: str = field(default="", metadata={"display_name": "UTM Content (first touch)"})
    contact_utm_last_source: str = field(default="", metadata={"display_name": "UTM Source (last touch)", "description": "Most recent marketing interaction"})
    contact_utm_last_medium: str = field(default="", metadata={"display_name": "UTM Medium (last touch)"})
    contact_utm_last_campaign: str = field(default="", metadata={"display_name": "UTM Campaign (last touch)"})
    contact_utm_last_term: str = field(default="", metadata={"display_name": "UTM Term (last touch)"})
    contact_utm_last_content: str = field(default="", metadata={"display_name": "UTM Content (last touch)"})
    contact_bant_score: int = field(default=-1, metadata={"display_name": "BANT Qualification Score", "description": "Budget, Authority, Need, Timeline. -1 means not qualified, 0-4 scale"})
    contact_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    contact_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    contact_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class CrmActivity:
    ws_id: str
    activity_title: str = field(metadata={"importance": 1, "display_name": "Title"})
    activity_type: str = field(metadata={"importance": 1, "display_name": "Type", "enum": [
        {"value": "WEB_CHAT", "label": "Web Chat"},
        {"value": "MESSENGER_CHAT", "label": "Messenger Chat"},
        {"value": "EMAIL", "label": "Email"},
        {"value": "CALL", "label": "Call"},
        {"value": "MEETING", "label": "Meeting"},
    ]})
    activity_direction: str = field(metadata={"importance": 1, "display_name": "Direction", "enum": [
        {"value": "INBOUND", "label": "Inbound"},
        {"value": "OUTBOUND", "label": "Outbound"},
    ]})
    activity_contact_id: str = field(metadata={"importance": 1, "display_name": "Contact"})
    activity_id: str = field(default="", metadata={"pkey": True, "display_name": "Activity ID"})
    activity_platform: str = field(default="", metadata={"importance": 1, "display_name": "Channel"})
    activity_ft_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Thread"})
    activity_summary: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Summary"})
    activity_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    activity_occurred_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Occurred at"})
    activity_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    activity_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class ProductTemplate:
    prodt_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    prodt_pcat_id: str = field(metadata={"display_name": "Category"})
    prodt_list_price: Decimal = field(metadata={"importance": 1, "display_name": "List Price"})
    prodt_standard_price: Decimal = field(metadata={"importance": 1, "display_name": "Standard Price"})
    prodt_uom_id: str = field(metadata={"display_name": "Unit of Measure"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    prodt_id: str = field(default="", metadata={"pkey": True, "display_name": "Product Template ID"})
    prodt_description: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Description"})
    prodt_target_customers: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Target Customers"})
    prodt_type: str = field(default="consu", metadata={"importance": 1, "display_name": "Type"})
    prodt_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    prodt_chips: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Chips"})
    pcat: Optional['ProductCategory'] = field(default=None, metadata={"display_name": "Category"})
    uom: Optional['ProductUom'] = field(default=None, metadata={"display_name": "Unit of Measure"})


@dataclass
class ProductProduct:
    prodt_id: str = field(metadata={"importance": 1, "display_name": "Product Template"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    prod_id: str = field(default="", metadata={"pkey": True, "display_name": "Product ID"})
    prod_default_code: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Internal Reference"})
    prod_barcode: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Barcode"})
    prod_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    prodt: Optional[ProductTemplate] = field(default=None, metadata={"display_name": "Product Template"})


@dataclass
class ProductCategory:
    pcat_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    pcat_id: str = field(default="", metadata={"pkey": True, "display_name": "Category ID"})
    pcat_parent_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Parent Category"})
    pcat_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    parent: Optional['ProductCategory'] = field(default=None, metadata={"display_name": "Parent Category"})


@dataclass
class ProductTag:
    tag_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    tag_id: str = field(default="", metadata={"pkey": True, "display_name": "Tag ID"})
    tag_sequence: int = field(default=10, metadata={"importance": 1, "display_name": "Sequence"})
    tag_color: str = field(default="#3C3C3C", metadata={"importance": 1, "display_name": "Color"})
    tag_visible_to_customers: bool = field(default=True, metadata={"importance": 1, "display_name": "Visible to Customers"})


@dataclass
class ProductUom:
    uom_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    uom_id: str = field(default="", metadata={"pkey": True, "display_name": "UoM ID"})
    uom_category_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Category"})
    uom_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    category: Optional[ProductCategory] = field(default=None, metadata={"display_name": "Category"})


@dataclass
class ProductM2mTemplateTag:
    tag_id: str = field(metadata={"display_name": "Tag"})
    prodt_id: str = field(metadata={"display_name": "Product Template"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    id: str = field(default="", metadata={"pkey": True, "display_name": "ID"})
    tag: Optional[ProductTag] = field(default=None, metadata={"display_name": "Tag"})
    prodt: Optional['ProductTemplate'] = field(default=None, metadata={"display_name": "Product Template"})


@dataclass
class CrmPipeline:
    ws_id: str
    pipeline_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    pipeline_id: str = field(default="", metadata={"pkey": True, "display_name": "Pipeline ID"})
    pipeline_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    pipeline_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    pipeline_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    pipeline_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class CrmPipelineStage:
    ws_id: str
    stage_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    stage_pipeline_id: str = field(metadata={"importance": 1, "display_name": "Pipeline"})
    stage_id: str = field(default="", metadata={"pkey": True, "display_name": "Stage ID"})
    stage_sequence: int = field(default=0, metadata={"display_name": "Sequence"})
    stage_probability: int = field(default=0, metadata={"importance": 1, "display_name": "Win Probability %", "description": "0-100 win probability percentage"})
    stage_status: str = field(default="OPEN", metadata={"importance": 1, "display_name": "Status", "enum": [{"value": "OPEN", "label": "Open"}, {"value": "WON", "label": "Won"}, {"value": "LOST", "label": "Lost"}]})
    stage_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    stage_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class CrmDeal:
    ws_id: str
    deal_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    deal_pipeline_id: str = field(metadata={"importance": 1, "display_name": "Pipeline"})
    deal_stage_id: str = field(metadata={"importance": 1, "display_name": "Stage", "fk_scope": {"stage_pipeline_id": "deal_pipeline_id"}})
    deal_id: str = field(default="", metadata={"pkey": True, "display_name": "Deal ID"})
    deal_contact_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Contact"})
    deal_value: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Value"})
    deal_expected_close_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Expected Close"})
    deal_closed_ts: float = field(default=0.0, metadata={"display_name": "Closed at"})
    deal_lost_reason: str = field(default="", metadata={"display_name": "Lost Reason"})
    deal_notes: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes"})
    deal_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    deal_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "description": "Custom fields JSON"})
    deal_owner_fuser_id: str = field(default="", metadata={"display_name": "Owner"})
    deal_priority: str = field(default="NONE", metadata={"importance": 1, "display_name": "Priority", "enum": [{"value": "NONE", "label": "None"}, {"value": "LOW", "label": "Low"}, {"value": "MEDIUM", "label": "Medium"}, {"value": "HIGH", "label": "High"}]})
    deal_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    deal_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    deal_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "crm_contact": CrmContact,
    "crm_activity": CrmActivity,
    "product_template": ProductTemplate,
    "product_product": ProductProduct,
    "product_category": ProductCategory,
    "product_tag": ProductTag,
    "product_uom": ProductUom,
    "product_m2m_template_tag": ProductM2mTemplateTag,
    "crm_pipeline": CrmPipeline,
    "crm_pipeline_stage": CrmPipelineStage,
    "crm_deal": CrmDeal,
}

ERP_DISPLAY_NAME_CONFIGS: Dict[str, str] = {
    "crm_contact": "{contact_first_name} {contact_last_name}",
    "crm_activity": "{activity_title}",
    "product_template": "{prodt_name}",
    "product_product": "{prod_default_code} {prod_barcode}",
    "product_category": "{pcat_name}",
    "product_tag": "{tag_name}",
    "product_uom": "{uom_name}",
    "crm_pipeline": "{pipeline_name}",
    "crm_pipeline_stage": "{stage_name}",
    "crm_deal": "{deal_name}",
}


def get_pkey_field(cls: Type) -> str:
    for name, f in cls.__dataclass_fields__.items():
        if f.metadata.get("pkey"):
            return name
    raise ValueError(f"No pkey field in {cls.__name__}")


def get_required_fields(cls: Type) -> List[str]:
    pkey = get_pkey_field(cls)
    return [
        name for name, f in cls.__dataclass_fields__.items()
        if name != "ws_id" and name != pkey
        and f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    ]


def get_important_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("importance", 0) > 0]


def get_extra_search_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("extra_search")]


def get_field_display(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display") if f else None


def get_field_enum(cls: Type, field_name: str) -> Optional[List[Dict[str, str]]]:
    f = cls.__dataclass_fields__.get(field_name)
    return (f.metadata.get("enum") if f else None) or None


def get_field_display_name(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display_name") if f else None


def get_field_description(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("description") if f else None


def get_field_fk_scope(cls: Type, field_name: str) -> Optional[Dict[str, str]]:
    f = cls.__dataclass_fields__.get(field_name)
    return (f.metadata.get("fk_scope") if f else None) or None
