"""Config flow for the Mon Panier integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import DEFAULT_STORE_NAME, DOMAIN


class MonPanierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mon Panier."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=DEFAULT_STORE_NAME,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return MonPanierOptionsFlow(config_entry)


class MonPanierOptionsFlow(config_entries.OptionsFlow):
    """Handle Mon Panier options."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage Mon Panier options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )
