"""Open Food Facts integration for Mon Panier."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from ..const import (
    CONF_OFF_COUNTRY,
    CONF_OFF_LANGUAGE,
    CONF_OFF_URL,
    CONF_OFF_USER_AGENT,
    DEFAULT_OFF_COUNTRY,
    DEFAULT_OFF_LANGUAGE,
    DEFAULT_OFF_URL,
    DEFAULT_OFF_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class OpenFoodFactsProduct:
    """Represent a product returned by Open Food Facts."""

    barcode: str
    name: str
    generic_name: str | None = None
    brands: str | None = None
    categories: list[str] | None = None
    image_url: str | None = None
    quantity: str | None = None
    product_quantity: float | None = None
    product_quantity_unit: str | None = None
    packaging: str | None = None
    packaging_tags: list[str] | None = None


class OpenFoodFactsClient:
    """Client for the Open Food Facts API."""

    API_PATH = "/api/v3/product"
    SEARCH_PATH = "/cgi/search.pl"

    def __init__(
        self,
        session: ClientSession,
        options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the client."""
        options = options or {}

        self._session = session
        self._base_url = options.get(
            CONF_OFF_URL,
            DEFAULT_OFF_URL,
        ).rstrip("/")
        self._country = options.get(
            CONF_OFF_COUNTRY,
            DEFAULT_OFF_COUNTRY,
        )
        self._language = options.get(
            CONF_OFF_LANGUAGE,
            DEFAULT_OFF_LANGUAGE,
        )
        self._user_agent = options.get(
            CONF_OFF_USER_AGENT,
            DEFAULT_OFF_USER_AGENT,
        )

    def _get_fields(self) -> str:
        """Return the requested Open Food Facts fields."""
        return (
            "code,"
            "product_name,"
            "generic_name,"
            "brands,"
            "categories_tags,"
            "image_front_url,"
            "quantity,"
            "product_quantity,"
            "product_quantity_unit,"
            "packaging,"
            "packaging_tags"
        )

    async def get_product(
        self,
        barcode: str,
    ) -> OpenFoodFactsProduct | None:
        """Retrieve a product by barcode."""
        barcode = barcode.strip()

        if not barcode:
            return None

        url = f"{self._base_url}{self.API_PATH}/{barcode}"

        params = {
            "product_type": "food",
            "cc": self._country,
            "lc": self._language,
            "tags_lc": self._language,
            "fields": self._get_fields(),
        }

        headers = {
            "User-Agent": self._user_agent,
            "Accept": "application/json",
        }

        try:
            async with self._session.get(
                url,
                params=params,
                headers=headers,
                timeout=10,
            ) as response:
                if response.status == 404:
                    return None

                if response.status != 200:
                    _LOGGER.warning(
                        "Open Food Facts returned HTTP %s for barcode %s",
                        response.status,
                        barcode,
                    )
                    return None

                data = await response.json()

        except (ClientError, TimeoutError) as err:
            _LOGGER.warning(
                "Unable to contact Open Food Facts: %s",
                err,
            )
            return None

        return self._parse_product(data, barcode)

    async def search_products(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[OpenFoodFactsProduct]:
        """Search products by text."""
        query = query.strip()

        if not query:
            return []

        url = f"{self._base_url}{self.SEARCH_PATH}"

        params = {
            "action": "process",
            "json": 1,
            "search_terms": query,
            "page_size": max(1, min(limit, 20)),
            "fields": self._get_fields(),
            "cc": self._country,
            "lc": self._language,
        }

        headers = {
            "User-Agent": self._user_agent,
            "Accept": "application/json",
        }

        try:
            async with self._session.get(
                url,
                params=params,
                headers=headers,
                timeout=10,
            ) as response:
                if response.status != 200:
                    _LOGGER.warning(
                        "Open Food Facts search returned HTTP %s",
                        response.status,
                    )
                    return []

                data = await response.json()

        except (ClientError, TimeoutError) as err:
            _LOGGER.warning(
                "Unable to search Open Food Facts: %s",
                err,
            )
            return []

        products_data = data.get("products", [])

        if not isinstance(products_data, list):
            return []

        products = []

        for product_data in products_data:
            if not isinstance(product_data, dict):
                continue

            product = self._parse_product(
                {"product": product_data},
                str(product_data.get("code", "")),
            )

            if product is not None:
                products.append(product)

        return products

    @staticmethod
    def _parse_product(
        data: dict[str, Any],
        barcode: str,
    ) -> OpenFoodFactsProduct | None:
        """Parse a product response."""
        product = data.get("product")

        if not isinstance(product, dict):
            return None

        product_name = (
            product.get("product_name")
            or product.get("generic_name")
            or ""
        ).strip()

        if not product_name:
            return None

        categories = product.get("categories_tags")

        if not isinstance(categories, list):
            categories = []

        categories = [
            category
            for category in categories
            if isinstance(category, str)
        ]

        packaging_tags = product.get("packaging_tags")

        if not isinstance(packaging_tags, list):
            packaging_tags = []

        packaging_tags = [
            tag
            for tag in packaging_tags
            if isinstance(tag, str)
        ]

        product_quantity = product.get("product_quantity")

        try:
            if product_quantity is not None:
                product_quantity = float(product_quantity)
        except (TypeError, ValueError):
            product_quantity = None

        return OpenFoodFactsProduct(
            barcode=str(product.get("code") or barcode),
            name=product_name,
            generic_name=(
                str(product["generic_name"]).strip()
                if product.get("generic_name")
                else None
            ),
            brands=(
                str(product["brands"]).strip()
                if product.get("brands")
                else None
            ),
            categories=categories,
            image_url=(
                str(product["image_front_url"]).strip()
                if product.get("image_front_url")
                else None
            ),
            quantity=(
                str(product["quantity"]).strip()
                if product.get("quantity")
                else None
            ),
            product_quantity=product_quantity,
            product_quantity_unit=(
                str(product["product_quantity_unit"]).strip()
                if product.get("product_quantity_unit")
                else None
            ),
            packaging=(
                str(product["packaging"]).strip()
                if product.get("packaging")
                else None
            ),
            packaging_tags=packaging_tags,
        )