"""Product catalog for Mon Panier."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Product


class ProductCatalog:
    """Load and provide access to the builtin product catalog."""

    def __init__(self, products: list[Product] | None = None) -> None:
        """Initialize the catalog."""
        self._products = products or []

    @classmethod
    def from_file(cls, path: Path) -> ProductCatalog:
        """Load products from a JSON file."""
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        products = [
            Product(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                synonyms=item.get("synonyms", []),
                source=item.get("source", "builtin"),
                favorite=item.get("favorite", False),
                purchase_count=item.get("purchase_count", 0),
                barcodes=item.get("barcodes", []),
            )
            for item in data
        ]

        return cls(products)

    def get_products(self) -> list[Product]:
        """Return all catalog products."""
        return list(self._products)

    def get_product(self, product_id: str) -> Product | None:
        """Return a product by its identifier."""
        return next(
            (
                product
                for product in self._products
                if product.id == product_id
            ),
            None,
        )

    def find_by_barcode(self, barcode: str) -> Product | None:
        """Return a product matching a barcode."""
        return next(
            (
                product
                for product in self._products
                if barcode in product.barcodes
            ),
            None,
        )

    def add_product(self, product: Product) -> None:
        """Add a product to the catalog."""
        if self.get_product(product.id) is None:
            self._products.append(product)
