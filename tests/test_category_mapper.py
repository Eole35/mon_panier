"""Tests for the Mon Panier category mapper."""

from custom_components.mon_panier.core.category_mapper import CategoryMapper


def test_map_beverages() -> None:
    """Beverages should map to boissons."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:beverages", "en:waters"]
    ) == "boissons"


def test_map_meat() -> None:
    """Meat should map to viandes."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:foods", "en:meats", "en:chicken"]
    ) == "viandes"


def test_map_fish() -> None:
    """Fish should map to poissonnerie."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:seafood", "en:fishes"]
    ) == "poissonnerie"


def test_map_cheese() -> None:
    """Cheese should map to fromagerie."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:cheeses"]
    ) == "fromagerie"


def test_map_frozen_foods() -> None:
    """Frozen products should map to surgeles."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:frozen-foods"]
    ) == "surgeles"


def test_map_baby_food() -> None:
    """Baby products should map to bebe."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:baby-foods"]
    ) == "bebe"


def test_map_hygiene() -> None:
    """Personal care products should map to hygiene_beaute."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:personal-care"]
    ) == "hygiene_beaute"


def test_map_cleaning() -> None:
    """Cleaning products should map to entretien."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:cleaning-products"]
    ) == "entretien"


def test_map_garden() -> None:
    """Garden products should map to jardin."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:garden-products"]
    ) == "jardin"


def test_map_pet_food() -> None:
    """Pet food should map to animaux."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:pet-food"]
    ) == "animaux"


def test_map_fruits_and_vegetables() -> None:
    """Fruits and vegetables should map correctly."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:fruits", "en:vegetables"]
    ) == "fruits_legumes"


def test_map_french_tag() -> None:
    """French tags should also be supported."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["fr:boissons"]
    ) == "boissons"


def test_unknown_category_defaults_to_grocery() -> None:
    """Unknown products should fall back to epicerie."""
    mapper = CategoryMapper()

    assert mapper.map_categories(
        ["en:something-completely-unknown"]
    ) == "epicerie"


def test_empty_categories_defaults_to_grocery() -> None:
    """Missing categories should fall back to epicerie."""
    mapper = CategoryMapper()

    assert mapper.map_categories(None) == "epicerie"
    assert mapper.map_categories([]) == "epicerie"
