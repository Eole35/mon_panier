"""Data models for Mon Panier."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..const import SOURCE_PERSONAL, UNIT_PIECE


@dataclass
class Product:
    """A generic product."""

    id: str
    name: str
    category: str
    synonyms: list[str] = field(default_factory=list)
    source: str = SOURCE_PERSONAL
    favorite: bool = False
    purchase_count: int = 0
    last_purchased: datetime | None = None
    barcodes: list[str] = field(default_factory=list)


@dataclass
class ListItem:
    """An item in a shopping list."""

    id: str
    product_id: str
    quantity: float = 1
    unit: str = UNIT_PIECE
    bio: bool = False
    promotion: bool = False
    large_quantity: bool = False
    checked: bool = False
    created_at: datetime | None = None


@dataclass
class ShoppingList:
    """A shopping list belonging to a store."""

    id: str
    store_id: str
    items: list[ListItem] = field(default_factory=list)


@dataclass
class Store:
    """A Mon Panier store."""

    id: str
    name: str
    category_order: list[str] = field(default_factory=list)


@dataclass
class HistoryEntry:
    """A purchased item stored in history."""

    id: str
    date: datetime
    store_id: str
    product_id: str
    product_name: str
    quantity: float
    unit: str
    bio: bool = False
    promotion: bool = False
    large_quantity: bool = False


@dataclass
class PersonalRule:
    """A personal learning rule."""

    input_text: str
    product_id: str


@dataclass
class CategoryOverride:
    """A personal category override."""

    product_id: str
    category: str


@dataclass
class MonPanierData:
    """Complete persistent data for Mon Panier."""

    schema_version: int = 1
    stores: list[Store] = field(default_factory=list)
    lists: list[ShoppingList] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)
    history: list[HistoryEntry] = field(default_factory=list)
    personal_rules: list[PersonalRule] = field(default_factory=list)
    category_overrides: list[CategoryOverride] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the data to a dictionary."""
        return {
            "schema_version": self.schema_version,
            "stores": [
                {
                    "id": store.id,
                    "name": store.name,
                    "category_order": store.category_order,
                }
                for store in self.stores
            ],
            "lists": [
                {
                    "id": shopping_list.id,
                    "store_id": shopping_list.store_id,
                    "items": [
                        {
                            "id": item.id,
                            "product_id": item.product_id,
                            "quantity": item.quantity,
                            "unit": item.unit,
                            "bio": item.bio,
                            "promotion": item.promotion,
                            "large_quantity": item.large_quantity,
                            "checked": item.checked,
                            "created_at": (
                                item.created_at.isoformat()
                                if item.created_at
                                else None
                            ),
                        }
                        for item in shopping_list.items
                    ],
                }
                for shopping_list in self.lists
            ],
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "synonyms": product.synonyms,
                    "source": product.source,
                    "favorite": product.favorite,
                    "purchase_count": product.purchase_count,
                    "last_purchased": (
                        product.last_purchased.isoformat()
                        if product.last_purchased
                        else None
                    ),
                    "barcodes": product.barcodes,
                }
                for product in self.products
            ],
            "history": [
                {
                    "id": entry.id,
                    "date": entry.date.isoformat(),
                    "store_id": entry.store_id,
                    "product_id": entry.product_id,
                    "product_name": entry.product_name,
                    "quantity": entry.quantity,
                    "unit": entry.unit,
                    "bio": entry.bio,
                    "promotion": entry.promotion,
                    "large_quantity": entry.large_quantity,
                }
                for entry in self.history
            ],
            "personal_rules": [
                {
                    "input_text": rule.input_text,
                    "product_id": rule.product_id,
                }
                for rule in self.personal_rules
            ],
            "category_overrides": [
                {
                    "product_id": override.product_id,
                    "category": override.category,
                }
                for override in self.category_overrides
            ],
        }
