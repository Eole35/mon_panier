from custom_components.mon_panier.core.models import MonPanierData, Store
from custom_components.mon_panier.storage import MonPanierStorage


async def test_storage_round_trip(hass) -> None:
    storage = MonPanierStorage(hass)

    data = MonPanierData(
        stores=[
            Store(
                id="carrefour",
                name="Carrefour",
            )
        ]
    )

    await storage.async_save(data)

    restored = await storage.async_load()

    assert restored.schema_version == 1
    assert restored.stores[0].id == "carrefour"
    assert restored.stores[0].name == "Carrefour"
