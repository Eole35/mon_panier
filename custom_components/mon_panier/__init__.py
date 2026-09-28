"""The Mon Panier integration."""

from __future__ import annotations

from pathlib import Path

import homeassistant.helpers.config_validation as cv

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .barcode import BarcodeScanner
from .const import (
    CONF_OFF_ENABLED,
    DEFAULT_OFF_ENABLED,
    DOMAIN,
)
from .core.catalog import ProductCatalog
from .core.category_mapper import CategoryMapper
from .core.learning import LearningEngine
from .core.product_service import ProductService
from .core.repository import MonPanierRepository
from .integrations.openfoodfacts import OpenFoodFactsClient
from .services import (
    async_add_item,
    async_clear_list,
    async_complete_item,
    async_confirm_product,
    async_create_store,
    async_delete_list,
    async_delete_store,
    async_reject_product,
    async_remove_item,
    async_rename_store,
    async_uncomplete_item,
    async_update_item,
)
from .storage import MonPanierStorage


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Mon Panier integration."""
    storage = MonPanierStorage(hass)
    data = await storage.async_load()
    repository = MonPanierRepository(data)

    catalog_path = Path(__file__).parent / "data" / "products.json"
    catalog = ProductCatalog.from_file(catalog_path)

    learning = LearningEngine(
        personal_rules=data.personal_rules,
        category_overrides=data.category_overrides,
    )

    product_service = ProductService(
        repository=repository,
        catalog=catalog,
        learning=learning,
        barcode_scanner=BarcodeScanner(),
        category_mapper=CategoryMapper(),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["storage"] = storage
    hass.data[DOMAIN]["repository"] = repository
    hass.data[DOMAIN]["product_service"] = product_service
    hass.data[DOMAIN]["pending_confirmations"] = {}

    async def handle_add_item(call):
        await async_add_item(hass, call)

    hass.services.async_register(
        DOMAIN,
        "add_item",
        handle_add_item,
    )

    async def handle_confirm_product(call):
        await async_confirm_product(hass, call)

    hass.services.async_register(
        DOMAIN,
        "confirm_product",
        handle_confirm_product,
    )

    async def handle_reject_product(call):
        await async_reject_product(hass, call)

    hass.services.async_register(
        DOMAIN,
        "reject_product",
        handle_reject_product,
    )

    async def handle_create_store(call):
        await async_create_store(hass, call)

    hass.services.async_register(
        DOMAIN,
        "create_store",
        handle_create_store,
    )

    async def handle_rename_store(call):
        await async_rename_store(hass, call)

    hass.services.async_register(
        DOMAIN,
        "rename_store",
        handle_rename_store,
    )

    async def handle_delete_store(call):
        await async_delete_store(hass, call)

    hass.services.async_register(
        DOMAIN,
        "delete_store",
        handle_delete_store,
    )

    async def handle_remove_item(call):
        await async_remove_item(hass, call)

    hass.services.async_register(
        DOMAIN,
        "remove_item",
        handle_remove_item,
    )

    async def handle_update_item(call):
        await async_update_item(hass, call)

    hass.services.async_register(
        DOMAIN,
        "update_item",
        handle_update_item,
    )

    async def handle_complete_item(call):
        await async_complete_item(hass, call)

    hass.services.async_register(
        DOMAIN,
        "complete_item",
        handle_complete_item,
    )

    async def handle_uncomplete_item(call):
        await async_uncomplete_item(hass, call)

    hass.services.async_register(
        DOMAIN,
        "uncomplete_item",
        handle_uncomplete_item,
    )

    async def handle_clear_list(call):
        await async_clear_list(hass, call)

    hass.services.async_register(
        DOMAIN,
        "clear_list",
        handle_clear_list,
    )

    async def handle_delete_list(call):
        await async_delete_list(hass, call)

    hass.services.async_register(
        DOMAIN,
        "delete_list",
        handle_delete_list,
    )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Mon Panier from a config entry."""
    product_service = hass.data[DOMAIN]["product_service"]

    off_enabled = entry.options.get(
        CONF_OFF_ENABLED,
        DEFAULT_OFF_ENABLED,
    )

    if off_enabled:
        session = async_get_clientsession(hass)
        product_service.openfoodfacts = OpenFoodFactsClient(
            session,
            entry.options,
        )
    else:
        product_service.openfoodfacts = None

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor"],
    )

    return True