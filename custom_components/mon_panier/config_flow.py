"""Config flow for the Mon Panier integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_OFF_COUNTRY,
    CONF_OFF_ENABLED,
    CONF_OFF_LANGUAGE,
    CONF_OFF_URL,
    CONF_OFF_USER_AGENT,
    DEFAULT_OFF_COUNTRY,
    DEFAULT_OFF_ENABLED,
    DEFAULT_OFF_LANGUAGE,
    DEFAULT_OFF_URL,
    DEFAULT_OFF_USER_AGENT,
    DOMAIN,
)


class MonPanierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mon Panier."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup."""
        if user_input is not None:
            return self.async_create_entry(
                title="Mon Panier",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return MonPanierOptionsFlow()


class MonPanierOptionsFlow(config_entries.OptionsFlow):
    """Handle Mon Panier options."""

    async def async_step_init(self, user_input=None):
        """Manage Mon Panier options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_OFF_ENABLED,
                    default=self.config_entry.options.get(
                        CONF_OFF_ENABLED,
                        DEFAULT_OFF_ENABLED,
                    ),
                ): bool,
                vol.Required(
                    CONF_OFF_URL,
                    default=self.config_entry.options.get(
                        CONF_OFF_URL,
                        DEFAULT_OFF_URL,
                    ),
                ): str,
                vol.Required(
                    CONF_OFF_COUNTRY,
                    default=self.config_entry.options.get(
                        CONF_OFF_COUNTRY,
                        DEFAULT_OFF_COUNTRY,
                    ),
                ): str,
                vol.Required(
                    CONF_OFF_LANGUAGE,
                    default=self.config_entry.options.get(
                        CONF_OFF_LANGUAGE,
                        DEFAULT_OFF_LANGUAGE,
                    ),
                ): str,
                vol.Required(
                    CONF_OFF_USER_AGENT,
                    default=self.config_entry.options.get(
                        CONF_OFF_USER_AGENT,
                        DEFAULT_OFF_USER_AGENT,
                    ),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
