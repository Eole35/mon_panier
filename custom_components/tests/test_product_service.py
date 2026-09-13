"""Tests for the Mon Panier product service."""

from __future__ import annotations

import pytest

from custom_components.mon_panier.barcode import BarcodeScanner
from custom_components.mon_panier.core.catalog import ProductCatalog
from custom_components.mon_panier.core.learning import LearningEngine
from custom_components.mon_panier.core.models import Product
from custom_components.mon_panier.core.product_service import ProductService
from custom_components.mon_panier.core.repository import MonPanierRepository
from custom_components.mon_panier.integrations.openfoodfacts import (
    OpenFoodFactsProduct,
)


def create_service(
    products: list[Product] | None = None,
    openfoodfacts=None,
) -> ProductService:
    """Create a product service for testing."""
    repository = MonPanierRepository()
    catalog = ProductCatalog(products or [])
    learning = LearningEngine()
    scanner = BarcodeScanner()

    return ProductService(
        repository=repository,
        catalog=catalog,
        learning=learning,
        barcode_scanner=scanner,
        openfoodfacts=openfoodfacts,
    )


def test_search_finds_builtin_product() -> None:
    """Builtin products should be searchable."""
    product = Product(
        id="bananes",
        name="Bananes",
        category="fruits_legumes",
        synonyms=["banane"],
        source="builtin",
    )

    service = create_service(products=[product])

    results = service.search("banan")

    assert len(results) == 1
    assert results[0].id == "bananes"


def test_personal_product_has_priority() -> None:
    """Personal products should be preferred over builtin products."""
    builtin = Product(
        id="bananes",
        name="Bananes",
        category="fruits_legumes",
        source="builtin",
    )

    service = create_service(products=[builtin])

    personal = service.repository.add_product(
        name="Bananes habituelles",
        category="fruits_legumes",
        product_id="bananes_habituelles",
        synonyms=["bananes"],
        source="personal",
    )

    results = service.search("bananes")

    assert results
    assert results[0].id == personal.id


def test_find_local_barcode_in_personal_product() -> None:
    """A personal barcode should be found locally."""
    service = create_service()

    product = service.repository.add_product(
        name="Pâtes",
        category="epicerie",
        product_id="pates",
        source="personal",
    )

    service.repository.add_barcode(
        product.id,
        "3017620422003",
    )

    result = service.find_local_by_barcode("3017620422003")

    assert result.product is not None
    assert result.product.id == "pates"
    assert result.source == "personal"
    assert result.requires_confirmation is False


def test_find_local_barcode_in_builtin_product() -> None:
    """A builtin barcode should be found locally."""
    product = Product(
        id="produit_test",
        name="Produit test",
        category="epicerie",
        source="builtin",
        barcodes=["3017620422003"],
    )

    service = create_service(products=[product])

    result = service.find_local_by_barcode("3017620422003")

    assert result.product is not None
    assert result.product.id == "produit_test"
    assert result.source == "builtin"
    assert result.requires_confirmation is False


def test_invalid_barcode_returns_empty_result() -> None:
    """An invalid barcode should not be searched."""
    service = create_service()

    result = service.find_local_by_barcode("123456")

    assert result.product is None
    assert result.external_product is None
    assert result.source is None
    assert result.requires_confirmation is False


@pytest.mark.asyncio
async def test_unknown_barcode_without_openfoodfacts_returns_empty_result() -> None:
    """An unknown barcode should fail cleanly without Open Food Facts."""
    service = create_service()

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is None
    assert result.external_product is None
    assert result.source is None
    assert result.requires_confirmation is False


class FakeOpenFoodFactsClient:
    """Fake Open Food Facts client for tests."""

    def __init__(
        self,
        product: OpenFoodFactsProduct | None,
    ) -> None:
        """Initialize the fake client."""
        self.product = product
        self.requested_barcode: str | None = None

    async def get_product(
        self,
        barcode: str,
    ) -> OpenFoodFactsProduct | None:
        """Return the configured fake product."""
        self.requested_barcode = barcode
        return self.product


@pytest.mark.asyncio
async def test_unknown_barcode_is_sent_to_openfoodfacts() -> None:
    """An unknown local barcode should be searched through OFF."""
    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit OFF",
        generic_name="Produit générique",
        brands="Marque",
        categories=["en:snacks"],
        image_url="https://example.com/image.jpg",
    )

    client = FakeOpenFoodFactsClient(external_product)
    service = create_service(openfoodfacts=client)

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert client.requested_barcode == "3017620422003"
    assert result.product is None
    assert result.external_product is external_product
    assert result.source == "openfoodfacts"
    assert result.requires_confirmation is True


@pytest.mark.asyncio
async def test_openfoodfacts_product_requires_confirmation() -> None:
    """A product returned by OFF must require user confirmation."""
    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit OFF",
    )

    client = FakeOpenFoodFactsClient(external_product)
    service = create_service(openfoodfacts=client)

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.external_product is not None
    assert result.requires_confirmation is True


@pytest.mark.asyncio
async def test_openfoodfacts_unknown_product_returns_empty_result() -> None:
    """An unknown product from OFF should return an empty result."""
    client = FakeOpenFoodFactsClient(None)
    service = create_service(openfoodfacts=client)

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is None
    assert result.external_product is None
    assert result.source is None
    assert result.requires_confirmation is False


def test_memorize_external_product() -> None:
    """A validated OFF product should be stored locally."""
    service = create_service()

    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit OFF",
    )

    product = service.memorize_external_product(
        external_product,
        category="epicerie",
    )

    assert product.name == "Produit OFF"
    assert product.category == "epicerie"
    assert product.source == "openfoodfacts"
    assert "3017620422003" in product.barcodes

    stored_product = service.repository.get_product(product.id)

    assert stored_product is product


def test_memorize_external_product_adds_new_barcode_to_existing_product() -> None:
    """An existing personal product should receive the new barcode."""
    service = create_service()

    existing = service.repository.add_product(
        name="Produit OFF",
        category="epicerie",
        product_id="produit_off",
        source="personal",
    )

    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit OFF",
    )

    product = service.memorize_external_product(
        external_product,
        category="epicerie",
    )

    assert product.id == existing.id
    assert product.source == "personal"
    assert "3017620422003" in product.barcodes


def test_memorize_personal_rule() -> None:
    """A personal text association should be memorized."""
    service = create_service()

    product = service.repository.add_product(
        name="Pommes de terre",
        category="fruits_legumes",
        product_id="pommes_de_terre",
        source="personal",
    )

    service.memorize_personal_rule(
        "pdt",
        product.id,
    )

    assert service.learning.find_product("pdt") == product.id
