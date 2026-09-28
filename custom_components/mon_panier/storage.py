"""Persistent storage for Mon Panier."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .core.models import MonPanierData


STORAGE_VERSION = 1
STORAGE_KEY = "mon_panier.data"


class MonPanierStorage:
    """Persist Mon Panier data using Home Assistant storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.store = Store[dict[str, Any]](
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )

    async def async_load(self) -> MonPanierData:
        """Load Mon Panier data."""
        data = await self.store.async_load()

        if data is None:
            return MonPanierData()

        return MonPanierData.from_dict(data)

    async def async_save(self, data: MonPanierData) -> None:
        """Save Mon Panier data."""
        await self.store.async_save(data.to_dict())
