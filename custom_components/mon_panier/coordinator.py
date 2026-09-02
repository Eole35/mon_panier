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
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "items": [],
            "items_count": 0,
            "purchased_count": 0,
        }
