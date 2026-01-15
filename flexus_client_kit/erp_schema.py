import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Type, List

pk = {"pk": True}
view_default = {"view_default": True}
extra_search = {"extra_search": True}
display_multiline = {"display": "string_multiline"}


def get_pk_field(cls: Type) -> str:
    for name, f in cls.__dataclass_fields__.items():
        if f.metadata.get("pk"):
            return name
    raise ValueError(f"No pk field in {cls.__name__}")


def get_view_default_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("view_default")]


def get_extra_search_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("extra_search")]


def get_field_display(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display") if f else None


@dataclass
class CrmContact:
    ws_id: str
    contact_first_name: str = field(metadata=view_default)
    contact_last_name: str = field(metadata=view_default)
    contact_email: str = field(metadata=view_default | extra_search)
    contact_id: str = field(default="", metadata=pk)
    contact_notes: str = field(default="", metadata=view_default | display_multiline)
    contact_details: dict = field(default_factory=dict)
    contact_tags: List[str] = field(default_factory=list, metadata=view_default)
    contact_address_line1: str = ""
    contact_address_line2: str = ""
    contact_address_city: str = ""
    contact_address_state: str = ""
    contact_address_zip: str = ""
    contact_address_country: str = field(default="", metadata=view_default)
    contact_utm_first_source: str = field(default="", metadata=view_default)
    contact_utm_first_medium: str = ""
    contact_utm_first_campaign: str = ""
    contact_utm_first_term: str = ""
    contact_utm_first_content: str = ""
    contact_utm_last_source: str = ""
    contact_utm_last_medium: str = ""
    contact_utm_last_campaign: str = ""
    contact_utm_last_term: str = ""
    contact_utm_last_content: str = ""
    contact_bant_score: int = -1
    contact_created_ts: float = field(default=0.0, metadata=view_default)
    contact_modified_ts: float = 0.0
    contact_archived_ts: float = 0.0


@dataclass
class CrmTask:
    ws_id: str
    contact_id: str = field(metadata=view_default)
    task_type: str = field(metadata=view_default)
    task_title: str = field(metadata=view_default)
    task_notes: str = field(default="", metadata=view_default | display_multiline)
    task_details: dict = field(default_factory=dict)
    task_id: str = field(default="", metadata=pk)
    task_due_ts: float = field(default=0.0, metadata=view_default)
    task_completed_ts: float = field(default=0.0, metadata=view_default)
    task_created_ts: float = field(default_factory=time.time)
    task_modified_ts: float = field(default_factory=time.time)
    contact: Optional['CrmContact'] = None


@dataclass
class ProductTemplate:
    prodt_id: str = field(metadata=pk)
    prodt_name: str = field(metadata=view_default)
    prodt_description: str = field(metadata=view_default | display_multiline)
    prodt_target_customers: str = field(metadata=view_default | display_multiline)
    prodt_type: str = field(metadata=view_default)
    prodt_pcat_id: str
    prodt_list_price: int = field(metadata=view_default)  # stored in cents
    prodt_standard_price: int = field(metadata=view_default)  # stored in cents
    prodt_uom_id: str
    prodt_active: bool = field(metadata=view_default)
    ws_id: str
    prodt_chips: List[str] = field(metadata=view_default)
    pcat: Optional['ProductCategory'] = None
    uom: Optional['ProductUom'] = None


@dataclass
class ProductProduct:
    prod_id: str = field(metadata=pk)
    prodt_id: str = field(metadata=view_default)
    prod_default_code: Optional[str] = field(metadata=view_default)
    prod_barcode: Optional[str] = field(metadata=view_default)
    prod_active: bool = field(metadata=view_default)
    ws_id: str
    prodt: Optional[ProductTemplate] = None  # optional because you have an option to include or not include it when querying


@dataclass
class ProductCategory:
    pcat_id: str = field(metadata=pk)
    pcat_name: str = field(metadata=view_default)
    pcat_parent_id: Optional[str] = field(metadata=view_default)
    pcat_active: bool = field(metadata=view_default)
    ws_id: str
    parent: Optional['ProductCategory'] = None


@dataclass
class ProductTag:
    tag_id: str = field(metadata=pk)
    tag_name: str = field(metadata=view_default)
    tag_sequence: int = field(metadata=view_default)
    tag_color: str = field(metadata=view_default)
    tag_visible_to_customers: bool = field(metadata=view_default)
    ws_id: str


@dataclass
class ProductUom:
    uom_id: str = field(metadata=pk)
    uom_name: str = field(metadata=view_default)
    uom_category_id: Optional[str] = field(metadata=view_default)
    uom_active: bool = field(metadata=view_default)
    ws_id: str
    category: Optional[ProductCategory] = None


@dataclass
class ProductM2mTemplateTag:
    id: str = field(metadata=pk)
    tag_id: str
    prodt_id: str
    ws_id: str
    tag: Optional[ProductTag] = None
    prodt: Optional['ProductTemplate'] = None


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "crm_contact": CrmContact,
    "crm_task": CrmTask,
    "product_template": ProductTemplate,
    "product_product": ProductProduct,
    "product_category": ProductCategory,
    "product_tag": ProductTag,
    "product_uom": ProductUom,
    "product_m2m_template_tag": ProductM2mTemplateTag,
}

ERP_DISPLAY_NAME_CONFIGS: Dict[str, str] = {
    "crm_contact": "{contact_first_name} {contact_last_name}",
    "crm_task": "{task_title}",
    "product_template": "{prodt_name}",
    "product_product": "{prod_default_code} {prod_barcode}",
    "product_category": "{pcat_name}",
    "product_tag": "{tag_name}",
    "product_uom": "{uom_name}",
}

