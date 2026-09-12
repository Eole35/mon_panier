"""Tests for Mon Panier barcode handling."""

from custom_components.mon_panier.barcode import BarcodeScanner


def test_parse_valid_ean13() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("3017620422003")

    assert result is not None
    assert result.value == "3017620422003"
    assert result.format == "EAN-13"


def test_parse_valid_ean8() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("96385074")

    assert result is not None
    assert result.value == "96385074"
    assert result.format == "EAN-8"


def test_parse_valid_upc_a() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("036000291452")

    assert result is not None
    assert result.value == "036000291452"
    assert result.format == "UPC-A"


def test_parse_barcode_with_spaces() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("301 762 042 2003")

    assert result is not None
    assert result.value == "3017620422003"
    assert result.format == "EAN-13"


def test_parse_barcode_with_non_digit_characters() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("EAN-13: 3017620422003")

    assert result is not None
    assert result.value == "3017620422003"
    assert result.format == "EAN-13"


def test_invalid_check_digit_is_rejected() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("3017620422004")

    assert result is None


def test_invalid_length_is_rejected() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("123456")

    assert result is None


def test_empty_barcode_is_rejected() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("")

    assert result is None


def test_non_numeric_input_is_rejected() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("abcdef")

    assert result is None


def test_whitespace_only_input_is_rejected() -> None:
    scanner = BarcodeScanner()

    result = scanner.parse("   ")

    assert result is None
