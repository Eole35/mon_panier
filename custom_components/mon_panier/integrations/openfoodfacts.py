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


class OpenFoodFactsClient:
    """Client for the Open Food Facts API."""

    API_PATH = "/api/v3/product"

    def __init__(
        self,
        session: ClientSession,
        options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the Open Food Facts client."""
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

    async def get_product(
        self,
        barcode: str,
    ) -> OpenFoodFactsProduct | None:
        """Retrieve a product from Open Food Facts."""
        barcode = barcode.strip()

        if not barcode:
            return None

        url = f"{self._base_url}{self.API_PATH}/{barcode}"

        params = {
            "product_type": "food",
            "cc": self._country,
            "lc": self._language,
            "tags_lc": self._language,
            "fields": (
                "code,"
                "product_name,"
                "generic_name,"
                "brands,"
                "categories_tags,"
                "image_front_url"
            ),
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

    @staticmethod
    def _parse_product(
        data: dict[str, Any],
        barcode: str,
    ) -> OpenFoodFactsProduct | None:
        """Parse an Open Food Facts response."""
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
        )
