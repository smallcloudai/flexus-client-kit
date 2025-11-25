from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class ProductTemplate:
    prodt_id: int
    prodt_name: str
    prodt_type: str
    prodt_pcat_id: int
    prodt_list_price: Decimal
    prodt_standard_price: Decimal
    prodt_uom_id: int
    prodt_active: bool


@dataclass
class ProductProduct:
    prod_id: int
    prodt_id: int
    prod_default_code: Optional[str]
    prod_barcode: Optional[str]
    prod_active: bool
    prodt: Optional[ProductTemplate] = None   # Optional not because it's not nullable, it's optional because you have an option to include or not include it when querying

