"""Barcode utilities for Mon Panier."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_LENGTHS = {
    8,   # EAN-8
    12,  # UPC-A
    13,  # EAN-13
}


@dataclass(frozen=True)
class Barcode:
    """Represent a validated product barcode."""

    value: str
    format: str


class BarcodeScanner:
    """Validate and normalize product barcodes."""

    def parse(self, value: str) -> Barcode | None:
        """Validate and normalize a barcode."""
        normalized = self.normalize(value)

        if not normalized:
            return None

        barcode_format = self.detect_format(normalized)

        if barcode_format is None:
            return None

        if not self.is_valid_check_digit(normalized):
            return None

        return Barcode(
            value=normalized,
            format=barcode_format,
        )

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize a scanned barcode."""
        value = value.strip()

        for separator in (" ", "-", "\t", "\n", "\r"):
            value = value.replace(separator, "")

        return value

    @staticmethod
    def detect_format(value: str) -> str | None:
        """Detect the barcode format from its length."""
        formats = {
            8: "EAN-8",
            12: "UPC-A",
            13: "EAN-13",
        }

        return formats.get(len(value))

    @staticmethod
    def is_valid_check_digit(value: str) -> bool:
        """Validate an EAN/UPC check digit."""
        if len(value) not in SUPPORTED_LENGTHS:
            return False

        digits = [int(character) for character in value]

        check_digit = digits[-1]
        payload = digits[:-1]

        total = 0

        for index, digit in enumerate(reversed(payload)):
            if index % 2 == 0:
                total += digit * 3
            else:
                total += digit

        calculated = (10 - (total % 10)) % 10

        return calculated == check_digit
