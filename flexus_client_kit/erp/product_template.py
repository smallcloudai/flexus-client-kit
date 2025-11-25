from dataclasses import dataclass
from typing import List
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
