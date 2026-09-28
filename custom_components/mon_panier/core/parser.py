"""Text parser for Mon Panier."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ..const import (
    UNIT_BAG,
    UNIT_BOTTLE,
    UNIT_BOX,
    UNIT_CAN,
    UNIT_CENTILITER,
    UNIT_GRAM,
    UNIT_JAR,
    UNIT_KILOGRAM,
    UNIT_LITER,
    UNIT_MILLILITER,
    UNIT_PACKAGE,
    UNIT_PIECE,
    UNIT_ROLL,
    UNIT_SET,
    UNIT_TRAY,
)


@dataclass
class ParsedInput:
    """Represent parsed shopping-list input."""

    text: str
    quantity: float = 1
    unit: str = UNIT_PIECE
    package_unit: str | None = None
    package_quantity: float | None = None
    package_unit_value: str | None = None
    brand: str | None = None


class ShoppingInputParser:
    """Parse natural shopping-list input."""

    UNIT_ALIASES = {
        "piece": UNIT_PIECE,
        "pieces": UNIT_PIECE,
        "pièce": UNIT_PIECE,
        "pièces": UNIT_PIECE,
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
        "g": UNIT_GRAM,
        "gramme": UNIT_GRAM,
        "grammes": UNIT_GRAM,
        "kg": UNIT_KILOGRAM,
        "kilo": UNIT_KILOGRAM,
        "kilos": UNIT_KILOGRAM,
        "kilogramme": UNIT_KILOGRAM,
        "kilogrammes": UNIT_KILOGRAM,
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

    PACKAGE_ALIASES = (
        "pot",
        "pots",
        "paquet",
        "paquets",
        "boîte",
        "boites",
        "boîtes",
        "bouteille",
        "bouteilles",
        "sachet",
        "sachets",
        "barquette",
        "barquettes",
        "rouleau",
        "rouleaux",
        "lot",
        "lots",
    )

    WEIGHT_ALIASES = (
        "kg",
        "g",
        "gramme",
        "grammes",
        "ml",
        "cl",
        "l",
        "litre",
        "litres",
        "millilitre",
        "millilitres",
        "centilitre",
        "centilitres",
    )

    def parse(self, value: str) -> ParsedInput:
        """Parse a natural shopping-list input."""
        text = self._clean(value)

        if not text:
            return ParsedInput(text="")

        # Case: "2 pots de 300g de sauce"
        package_with_quantity = re.match(
            rf"^(?P<quantity>{self.NUMBER_PATTERN})\s+"
            rf"(?P<package>{'|'.join(self.PACKAGE_ALIASES)})"
            rf"\s+(?:de|d['’])\s*"
            rf"(?P<package_quantity>{self.NUMBER_PATTERN})\s*"
            rf"(?P<package_unit>{'|'.join(self.WEIGHT_ALIASES)})"
            rf"\s+(?:de|d['’]|du|des)\s+"
            rf"(?P<product>.+)$",
            text,
            flags=re.IGNORECASE,
        )

        if package_with_quantity:
            package_unit = self._normalize_package_unit(
                package_with_quantity.group("package")
            )
            quantity = self._parse_number(
                package_with_quantity.group("quantity")
            )
            package_quantity = self._parse_number(
                package_with_quantity.group("package_quantity")
            )
            package_unit_value = self._normalize_weight_unit(
                package_with_quantity.group("package_unit")
            )
            product = self._clean(
                package_with_quantity.group("product")
            )

            return ParsedInput(
                text=product,
                quantity=quantity,
                unit=package_unit,
                package_unit=package_unit,
                package_quantity=package_quantity,
                package_unit_value=package_unit_value,
            )

        # Case: "sauce mexicaine 300g"
        trailing_quantity = re.search(
            rf"\s+(?P<package_quantity>{self.NUMBER_PATTERN})\s*"
            rf"(?P<package_unit>{'|'.join(self.WEIGHT_ALIASES)})$",
            text,
            flags=re.IGNORECASE,
        )

        if trailing_quantity:
            product = self._clean(
                text[:trailing_quantity.start()]
            )
            package_quantity = self._parse_number(
                trailing_quantity.group("package_quantity")
            )
            package_unit_value = self._normalize_weight_unit(
                trailing_quantity.group("package_unit")
            )

            return ParsedInput(
                text=product,
                quantity=1,
                unit=UNIT_PIECE,
                package_quantity=package_quantity,
                package_unit_value=package_unit_value,
            )

        # Case: "2 pots de sauce"
        package_match = re.match(
            rf"^(?P<quantity>{self.NUMBER_PATTERN})\s+"
            rf"(?P<package>{'|'.join(self.PACKAGE_ALIASES)})"
            rf"\s+(?:de|d['’]|du|des)\s+"
            rf"(?P<product>.+)$",
            text,
            flags=re.IGNORECASE,
        )

        if package_match:
            package_unit = self._normalize_package_unit(
                package_match.group("package")
            )
            quantity = self._parse_number(
                package_match.group("quantity")
            )
            product = self._clean(
                package_match.group("product")
            )

            return ParsedInput(
                text=product,
                quantity=quantity,
                unit=package_unit,
            )

        # Generic quantity + unit:
        # "500 g lardons", "2 bouteilles eau", "5 bananes".
        quantity_match = re.match(
            rf"^{self.NUMBER_PATTERN}\s*",
            text,
            flags=re.IGNORECASE,
        )

        if quantity_match:
            quantity = self._parse_number(
                quantity_match.group(1)
            )
            remaining = text[quantity_match.end():]

            unit_match = self._extract_unit(remaining)

            if unit_match:
                unit, end_position = unit_match
                remaining = remaining[end_position:].strip()
                remaining = re.sub(
                    r"^(?:de\s+|d['’]\s*|du\s+|des\s+)",
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
    def _normalize_package_unit(value: str) -> str:
        """Normalize a package unit."""
        aliases = {
            "pot": UNIT_JAR,
            "pots": UNIT_JAR,
            "paquet": UNIT_PACKAGE,
            "paquets": UNIT_PACKAGE,
            "boîte": UNIT_BOX,
            "boites": UNIT_BOX,
            "boîtes": UNIT_BOX,
            "bouteille": UNIT_BOTTLE,
            "bouteilles": UNIT_BOTTLE,
            "sachet": UNIT_BAG,
            "sachets": UNIT_BAG,
            "barquette": UNIT_TRAY,
            "barquettes": UNIT_TRAY,
            "rouleau": UNIT_ROLL,
            "rouleaux": UNIT_ROLL,
            "lot": UNIT_SET,
            "lots": UNIT_SET,
        }
        return aliases[value.lower()]

    @staticmethod
    def _normalize_weight_unit(value: str) -> str:
        """Normalize a weight or volume unit."""
        aliases = {
            "g": UNIT_GRAM,
            "gramme": UNIT_GRAM,
            "grammes": UNIT_GRAM,
            "kg": UNIT_KILOGRAM,
            "kilo": UNIT_KILOGRAM,
            "kilos": UNIT_KILOGRAM,
            "kilogramme": UNIT_KILOGRAM,
            "kilogrammes": UNIT_KILOGRAM,
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
        return aliases[value.lower()]

    @staticmethod
    def _extract_brand(value: str) -> str | None:
        """Extract a trailing brand from the input."""
        words = value.split()

        if len(words) < 2:
            return None

        return " ".join(words[-2:])

    @staticmethod
    def _parse_number(value: str) -> float:
        """Convert a French decimal number to a float."""
        return float(value.replace(",", "."))
