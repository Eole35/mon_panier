"""Personal learning for Mon Panier."""

from __future__ import annotations

from .models import CategoryOverride, PersonalRule, Product


class LearningEngine:
    """Manage personal product and category learning."""

    def __init__(
        self,
        personal_rules: list[PersonalRule] | None = None,
        category_overrides: list[CategoryOverride] | None = None,
    ) -> None:
        """Initialize the learning engine."""
        self.personal_rules = personal_rules or []
        self.category_overrides = category_overrides or []

    def learn_product(
        self,
        input_text: str,
        product_id: str,
    ) -> PersonalRule:
        """Remember that an input refers to a product."""
        normalized_input = self.normalize(input_text)

        existing = next(
            (
                rule
                for rule in self.personal_rules
                if self.normalize(rule.input_text) == normalized_input
            ),
            None,
        )

        if existing:
            existing.product_id = product_id
            return existing

        rule = PersonalRule(
            input_text=normalized_input,
            product_id=product_id,
        )
        self.personal_rules.append(rule)

        return rule

    def find_product(
        self,
        input_text: str,
    ) -> str | None:
        """Return the learned product for an input."""
        normalized_input = self.normalize(input_text)

        for rule in self.personal_rules:
            if self.normalize(rule.input_text) == normalized_input:
                return rule.product_id

        return None

    def learn_category(
        self,
        product_id: str,
        category: str,
    ) -> CategoryOverride:
        """Remember a personal category override."""
        existing = next(
            (
                override
                for override in self.category_overrides
                if override.product_id == product_id
            ),
            None,
        )

        if existing:
            existing.category = category
            return existing

        override = CategoryOverride(
            product_id=product_id,
            category=category,
        )
        self.category_overrides.append(override)

        return override

    def get_category(
        self,
        product: Product,
    ) -> str:
        """Return the learned category or the product category."""
        override = next(
            (
                override
                for override in self.category_overrides
                if override.product_id == product.id
            ),
            None,
        )

        if override:
            return override.category

        return product.category

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize text used by personal rules."""
        return " ".join(value.strip().lower().split())
