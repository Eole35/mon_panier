"""Category mapping for Mon Panier."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Product


class CategoryMapper:
    """Map external product categories to Mon Panier categories."""

    DEFAULT_CATEGORY = "epicerie"

    CATEGORY_RULES: dict[str, tuple[str, ...]] = {
        "fruits_legumes": (
            "fruits",
            "vegetables",
            "fresh-fruits",
            "fresh-vegetables",
            "legumes",
            "fruits-and-vegetables",
            "pommes-de-terre",
            "potatoes",
        ),
        "viandes": (
            "meats",
            "meat",
            "beef",
            "pork",
            "chicken",
            "poultry",
            "lamb",
            "veal",
            "charcuterie",
            "cold-cuts",
        ),
        "poissonnerie": (
            "fish",
            "seafood",
            "fishes",
            "shellfish",
            "crustaceans",
            "molluscs",
        ),
        "fromagerie": (
            "cheeses",
            "cheese",
            "fromages",
        ),
        "frais": (
            "eggs",
            "egg",
            "fresh-foods",
            "fresh-products",
        ),
        "produits_laitiers": (
            "dairies",
            "dairy",
            "milk",
            "yogurts",
            "yoghurts",
            "butters",
            "butter",
            "cream",
        ),
        "boulangerie": (
            "breads",
            "bread",
            "bakery-products",
            "pastries",
            "viennoiseries",
        ),
        "epicerie": (
            "groceries",
            "grocery",
            "canned-foods",
            "sauces",
            "condiments",
            "pasta",
            "rice",
            "cereals",
            "biscuits",
            "cookies",
            "chocolates",
            "confectioneries",
            "snacks",
            "spreads",
            "jams",
            "oils",
            "vinegars",
        ),
        "vrac": (
            "bulk",
            "bulk-foods",
        ),
        "boissons": (
            "beverages",
            "beverage",
            "waters",
            "water",
            "juices",
            "fruit-juices",
            "soft-drinks",
            "sodas",
            "coffees",
            "coffee",
            "teas",
            "tea",
            "drinks",
        ),
        "surgeles": (
            "frozen-foods",
            "frozen-food",
            "frozen-products",
            "ice-creams",
            "ice-cream",
        ),
        "bebe": (
            "baby-foods",
            "baby-food",
            "baby-products",
            "infant-foods",
            "infant-formulas",
        ),
        "hygiene_beaute": (
            "hygiene",
            "beauty",
            "cosmetics",
            "personal-care",
            "oral-care",
            "shampoos",
            "soaps",
        ),
        "entretien": (
            "cleaning",
            "cleaning-products",
            "laundry",
            "dishwashing",
            "household-cleaning",
        ),
        "maison": (
            "household",
            "home",
            "kitchen",
            "household-products",
        ),
        "jardin": (
            "garden",
            "gardening",
            "garden-products",
            "seeds",
        ),
        "animaux": (
            "pet-food",
            "pet-foods",
            "pet-products",
            "dog-food",
            "cat-food",
            "animal-food",
        ),
    }

    def map_categories(
        self,
        categories: Iterable[str] | None,
    ) -> str:
        """Return the best Mon Panier category."""
        if categories is None:
            return self.DEFAULT_CATEGORY

        normalized_categories = {
            self._normalize(category)
            for category in categories
            if category
        }

        # More specific categories are checked before the generic ones.
        category_order = (
            "animaux",
            "bebe",
            "hygiene_beaute",
            "entretien",
            "jardin",
            "surgeles",
            "poissonnerie",
            "fromagerie",
            "viandes",
            "boulangerie",
            "boissons",
            "vrac",
            "produits_laitiers",
            "fruits_legumes",
            "frais",
            "maison",
            "epicerie",
        )

        for category_id in category_order:
            rules = self.CATEGORY_RULES[category_id]

            for external_category in normalized_categories:
                if self._matches_any(
                    external_category,
                    rules,
                ):
                    return category_id

        return self.DEFAULT_CATEGORY

    @staticmethod
    def _matches_any(
        value: str,
        rules: tuple[str, ...],
    ) -> bool:
        """Check whether a category matches one of the rules."""
        for rule in rules:
            if value == rule:
                return True

            if value.endswith(f"-{rule}"):
                return True

            if value.endswith(f":{rule}"):
                return True

        return False

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize an Open Food Facts category tag."""
        value = value.strip().lower()

        if value.startswith("en:"):
            value = value[3:]
        elif value.startswith("fr:"):
            value = value[3:]

        return value.replace("_", "-")
