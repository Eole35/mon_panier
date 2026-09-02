"""Repository for Mon Panier data."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from ..const import (
    UNIT_PIECE,
)
from .models import (
    CategoryOverride,
    HistoryEntry,
    ListItem,
    MonPanierData,
    PersonalRule,
    Product,
    ShoppingList,
    Store,
)


class MonPanierRepository:
    """Manage Mon Panier data."""

    def __init__(self, data: MonPanierData | None = None) -> None:
        """Initialize the repository."""
        self.data = data or MonPanierData()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _new_id() -> str:
        """Generate a unique identifier."""
        return uuid4().hex[:8]

    # -------------------------------------------------------------------------
    # Stores
    # -------------------------------------------------------------------------

    def create_store(self, name: str, store_id: str | None = None) -> Store:
        """Create a store and its shopping list."""
        store = Store(
            id=store_id or self._slugify(name),
            name=name,
        )

        self.data.stores.append(store)

        self.data.lists.append(
            ShoppingList(
                id=store.id,
                store_id=store.id,
            )
        )

        return store

    def get_store(self, store_id: str) -> Store | None:
        """Return a store by ID."""
        return next(
            (store for store in self.data.stores if store.id == store_id),
            None,
        )

    def get_stores(self) -> list[Store]:
        """Return all stores."""
        return list(self.data.stores)

    def rename_store(self, store_id: str, name: str) -> Store:
        """Rename a store."""
        store = self._require_store(store_id)
        store.name = name
        return store

    def delete_store(self, store_id: str) -> None:
        """Delete a store and its shopping list."""
        store = self._require_store(store_id)

        self.data.stores.remove(store)

        shopping_list = self.get_list(store_id)
        if shopping_list:
            self.data.lists.remove(shopping_list)

    # -------------------------------------------------------------------------
    # Shopping lists
    # -------------------------------------------------------------------------

    def get_list(self, store_id: str) -> ShoppingList | None:
        """Return the shopping list for a store."""
        return next(
            (
                shopping_list
                for shopping_list in self.data.lists
                if shopping_list.store_id == store_id
            ),
            None,
        )

    def clear_list(self, store_id: str) -> None:
        """Remove all items from a shopping list."""
        shopping_list = self._require_list(store_id)
        shopping_list.items.clear()

    def delete_list(self, store_id: str) -> None:
        """Delete a shopping list without deleting the store."""
        shopping_list = self._require_list(store_id)
        self.data.lists.remove(shopping_list)

    # -------------------------------------------------------------------------
    # Products
    # -------------------------------------------------------------------------

    def add_product(
        self,
        name: str,
        category: str,
        *,
        product_id: str | None = None,
        synonyms: list[str] | None = None,
        source: str = "personal",
    ) -> Product:
        """Add a product."""
        product = Product(
            id=product_id or self._slugify(name),
            name=name,
            category=category,
            synonyms=synonyms or [],
            source=source,
        )

        self.data.products.append(product)

        return product

    def get_product(self, product_id: str) -> Product | None:
        """Return a product by ID."""
        return next(
            (
                product
                for product in self.data.products
                if product.id == product_id
            ),
            None,
        )

    def get_products(self) -> list[Product]:
        """Return all products."""
        return list(self.data.products)

    def set_product_favorite(
        self,
        product_id: str,
        favorite: bool,
    ) -> Product:
        """Set the favorite state of a product."""
        product = self._require_product(product_id)
        product.favorite = favorite
        return product

    def add_barcode(
        self,
        product_id: str,
        barcode: str,
    ) -> Product:
        """Associate a barcode with a product."""
        product = self._require_product(product_id)

        if barcode not in product.barcodes:
            product.barcodes.append(barcode)

        return product

    # -------------------------------------------------------------------------
    # List items
    # -------------------------------------------------------------------------

    def add_item(
        self,
        store_id: str,
        product_id: str,
        *,
        quantity: float = 1,
        unit: str = UNIT_PIECE,
        bio: bool = False,
        promotion: bool = False,
        large_quantity: bool = False,
    ) -> ListItem:
        """Add an item to a shopping list."""
        shopping_list = self._require_list(store_id)

        existing_item = self._find_compatible_item(
            shopping_list,
            product_id,
            unit,
            bio,
            promotion,
            large_quantity,
        )

        if existing_item:
            existing_item.quantity += quantity
            return existing_item

        item = ListItem(
            id=self._new_id(),
            product_id=product_id,
            quantity=quantity,
            unit=unit,
            bio=bio,
            promotion=promotion,
            large_quantity=large_quantity,
            created_at=datetime.now(),
        )

        shopping_list.items.append(item)

        return item

    def remove_item(
        self,
        store_id: str,
        item_id: str,
    ) -> None:
        """Remove an item from a shopping list."""
        shopping_list = self._require_list(store_id)

        item = next(
            (
                item
                for item in shopping_list.items
                if item.id == item_id
            ),
            None,
        )

        if item is None:
            raise ValueError(f"Unknown item: {item_id}")

        shopping_list.items.remove(item)

    def update_item(
        self,
        store_id: str,
        item_id: str,
        *,
        quantity: float | None = None,
        unit: str | None = None,
        bio: bool | None = None,
        promotion: bool | None = None,
        large_quantity: bool | None = None,
    ) -> ListItem:
        """Update an item."""
        item = self._require_item(store_id, item_id)

        if quantity is not None:
            item.quantity = quantity

        if unit is not None:
            item.unit = unit

        if bio is not None:
            item.bio = bio

        if promotion is not None:
            item.promotion = promotion

        if large_quantity is not None:
            item.large_quantity = large_quantity

        return item

    def complete_item(
        self,
        store_id: str,
        item_id: str,
    ) -> ListItem:
        """Mark an item as purchased."""
        item = self._require_item(store_id, item_id)

        if item.checked:
            return item

        item.checked = True

        product = self.get_product(item.product_id)

        if product:
            product.purchase_count += 1
            product.last_purchased = datetime.now()

            store = self._require_store(store_id)

            self.data.history.append(
                HistoryEntry(
                    id=self._new_id(),
                    date=datetime.now(),
                    store_id=store.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item.quantity,
                    unit=item.unit,
                    bio=item.bio,
                    promotion=item.promotion,
                    large_quantity=item.large_quantity,
                )
            )

        return item

    def uncomplete_item(
        self,
        store_id: str,
        item_id: str,
    ) -> ListItem:
        """Mark an item as not purchased."""
        item = self._require_item(store_id, item_id)
        item.checked = False
        return item

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------

    def get_history(self) -> list[HistoryEntry]:
        """Return purchase history."""
        return list(self.data.history)

    # -------------------------------------------------------------------------
    # Learning
    # -------------------------------------------------------------------------

    def add_personal_rule(
        self,
        input_text: str,
        product_id: str,
    ) -> PersonalRule:
        """Add a personal search rule."""
        rule = PersonalRule(
            input_text=input_text,
            product_id=product_id,
        )

        self.data.personal_rules.append(rule)

        return rule

    def get_personal_rules(self) -> list[PersonalRule]:
        """Return personal rules."""
        return list(self.data.personal_rules)

    def add_category_override(
        self,
        product_id: str,
        category: str,
    ) -> CategoryOverride:
        """Add or update a category override."""
        existing = next(
            (
                override
                for override in self.data.category_overrides
                if override.product_id == product_id
            ),
            None,
        )

        if existing:
            existing.category = category
            return existing

        override = CategoryOverride(
            product_id=product_id,
            category=category,
        )

        self.data.category_overrides.append(override)

        return override

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return repository data as a dictionary."""
        return self.data.to_dict()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _require_store(self, store_id: str) -> Store:
        """Return a store or raise an error."""
        store = self.get_store(store_id)

        if store is None:
            raise ValueError(f"Unknown store: {store_id}")

        return store

    def _require_list(self, store_id: str) -> ShoppingList:
        """Return a shopping list or raise an error."""
        shopping_list = self.get_list(store_id)

        if shopping_list is None:
            raise ValueError(f"Unknown shopping list: {store_id}")

        return shopping_list

    def _require_product(self, product_id: str) -> Product:
        """Return a product or raise an error."""
        product = self.get_product(product_id)

        if product is None:
            raise ValueError(f"Unknown product: {product_id}")

        return product

    def _require_item(
        self,
        store_id: str,
        item_id: str,
    ) -> ListItem:
        """Return an item or raise an error."""
        shopping_list = self._require_list(store_id)

        item = next(
            (
                item
                for item in shopping_list.items
                if item.id == item_id
            ),
            None,
        )

        if item is None:
            raise ValueError(f"Unknown item: {item_id}")

        return item

    @staticmethod
    def _find_compatible_item(
        shopping_list: ShoppingList,
        product_id: str,
        unit: str,
        bio: bool,
        promotion: bool,
        large_quantity: bool,
    ) -> ListItem | None:
        """Find an existing compatible item."""
        for item in shopping_list.items:
            if (
                item.product_id == product_id
                and item.unit == unit
                and item.bio == bio
                and item.promotion == promotion
                and item.large_quantity == large_quantity
                and not item.checked
            ):
                return item

        return None

    @staticmethod
    def _slugify(value: str) -> str:
        """Create a simple stable identifier."""
        normalized = value.strip().lower()

        replacements = {
            "à": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ö": "o",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ÿ": "y",
            "ç": "c",
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        result = "".join(
            character if character.isalnum() else "_"
            for character in normalized
        )

        return "_".join(part for part in result.split("_") if part)
