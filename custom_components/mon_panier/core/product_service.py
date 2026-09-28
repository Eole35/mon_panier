"""Product service for Mon Panier."""

from __future__ import annotations

from dataclasses import dataclass

from ..barcode import BarcodeScanner
from ..const import (
    SOURCE_BUILTIN,
    SOURCE_OPENFOODFACTS,
)
from ..integrations.openfoodfacts import (
    OpenFoodFactsClient,
    OpenFoodFactsProduct,
)
from .catalog import ProductCatalog
from .category_mapper import CategoryMapper
from .learning import LearningEngine
from .models import Product
from .repository import MonPanierRepository
from .search import ProductSearch


@dataclass(frozen=True)
class ProductLookupResult:
    """Represent the result of a product lookup."""

    product: Product | None = None
    external_product: OpenFoodFactsProduct | None = None
    source: str | None = None
    category: str | None = None
    requires_confirmation: bool = False


class ProductService:
    """Coordinate product lookup, barcode lookup and learning."""

    def __init__(
        self,
        repository: MonPanierRepository,
        catalog: ProductCatalog,
        learning: LearningEngine,
        barcode_scanner: BarcodeScanner,
        category_mapper: CategoryMapper,
        openfoodfacts: OpenFoodFactsClient | None = None,
    ) -> None:
        """Initialize the product service."""
        self.repository = repository
        self.catalog = catalog
        self.learning = learning
        self.barcode_scanner = barcode_scanner
        self.category_mapper = category_mapper
        self.openfoodfacts = openfoodfacts

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[Product]:
        """Search personal and builtin products."""
        personal_products = self.repository.get_products()
        personal_ids = {
            product.id
            for product in personal_products
        }
        builtin_products = [
            product
            for product in self.catalog.get_products()
            if product.id not in personal_ids
        ]
        products = [
            *personal_products,
            *builtin_products,
        ]
        return ProductSearch(products).search(
            query,
            limit=limit,
        )

    async def find_by_text(
        self,
        query: str,
    ) -> ProductLookupResult:
        """Find a product locally, then through Open Food Facts."""
        products = self.search(
            query,
            limit=1,
        )
        if products:
            product = products[0]
            return ProductLookupResult(
                product=product,
                source=product.source,
                category=product.category,
                requires_confirmation=False,
            )

        if self.openfoodfacts is None:
            return ProductLookupResult()

        external_products = await self.openfoodfacts.search_products(
            query,
        )
        if not external_products:
            return ProductLookupResult()

        external_product = external_products[0]
        category = self.category_mapper.map_categories(
            external_product.categories,
        )
        return ProductLookupResult(
            external_product=external_product,
            source=SOURCE_OPENFOODFACTS,
            category=category,
            requires_confirmation=True,
        )

    def find_local_by_barcode(
        self,
        barcode: str,
    ) -> ProductLookupResult:
        """Find a product by barcode in local databases."""
        parsed_barcode = self.barcode_scanner.parse(barcode)
        if parsed_barcode is None:
            return ProductLookupResult()

        product = self._find_local_barcode(
            parsed_barcode.value,
        )
        if product is None:
            return ProductLookupResult()

        return ProductLookupResult(
            product=product,
            source=product.source,
            category=product.category,
            requires_confirmation=False,
        )

    async def find_by_barcode(
        self,
        barcode: str,
    ) -> ProductLookupResult:
        """Find a product locally, then through Open Food Facts."""
        parsed_barcode = self.barcode_scanner.parse(barcode)
        if parsed_barcode is None:
            return ProductLookupResult()

        # 1. Personal products.
        product = self._find_personal_barcode(
            parsed_barcode.value,
        )
        if product is not None:
            return ProductLookupResult(
                product=product,
                source=product.source,
                category=product.category,
                requires_confirmation=False,
            )

        # 2. Builtin catalog.
        product = self.catalog.find_by_barcode(
            parsed_barcode.value,
        )
        if product is not None:
            return ProductLookupResult(
                product=product,
                source=SOURCE_BUILTIN,
                category=product.category,
                requires_confirmation=False,
            )

        # 3. Open Food Facts.
        if self.openfoodfacts is None:
            return ProductLookupResult()

        external_product = await self.openfoodfacts.get_product(
            parsed_barcode.value,
        )
        if external_product is None:
            return ProductLookupResult()

        category = self.category_mapper.map_categories(
            external_product.categories,
        )
        return ProductLookupResult(
            external_product=external_product,
            source=SOURCE_OPENFOODFACTS,
            category=category,
            requires_confirmation=True,
        )

    def memorize_external_product(
        self,
        external_product: OpenFoodFactsProduct,
        category: str,
    ) -> Product:
        """Memorize a validated Open Food Facts product locally."""
        product_id = self._create_product_id(
            external_product.name,
        )
        product = self.repository.get_product(
            product_id,
        )

        if product is None:
            product = self.repository.add_product(
                name=external_product.name,
                category=category,
                product_id=product_id,
                source=SOURCE_OPENFOODFACTS,
            )

        self._apply_external_metadata(
            product,
            external_product,
        )

        self.repository.add_barcode(
            product.id,
            external_product.barcode,
        )
        return product

    @staticmethod
    def _apply_external_metadata(
        product: Product,
        external_product: OpenFoodFactsProduct,
    ) -> None:
        """Fill missing product metadata from Open Food Facts."""
        metadata = {
            "brand": external_product.brands,
            "quantity": external_product.quantity,
            "product_quantity": external_product.product_quantity,
            "product_quantity_unit": (
                external_product.product_quantity_unit
            ),
            "packaging": external_product.packaging,
        }

        for field_name, value in metadata.items():
            if value is not None and not getattr(product, field_name, None):
                setattr(product, field_name, value)

        if external_product.packaging_tags and not product.packaging_tags:
            product.packaging_tags = list(
                external_product.packaging_tags,
            )

    def memorize_personal_rule(
        self,
        input_text: str,
        product_id: str,
    ) -> None:
        """Remember a personal association between text and a product."""
        self.learning.learn_product(
            input_text,
            product_id,
        )

    def _find_personal_barcode(
        self,
        barcode: str,
    ) -> Product | None:
        """Find a barcode in personal products."""
        return next(
            (
                product
                for product in self.repository.get_products()
                if barcode in product.barcodes
            ),
            None,
        )

    def _find_local_barcode(
        self,
        barcode: str,
    ) -> Product | None:
        """Find a barcode in personal or builtin products."""
        product = self._find_personal_barcode(
            barcode,
        )
        if product is not None:
            return product

        return self.catalog.find_by_barcode(
            barcode,
        )

    @staticmethod
    def _create_product_id(name: str) -> str:
        """Create a stable product ID from its name."""
        return MonPanierRepository._slugify(name)
