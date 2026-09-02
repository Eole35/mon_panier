"""Sensor platform for the Mon Panier integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MonPanierCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mon Panier sensors from a config entry."""
    store_name = entry.data.get("name", entry.title)
    store_id = entry.entry_id

    coordinator = MonPanierCoordinator(
        hass,
        store_id=store_id,
        store_name=store_name,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            MonPanierSensor(coordinator),
        ]
    )


class MonPanierSensor(
    CoordinatorEntity[MonPanierCoordinator],
    SensorEntity,
):
    """Representation of a Mon Panier store."""

    _attr_native_unit_of_measurement = "articles"
    _attr_icon = "mdi:cart"

    def __init__(self, coordinator: MonPanierCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attr_name = coordinator.store_name
        self._attr_unique_id = f"{DOMAIN}_{coordinator.store_id}"

    @property
    def native_value(self) -> int:
        """Return the number of active shopping items."""
        return self.coordinator.data["items_count"]

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return additional sensor attributes."""
        data = self.coordinator.data

        return {
            "store_id": data["store_id"],
            "store_name": data["store_name"],
            "items_count": data["items_count"],
            "purchased_count": data["purchased_count"],
        }
