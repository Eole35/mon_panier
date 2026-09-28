"""Data coordinator for the Mon Panier integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MonPanierCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Mon Panier data."""

    def __init__(
        self,
        hass: HomeAssistant,
        store_id: str,
        store_name: str,
    ) -> None:
        """Initialize the Mon Panier coordinator."""
        self.store_id = store_id
        self.store_name = store_name

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{store_id}",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest Mon Panier data."""
        repository = self.hass.data[DOMAIN]["repository"]

        store = repository.get_store(self.store_id)
        shopping_list = repository.get_list(self.store_id)

        store_name = (
            store.name
            if store is not None
            else self.store_name
        )

        if shopping_list is None:
            return {
                "store_id": self.store_id,
                "store_name": store_name,
                "items": [],
                "items_count": 0,
                "purchased_count": 0,
            }

        items = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit": item.unit,
                "checked": item.checked,
                "bio": item.bio,
                "promotion": item.promotion,
                "large_quantity": item.large_quantity,
            }
            for item in shopping_list.items
        ]

        items_count = sum(
            1
            for item in shopping_list.items
            if not item.checked
        )

        purchased_count = sum(
            1
            for item in shopping_list.items
            if item.checked
        )

        return {
            "store_id": self.store_id,
            "store_name": store_name,
            "items": items,
            "items_count": items_count,
            "purchased_count": purchased_count,
        }