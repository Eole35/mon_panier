"""Tests for the Mon Panier product service."""

from __future__ import annotations

import pytest

from custom_components.mon_panier.barcode import BarcodeScanner
from custom_components.mon_panier.core.catalog import ProductCatalog
from custom_components.mon_panier.core.category_mapper import CategoryMapper
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
    category_mapper = CategoryMapper()

    return ProductService(
        repository=repository,
        catalog=catalog,
        learning=learning,
        barcode_scanner=scanner,
        category_mapper=category_mapper,
        openfoodfacts=openfoodfacts,
    )


def test_search_builtin_product() -> None:
    """Test searching a builtin product."""
    products = [
        Product(
            id="bananes",
            name="Bananes",
            category="fruits_legumes",
            synonyms=["banane"],
            source="builtin",
        ),
    ]

    service = create_service(products)

    results = service.search("bananes")

    assert len(results) == 1
    assert results[0].id == "bananes"


def test_search_builtin_product_with_partial_query() -> None:
    """Test partial product search."""
    products = [
        Product(
            id="lardons",
            name="Lardons",
            category="viandes",
            synonyms=["lardon"],
            source="builtin",
        ),
    ]

    service = create_service(products)

    results = service.search("lard")

    assert len(results) == 1
    assert results[0].id == "lardons"


def test_search_personal_product_has_priority() -> None:
    """Test that a personal product has priority over a builtin product."""
    builtin_product = Product(
        id="bananes",
        name="Bananes",
        category="fruits_legumes",
        source="builtin",
    )

    service = create_service([builtin_product])

    personal_product = service.repository.add_product(
        name="Bananes de mon magasin",
        category="fruits_legumes",
        product_id="bananes_personnelles",
        synonyms=["bananes"],
        source="personal",
    )

    results = service.search("bananes")

    assert len(results) >= 1
    assert results[0].id == personal_product.id


def test_search_favorite_product_has_priority() -> None:
    """Test that favorite products are prioritized in search."""
    normal_product = Product(
        id="pommes",
        name="Pommes",
        category="fruits_legumes",
        source="builtin",
    )

    favorite_product = Product(
        id="pommes_favorites",
        name="Pommes favorites",
        category="fruits_legumes",
        synonyms=["pommes"],
        source="personal",
        favorite=True,
    )

    service = create_service(
        [
            normal_product,
            favorite_product,
        ]
    )

    results = service.search("pommes")

    assert len(results) >= 1
    assert results[0].id == "pommes_favorites"


def test_find_personal_product_by_barcode() -> None:
    """Test finding a personal product by barcode."""
    service = create_service()

    product = service.repository.add_product(
        name="Produit personnel",
        category="epicerie",
        product_id="produit_personnel",
        source="personal",
    )

    service.repository.add_barcode(
        product.id,
        "3017620422003",
    )

    result = service.find_local_by_barcode(
        "3017620422003",
    )

    assert result.product is not None
    assert result.product.id == "produit_personnel"
    assert result.source == "personal"
    assert result.requires_confirmation is False


def test_find_builtin_product_by_barcode() -> None:
    """Test finding a builtin product by barcode."""
    product = Product(
        id="produit_builtin",
        name="Produit builtin",
        category="epicerie",
        source="builtin",
        barcodes=["3017620422003"],
    )

    service = create_service([product])

    result = service.find_local_by_barcode(
        "3017620422003",
    )

    assert result.product is not None
    assert result.product.id == "produit_builtin"
    assert result.source == "builtin"
    assert result.requires_confirmation is False


def test_find_local_by_barcode_invalid_barcode() -> None:
    """Test that an invalid barcode returns an empty result."""
    service = create_service()

    result = service.find_local_by_barcode(
        "3017620422004",
    )

    assert result.product is None
    assert result.source is None
    assert result.category is None
    assert result.requires_confirmation is False


def test_find_local_by_barcode_unknown_product() -> None:
    """Test that an unknown barcode returns an empty local result."""
    service = create_service()

    result = service.find_local_by_barcode(
        "3017620422003",
    )

    assert result.product is None
    assert result.source is None
    assert result.category is None
    assert result.requires_confirmation is False


@pytest.mark.asyncio
async def test_find_by_barcode_unknown_without_openfoodfacts() -> None:
    """Test an unknown barcode without Open Food Facts."""
    service = create_service()

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is None
    assert result.external_product is None
    assert result.source is None
    assert result.category is None
    assert result.requires_confirmation is False


class FakeOpenFoodFactsClient:
    """Fake Open Food Facts client for tests."""

    def __init__(
        self,
        product: OpenFoodFactsProduct | None,
    ) -> None:
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
async def test_find_by_barcode_uses_openfoodfacts() -> None:
    """Test that Open Food Facts is queried for an unknown local barcode."""
    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit Open Food Facts",
        generic_name="Produit alimentaire",
        brands="Marque",
        categories=["en:beverages"],
    )

    fake_client = FakeOpenFoodFactsClient(
        external_product,
    )

    service = create_service(
        openfoodfacts=fake_client,
    )

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert fake_client.requested_barcode == "3017620422003"

    assert result.product is None
    assert result.external_product is external_product
    assert result.source == "openfoodfacts"
    assert result.category == "boissons"
    assert result.requires_confirmation is True


@pytest.mark.asyncio
async def test_find_by_barcode_openfoodfacts_product_requires_confirmation() -> None:
    """Test that an Open Food Facts product requires user confirmation."""
    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Eau minérale",
        categories=["en:waters"],
    )

    fake_client = FakeOpenFoodFactsClient(
        external_product,
    )

    service = create_service(
        openfoodfacts=fake_client,
    )

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.external_product is not None
    assert result.external_product.name == "Eau minérale"
    assert result.source == "openfoodfacts"
    assert result.category == "boissons"
    assert result.requires_confirmation is True


@pytest.mark.asyncio
async def test_find_by_barcode_openfoodfacts_unknown_product() -> None:
    """Test an unknown product in Open Food Facts."""
    fake_client = FakeOpenFoodFactsClient(
        None,
    )

    service = create_service(
        openfoodfacts=fake_client,
    )

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is None
    assert result.external_product is None
    assert result.source is None
    assert result.category is None
    assert result.requires_confirmation is False


@pytest.mark.asyncio
async def test_find_by_barcode_personal_product_does_not_call_openfoodfacts() -> None:
    """Test that a personal barcode is resolved locally first."""
    service = create_service(
        openfoodfacts=FakeOpenFoodFactsClient(
            OpenFoodFactsProduct(
                barcode="3017620422003",
                name="Produit externe",
            )
        ),
    )

    product = service.repository.add_product(
        name="Produit personnel",
        category="epicerie",
        product_id="produit_personnel",
        source="personal",
    )

    service.repository.add_barcode(
        product.id,
        "3017620422003",
    )

    fake_client = service.openfoodfacts

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is not None
    assert result.product.id == "produit_personnel"
    assert result.source == "personal"
    assert result.requires_confirmation is False

    assert fake_client.requested_barcode is None


@pytest.mark.asyncio
async def test_find_by_barcode_builtin_product_does_not_call_openfoodfacts() -> None:
    """Test that a builtin barcode is resolved locally first."""
    builtin_product = Product(
        id="produit_builtin",
        name="Produit builtin",
        category="epicerie",
        source="builtin",
        barcodes=["3017620422003"],
    )

    fake_client = FakeOpenFoodFactsClient(
        OpenFoodFactsProduct(
            barcode="3017620422003",
            name="Produit externe",
        )
    )

    service = create_service(
        [builtin_product],
        openfoodfacts=fake_client,
    )

    result = await service.find_by_barcode(
        "3017620422003",
    )

    assert result.product is not None
    assert result.product.id == "produit_builtin"
    assert result.source == "builtin"
    assert result.requires_confirmation is False

    assert fake_client.requested_barcode is None


def test_memorize_external_product_creates_personal_product() -> None:
    """Test memorizing an Open Food Facts product."""
    service = create_service()

    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit Open Food Facts",
        generic_name="Produit alimentaire",
        brands="Marque",
        categories=["en:beverages"],
    )

    product = service.memorize_external_product(
        external_product,
        "boissons",
    )

    assert product.name == "Produit Open Food Facts"
    assert product.category == "boissons"
    assert product.source == "openfoodfacts"
    assert product.barcodes == ["3017620422003"]

    stored_product = service.repository.get_product(
        product.id,
    )

    assert stored_product is not None
    assert stored_product.id == product.id


def test_memorize_external_product_adds_barcode_to_existing_product() -> None:
    """Test adding an external barcode to an existing personal product."""
    service = create_service()

    existing_product = service.repository.add_product(
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
        "epicerie",
    )

    assert product.id == existing_product.id
    assert product.barcodes == ["3017620422003"]


def test_memorize_external_product_does_not_duplicate_barcode() -> None:
    """Test that memorizing the same barcode does not duplicate it."""
    service = create_service()

    existing_product = service.repository.add_product(
        name="Produit OFF",
        category="epicerie",
        product_id="produit_off",
        source="personal",
    )

    service.repository.add_barcode(
        existing_product.id,
        "3017620422003",
    )

    external_product = OpenFoodFactsProduct(
        barcode="3017620422003",
        name="Produit OFF",
    )

    product = service.memorize_external_product(
        external_product,
        "epicerie",
    )

    assert product.id == existing_product.id
    assert product.barcodes == ["3017620422003"]


def test_memorize_personal_rule() -> None:
    """Test memorizing a personal search rule."""
    service = create_service()

    product = service.repository.add_product(
        name="Lardons allumettes",
        category="viandes",
        product_id="lardons_allumettes",
        source="personal",
    )

    service.memorize_personal_rule(
        "lardons allumette",
        product.id,
    )

    assert service.learning.find_product(
        "lardons allumette",
    ) == product.id


def test_memorize_personal_rule_is_normalized() -> None:
    """Test that personal rules are normalized."""
    service = create_service()

    product = service.repository.add_product(
        name="Pommes de terre",
        category="fruits_legumes",
        product_id="pommes_de_terre",
        source="personal",
    )

    service.memorize_personal_rule(
        "  PDT  ",
        product.id,
    )

    assert service.learning.find_product(
        "pdt",
    ) == product.id


def test_search_returns_empty_for_short_query() -> None:
    """Test that very short search queries return no result."""
    products = [
        Product(
            id="eau",
            name="Eau",
            category="boissons",
            source="builtin",
        ),
    ]

    service = create_service(products)

    assert service.search("e") == []
    assert service.search("") == []


def test_search_does_not_duplicate_personal_and_builtin_product() -> None:
    """Test that the same product ID is not returned twice."""
    builtin_product = Product(
        id="bananes",
        name="Bananes",
        category="fruits_legumes",
        source="builtin",
    )

    service = create_service([builtin_product])

    service.repository.add_product(
        name="Bananes personnelles",
        category="fruits_legumes",
        product_id="bananes",
        source="personal",
    )

    results = service.search("bananes")

    assert len(results) == 1
    assert results[0].id == "bananes"


def test_find_local_by_barcode_normalizes_scanner_output() -> None:
    """Test that a formatted barcode is normalized before lookup."""
    product = Product(
        id="produit_builtin",
        name="Produit builtin",
        category="epicerie",
        source="builtin",
        barcodes=["3017620422003"],
    )

    service = create_service([product])

    result = service.find_local_by_barcode(
        "301-762-042-2003",
    )

    assert result.product is not None
    assert result.product.id == "produit_builtin"
