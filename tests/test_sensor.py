"""Tests for the Mon Panier sensor."""

from __future__ import annotations

import pytest
from homeassistant.helpers.dispatcher import async_dispatcher_send

from custom_components.mon_panier.core.models import MonPanierData
from custom_components.mon_panier.core.repository import MonPanierRepository


@pytest.mark.asyncio
async def test_repository_store_and_list_are_linked() -> None:
    """Test that a store and its shopping list use the same ID."""
    repository = MonPanierRepository(MonPanierData())
    store = repository.create_store("Carrefour")

    assert store.id == "carrefour"

    shopping_list = repository.get_list(store.id)

    assert shopping_list is not None
    assert shopping_list.store_id == "carrefour"


@pytest.mark.asyncio
async def test_coordinator_reads_shopping_list(hass) -> None:
    """Test that the coordinator returns the shopping list data."""
    from custom_components.mon_panier.const import DOMAIN
    from custom_components.mon_panier.coordinator import MonPanierCoordinator

    repository = MonPanierRepository(MonPanierData())
    store = repository.create_store("Carrefour")

    bananas = repository.add_product(
        name="Bananes",
        category="fruits",
        product_id="bananes",
    )

    apples = repository.add_product(
        name="Pommes",
        category="fruits",
        product_id="pommes",
    )

    repository.add_item(
        store.id,
        bananas.id,
        quantity=2,
    )

    repository.add_item(
        store.id,
        apples.id,
        quantity=1,
    )

    repository.get_list(store.id).items[1].checked = True

    hass.data[DOMAIN] = {
        "repository": repository,
    }

    coordinator = MonPanierCoordinator(
        hass,
        store_id=store.id,
        store_name=store.name,
    )

    data = await coordinator._async_update_data()

    assert data["store_id"] == "carrefour"
    assert data["store_name"] == "Carrefour"
    assert data["items_count"] == 1
    assert data["purchased_count"] == 1
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_coordinator_reads_renamed_store(hass) -> None:
    """Test that the coordinator uses the current store name."""
    from custom_components.mon_panier.const import DOMAIN
    from custom_components.mon_panier.coordinator import MonPanierCoordinator

    repository = MonPanierRepository(MonPanierData())
    store = repository.create_store("Carrefour")

    hass.data[DOMAIN] = {
        "repository": repository,
    }

    coordinator = MonPanierCoordinator(
        hass,
        store_id=store.id,
        store_name=store.name,
    )

    repository.rename_store(store.id, "Leclerc")

    data = await coordinator._async_update_data()

    assert data["store_id"] == "carrefour"
    assert data["store_name"] == "Leclerc"


@pytest.mark.asyncio
async def test_sensor_name_updates_after_store_rename(hass) -> None:
    """Test that the sensor name follows the current store name."""
    from custom_components.mon_panier.const import DOMAIN
    from custom_components.mon_panier.coordinator import MonPanierCoordinator
    from custom_components.mon_panier.sensor import MonPanierSensor

    repository = MonPanierRepository(MonPanierData())
    store = repository.create_store("Carrefour")

    hass.data[DOMAIN] = {
        "repository": repository,
    }

    coordinator = MonPanierCoordinator(
        hass,
        store_id=store.id,
        store_name=store.name,
    )

    await coordinator.async_refresh()

    sensor = MonPanierSensor(coordinator)

    assert sensor.name == "Carrefour"

    repository.rename_store(store.id, "Leclerc")

    await coordinator.async_refresh()

    sensor._attr_name = coordinator.data["store_name"]

    assert sensor.name == "Leclerc"


@pytest.mark.asyncio
async def test_sensor_setup_creates_one_sensor_per_store(hass) -> None:
    """Test that sensor setup creates one sensor for each store."""
    from custom_components.mon_panier.const import DOMAIN
    from custom_components.mon_panier.sensor import async_setup_entry

    repository = MonPanierRepository(MonPanierData())
    repository.create_store("Carrefour")
    repository.create_store("Leclerc")

    hass.data[DOMAIN] = {
        "repository": repository,
    }

    added_entities = []

    def add_entities(entities) -> None:
        added_entities.extend(entities)

    await async_setup_entry(
        hass,
        None,
        add_entities,
    )

    assert len(added_entities) == 2
    assert {
        entity.coordinator.store_id
        for entity in added_entities
    } == {"carrefour", "leclerc"}


@pytest.mark.asyncio
async def test_create_store_creates_sensor_automatically(hass) -> None:
    """Test that a store creation signal creates a sensor automatically."""
    from custom_components.mon_panier.const import (
        DOMAIN,
        EVENT_STORE_CREATED,
    )
    from custom_components.mon_panier.sensor import async_setup_entry

    repository = MonPanierRepository(MonPanierData())
    repository.create_store("Carrefour")

    hass.data[DOMAIN] = {
        "repository": repository,
    }

    added_entities = []

    def add_entities(entities) -> None:
        added_entities.extend(entities)

    await async_setup_entry(
        hass,
        None,
        add_entities,
    )

    assert len(added_entities) == 1

    store = repository.create_store("Leclerc")

    async_dispatcher_send(
        hass,
        EVENT_STORE_CREATED,
        store.id,
    )

    await hass.async_block_till_done()

    assert len(added_entities) == 2
    assert {
        entity.coordinator.store_id
        for entity in added_entities
    } == {"carrefour", "leclerc"}