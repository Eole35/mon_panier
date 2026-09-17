"""Tests for the Mon Panier config flow."""

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.mon_panier.const import (
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


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Test that the user flow creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is config_entries.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )

    assert result["type"] is config_entries.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Mon Panier"
    assert result["data"] == {}


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_options_flow_uses_defaults(hass: HomeAssistant) -> None:
    """Test that the options flow exposes the expected defaults."""
    entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Mon Panier",
        data={},
        source=config_entries.SOURCE_USER,
        unique_id=None,
        discovery_keys={},
        options={},
        subentries_data={},
    )

    with patch.object(
        hass.config_entries,
        "async_entries",
        return_value=[entry],
    ):
        result = await hass.config_entries.options.async_init(
            entry.entry_id,
            context={"source": "init"},
        )

    assert result["type"] is config_entries.FlowResultType.FORM
    assert result["step_id"] == "init"

    schema = result["data_schema"]

    assert schema({})[CONF_OFF_ENABLED] is DEFAULT_OFF_ENABLED
    assert schema({})[CONF_OFF_URL] == DEFAULT_OFF_URL
    assert schema({})[CONF_OFF_COUNTRY] == DEFAULT_OFF_COUNTRY
    assert schema({})[CONF_OFF_LANGUAGE] == DEFAULT_OFF_LANGUAGE
    assert schema({})[CONF_OFF_USER_AGENT] == DEFAULT_OFF_USER_AGENT


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_options_flow_saves_values(hass: HomeAssistant) -> None:
    """Test that the options flow saves Open Food Facts settings."""
    entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Mon Panier",
        data={},
        source=config_entries.SOURCE_USER,
        unique_id=None,
        discovery_keys={},
        options={},
        subentries_data={},
    )

    hass.config_entries._entries.append(entry)

    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        context={"source": "init"},
    )

    assert result["type"] is config_entries.FlowResultType.FORM

    user_input = {
        CONF_OFF_ENABLED: False,
        CONF_OFF_URL: "https://example.test",
        CONF_OFF_COUNTRY: "be",
        CONF_OFF_LANGUAGE: "fr",
        CONF_OFF_USER_AGENT: "MonPanier/test",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=user_input,
    )

    assert result["type"] is config_entries.FlowResultType.CREATE_ENTRY
    assert result["data"] == user_input
