"""Text parser for Mon Panier."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..const import (
    UNIT_BAG,
    UNIT_BOTTLE,
    UNIT_BOX,
    UNIT_CAN,
    UNIT_CENTILITER,
    UNIT_GRAM,
    UNIT_KILOGRAM,
    UNIT_LITER,
    UNIT_PACKAGE,
    UNIT_PIECE,
    UNIT_ROLL,
    UNIT_SET,
    UNIT_TRAY,
    UNIT_JAR,
    UNIT_MILLILITER,
)


@dataclass
class ParsedInput:
    """Represent parsed shopping-list input."""

    text: str
    quantity: float = 1
    unit: str = UNIT_PIECE


class ShoppingInputParser:
    """Parse quantities and units from shopping-list text."""

    UNIT_ALIASES = {
        # Piece
        "piece": UNIT_PIECE,
        "pieces": UNIT_PIECE,
        "pièce": UNIT_PIECE,
        "pièces": UNIT_PIECE,

        # Packaging
        "paquet": UNIT_PACKAGE,
        "paquets": UNIT_PACKAGE,

        "boite": UNIT_BOX,
        "boîte": UNIT_BOX,
        "boites": UNIT_BOX,
        "boîtes": UNIT_BOX,

        "bouteille": UNIT_BOTTLE,
        "bouteilles": UNIT_BOTTLE,

        "bidon": UNIT_CAN,
        "bidons": UNIT_CAN,

        "pot": UNIT_JAR,
        "pots": UNIT_JAR,

        "sachet": UNIT_BAG,
        "sachets": UNIT_BAG,

        "barquette": UNIT_TRAY,
        "barquettes": UNIT_TRAY,

        "rouleau": UNIT_ROLL,
        "rouleaux": UNIT_ROLL,

        "lot": UNIT_SET,
        "lots": UNIT_SET,

        # Weight
        "g": UNIT_GRAM,
        "gramme": UNIT_GRAM,
        "grammes": UNIT_GRAM,

        "kg": UNIT_KILOGRAM,
        "kilo": UNIT_KILOGRAM,
        "kilos": UNIT_KILOGRAM,
        "kilogramme": UNIT_KILOGRAM,
        "kilogrammes": UNIT_KILOGRAM,

        # Volume
        "ml": UNIT_MILLILITER,
        "millilitre": UNIT_MILLILITER,
        "millilitres": UNIT_MILLILITER,

        "cl": UNIT_CENTILITER,
        "centilitre": UNIT_CENTILITER,
        "centilitres": UNIT_CENTILITER,

        "l": UNIT_LITER,
        "litre": UNIT_LITER,
        "litres": UNIT_LITER,
    }

    NUMBER_PATTERN = r"(\d+(?:[.,]\d+)?)"

    def parse(self, value: str) -> ParsedInput:
        """Parse a shopping-list input."""
        text = self._clean(value)

        if not text:
            return ParsedInput(text="")

        quantity_match = re.match(
            rf"^{self.NUMBER_PATTERN}\s*",
            text,
            flags=re.IGNORECASE,
        )

        if quantity_match:
            quantity = self._parse_number(quantity_match.group(1))
            remaining = text[quantity_match.end():]

            unit_match = self._extract_unit(remaining)

            if unit_match:
                unit, end_position = unit_match
                remaining = remaining[end_position:].strip()

                # Remove common French connector after packaging units.
                remaining = re.sub(
                    r"^(?:de|d'|du|des)\s+",
                    "",
                    remaining,
                    flags=re.IGNORECASE,
                )

                return ParsedInput(
                    text=remaining,
                    quantity=quantity,
                    unit=unit,
                )

            return ParsedInput(
                text=remaining.strip(),
                quantity=quantity,
                unit=UNIT_PIECE,
            )

        return ParsedInput(
            text=text,
            quantity=1,
            unit=UNIT_PIECE,
        )

    @staticmethod
    def _clean(value: str) -> str:
        """Clean user input."""
        return re.sub(r"\s+", " ", value.strip())

    def _extract_unit(
        self,
        value: str,
    ) -> tuple[str, int] | None:
        """Extract a known unit from the beginning of a value."""
        normalized = value.lower()

        # Longest aliases first so "litres" is tested before "l".
        aliases = sorted(
            self.UNIT_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for alias, unit in aliases:
            pattern = rf"^{re.escape(alias)}(?=\s|$)"
            match = re.match(pattern, normalized)

            if match:
                return unit, match.end()

        return None

    @staticmethod
    def _parse_number(value: str) -> float:
        """Convert a French decimal number to a float."""
        return float(value.replace(",", "."))
