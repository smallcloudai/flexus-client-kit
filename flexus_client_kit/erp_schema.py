from dataclasses import dataclass, field
from typing import Optional, Dict, Type, List


def get_pkey_field(cls: Type) -> str:
    for name, f in cls.__dataclass_fields__.items():
        if f.metadata.get("pkey"):
            return name
    raise ValueError(f"No pkey field in {cls.__name__}")


def get_important_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("importance", 0) > 0]


def get_extra_search_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("extra_search")]


def get_field_display(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display") if f else None


def get_field_enum(cls: Type, field_name: str) -> Optional[List[str]]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("enum") if f else None


def get_field_display_name(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display_name") if f else None


def get_field_description(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("description") if f else None


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
    activity_type: str = field(metadata={"importance": 1, "display_name": "Type", "enum": ["WEB_CHAT", "MESSENGER_CHAT", "EMAIL", "CALL", "MEETING"]})
    activity_direction: str = field(metadata={"importance": 1, "display_name": "Direction", "enum": ["INBOUND", "OUTBOUND"]})
    activity_contact_id: str = field(metadata={"importance": 1, "display_name": "Contact"})
    activity_id: str = field(default="", metadata={"pkey": True, "display_name": "Activity ID"})
    activity_channel: str = field(default="", metadata={"importance": 1, "display_name": "Channel"})
    activity_ft_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Thread"})
    activity_summary: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Summary"})
    activity_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    activity_occurred_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Occurred at"})
    activity_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    activity_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class ProductTemplate:
    prodt_id: str = field(metadata={"pkey": True, "display_name": "Product Template ID"})
    prodt_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    prodt_description: str = field(metadata={"importance": 1, "display": "string_multiline", "display_name": "Description"})
    prodt_target_customers: str = field(metadata={"importance": 1, "display": "string_multiline", "display_name": "Target Customers"})
    prodt_type: str = field(metadata={"importance": 1, "display_name": "Type"})
    prodt_pcat_id: str = field(metadata={"display_name": "Category"})
    prodt_list_price: int = field(metadata={"importance": 1, "display_name": "List Price"})
    prodt_standard_price: int = field(metadata={"importance": 1, "display_name": "Standard Price"})
    prodt_uom_id: str = field(metadata={"display_name": "Unit of Measure"})
    prodt_active: bool = field(metadata={"importance": 1, "display_name": "Active"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    prodt_chips: List[str] = field(metadata={"importance": 1, "display_name": "Chips"})
    pcat: Optional['ProductCategory'] = field(default=None, metadata={"display_name": "Category"})
    uom: Optional['ProductUom'] = field(default=None, metadata={"display_name": "Unit of Measure"})


@dataclass
class ProductProduct:
    prod_id: str = field(metadata={"pkey": True, "display_name": "Product ID"})
    prodt_id: str = field(metadata={"importance": 1, "display_name": "Product Template"})
    prod_default_code: Optional[str] = field(metadata={"importance": 1, "display_name": "Internal Reference"})
    prod_barcode: Optional[str] = field(metadata={"importance": 1, "display_name": "Barcode"})
    prod_active: bool = field(metadata={"importance": 1, "display_name": "Active"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    prodt: Optional[ProductTemplate] = field(default=None, metadata={"display_name": "Product Template"})


@dataclass
class ProductCategory:
    pcat_id: str = field(metadata={"pkey": True, "display_name": "Category ID"})
    pcat_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    pcat_parent_id: Optional[str] = field(metadata={"importance": 1, "display_name": "Parent Category"})
    pcat_active: bool = field(metadata={"importance": 1, "display_name": "Active"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    parent: Optional['ProductCategory'] = field(default=None, metadata={"display_name": "Parent Category"})


@dataclass
class ProductTag:
    tag_id: str = field(metadata={"pkey": True, "display_name": "Tag ID"})
    tag_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    tag_sequence: int = field(metadata={"importance": 1, "display_name": "Sequence"})
    tag_color: str = field(metadata={"importance": 1, "display_name": "Color"})
    tag_visible_to_customers: bool = field(metadata={"importance": 1, "display_name": "Visible to Customers"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})


@dataclass
class ProductUom:
    uom_id: str = field(metadata={"pkey": True, "display_name": "UoM ID"})
    uom_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    uom_category_id: Optional[str] = field(metadata={"importance": 1, "display_name": "Category"})
    uom_active: bool = field(metadata={"importance": 1, "display_name": "Active"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    category: Optional[ProductCategory] = field(default=None, metadata={"display_name": "Category"})


@dataclass
class ProductM2mTemplateTag:
    id: str = field(metadata={"pkey": True, "display_name": "ID"})
    tag_id: str = field(metadata={"display_name": "Tag"})
    prodt_id: str = field(metadata={"display_name": "Product Template"})
    ws_id: str = field(metadata={"display_name": "Workspace ID"})
    tag: Optional[ProductTag] = field(default=None, metadata={"display_name": "Tag"})
    prodt: Optional['ProductTemplate'] = field(default=None, metadata={"display_name": "Product Template"})


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "crm_contact": CrmContact,
    "crm_activity": CrmActivity,
    "product_template": ProductTemplate,
    "product_product": ProductProduct,
    "product_category": ProductCategory,
    "product_tag": ProductTag,
    "product_uom": ProductUom,
    "product_m2m_template_tag": ProductM2mTemplateTag,
}

ERP_DISPLAY_NAME_CONFIGS: Dict[str, str] = {
    "crm_contact": "{contact_first_name} {contact_last_name}",
    "crm_activity": "{activity_title}",
    "product_template": "{prodt_name}",
    "product_product": "{prod_default_code} {prod_barcode}",
    "product_category": "{pcat_name}",
    "product_tag": "{tag_name}",
    "product_uom": "{uom_name}",
}
