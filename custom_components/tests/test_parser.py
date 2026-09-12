"""Tests for the Mon Panier input parser."""

from custom_components.mon_panier.core.parser import ShoppingInputParser
from custom_components.mon_panier.const import (
    UNIT_BOTTLE,
    UNIT_GRAM,
    UNIT_KILOGRAM,
    UNIT_PACKAGE,
    UNIT_PIECE,
)


def test_parse_product_without_quantity() -> None:
    """A product without quantity defaults to one piece."""
    parser = ShoppingInputParser()

    result = parser.parse("bananes")

    assert result.text == "bananes"
    assert result.quantity == 1
    assert result.unit == UNIT_PIECE


def test_parse_integer_quantity() -> None:
    """Parse an integer quantity."""
    parser = ShoppingInputParser()

    result = parser.parse("5 bananes")

    assert result.text == "bananes"
    assert result.quantity == 5
    assert result.unit == UNIT_PIECE


def test_parse_weight_in_grams() -> None:
    """Parse a quantity expressed in grams."""
    parser = ShoppingInputParser()

    result = parser.parse("500 g lardons")

    assert result.text == "lardons"
    assert result.quantity == 500
    assert result.unit == UNIT_GRAM


def test_parse_weight_in_kilograms() -> None:
    """Parse a quantity expressed in kilograms."""
    parser = ShoppingInputParser()

    result = parser.parse("1 kg pommes de terre")

    assert result.text == "pommes de terre"
    assert result.quantity == 1
    assert result.unit == UNIT_KILOGRAM


def test_parse_french_decimal() -> None:
    """Parse a French decimal quantity."""
    parser = ShoppingInputParser()

    result = parser.parse("1,5 kg pommes de terre")

    assert result.text == "pommes de terre"
    assert result.quantity == 1.5
    assert result.unit == UNIT_KILOGRAM


def test_parse_bottles_with_connector() -> None:
    """Parse a packaging quantity with a French connector."""
    parser = ShoppingInputParser()

    result = parser.parse("2 bouteilles d'eau")

    assert result.text == "eau"
    assert result.quantity == 2
    assert result.unit == UNIT_BOTTLE


def test_parse_packages_with_connector() -> None:
    """Parse packages with a French connector."""
    parser = ShoppingInputParser()

    result = parser.parse("3 paquets de pâtes")

    assert result.text == "pâtes"
    assert result.quantity == 3
    assert result.unit == UNIT_PACKAGE


def test_parse_plural_unit() -> None:
    """Plural units are normalized."""
    parser = ShoppingInputParser()

    result = parser.parse("6 bouteilles eau")

    assert result.text == "eau"
    assert result.quantity == 6
    assert result.unit == UNIT_BOTTLE


def test_parse_extra_spaces() -> None:
    """Extra spaces are removed."""
    parser = ShoppingInputParser()

    result = parser.parse("  5   bananes  ")

    assert result.text == "bananes"
    assert result.quantity == 5
    assert result.unit == UNIT_PIECE


def test_parse_empty_input() -> None:
    """Empty input returns an empty parsed value."""
    parser = ShoppingInputParser()

    result = parser.parse("   ")

    assert result.text == ""
    assert result.quantity == 1
    assert result.unit == UNIT_PIECE
