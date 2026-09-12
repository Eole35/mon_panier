"""Search engine for Mon Panier."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from .models import Product


class ProductSearch:
    """Search products from the personal and builtin catalog."""

    MIN_QUERY_LENGTH = 2
    DEFAULT_LIMIT = 5

    def __init__(self, products: list[Product]) -> None:
        """Initialize the search engine."""
        self.products = products

    def search(
        self,
        query: str,
        *,
        limit: int = DEFAULT_LIMIT,
    ) -> list[Product]:
        """Return the best matching products."""
        normalized_query = self.normalize(query)

        if len(normalized_query) < self.MIN_QUERY_LENGTH:
            return []

        scored_products: list[tuple[float, Product]] = []

        for product in self.products:
            score = self._score_product(product, normalized_query)

            if score > 0:
                scored_products.append((score, product))

        scored_products.sort(
            key=lambda result: (
                -result[0],
                -result[1].purchase_count,
                result[1].name.lower(),
            )
        )

        return [product for _, product in scored_products[:limit]]

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize text for searching."""
        value = value.strip().lower()

        value = unicodedata.normalize("NFD", value)
        value = "".join(
            character
            for character in value
            if unicodedata.category(character) != "Mn"
        )

        value = re.sub(r"[-_'’]", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def _score_product(
        self,
        product: Product,
        query: str,
    ) -> float:
        """Calculate the relevance score of a product."""
        product_name = self.normalize(product.name)

        synonyms = [
            self.normalize(synonym)
            for synonym in product.synonyms
        ]

        candidates = [product_name, *synonyms]

        best_score = 0.0

        for candidate in candidates:
            score = self._score_candidate(candidate, query)
            best_score = max(best_score, score)

        if best_score == 0:
            return 0.0

        # Personal products are preferred over builtin products.
        if product.source == "personal":
            best_score += 5

        # Favorites receive a strong priority.
        if product.favorite:
            best_score += 20

        # Frequently purchased products receive a small bonus.
        best_score += min(product.purchase_count, 10) * 0.5

        return best_score

    @staticmethod
    def _score_candidate(
        candidate: str,
        query: str,
    ) -> float:
        """Calculate the score between a query and a candidate."""
        if candidate == query:
            return 100.0

        # Query starts the product name.
        if candidate.startswith(query):
            return 90.0

        # One of the words starts with the query.
        words = candidate.split()
        if any(word.startswith(query) for word in words):
            return 80.0

        # Query appears somewhere in the candidate.
        if query in candidate:
            return 70.0

        # Compare individual words for partial matching.
        query_words = query.split()

        if query_words:
            matched_words = sum(
                1
                for query_word in query_words
                if any(
                    word.startswith(query_word)
                    or query_word in word
                    for word in words
                )
            )

            if matched_words == len(query_words):
                return 65.0

        # Approximate matching.
        ratio = SequenceMatcher(
            None,
            query,
            candidate,
        ).ratio()

        if ratio >= 0.85:
            return 60.0

        if ratio >= 0.75:
            return 45.0

        if ratio >= 0.65:
            return 30.0

        return 0.0
