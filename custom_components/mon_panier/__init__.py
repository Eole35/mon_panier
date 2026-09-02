"""The Mon Panier integration."""

from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Mon Panier integration."""
    hass.data.setdefault(DOMAIN, {})

    return True
