from custom_components.mon_panier.const import DOMAIN
from custom_components.mon_panier.core.repository import MonPanierRepository
from custom_components.mon_panier.storage import MonPanierStorage


async def test_async_setup(hass) -> None:
    from custom_components.mon_panier import async_setup

    assert await async_setup(hass, {}) is True

    assert DOMAIN in hass.data
    assert isinstance(hass.data[DOMAIN]["storage"], MonPanierStorage)
    assert isinstance(hass.data[DOMAIN]["repository"], MonPanierRepository)
    assert hass.services.has_service(DOMAIN, "create_store")


async def test_create_store_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    store = repository.get_stores()[0]

    assert store.name == "Carrefour"
    assert store.id == "carrefour"
    assert repository.get_list("carrefour") is not None


async def test_create_store_service_persists(hass) -> None:
    from custom_components.mon_panier import async_setup
    from custom_components.mon_panier.storage import MonPanierStorage

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    storage = MonPanierStorage(hass)
    restored = await storage.async_load()

    assert len(restored.stores) == 1
    assert restored.stores[0].id == "carrefour"
    assert restored.stores[0].name == "Carrefour"


async def test_rename_store_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "rename_store",
        {
            "store": "carrefour",
            "name": "Carrefour Market",
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    store = repository.get_store("carrefour")

    assert store is not None
    assert store.name == "Carrefour Market"

    restored = await hass.data[DOMAIN]["storage"].async_load()

    assert restored.stores[0].name == "Carrefour Market"


async def test_delete_store_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "delete_store",
        {"store": "carrefour"},
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]

    assert repository.get_store("carrefour") is None
    assert repository.get_list("carrefour") is None

    restored = await hass.data[DOMAIN]["storage"].async_load()

    assert restored.stores == []
    assert restored.lists == []


async def test_add_item_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    assert len(shopping_list.items) == 1
    assert shopping_list.items[0].product_id == "bananes"
    assert shopping_list.items[0].quantity == 2

    restored = await hass.data[DOMAIN]["storage"].async_load()

    assert len(restored.lists[0].items) == 1
    assert restored.lists[0].items[0].product_id == "bananes"
    assert restored.lists[0].items[0].quantity == 2


async def test_add_item_service_parses_text(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "text": "5 bananes",
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    assert len(shopping_list.items) == 1
    assert shopping_list.items[0].product_id == "bananes"
    assert shopping_list.items[0].quantity == 5
    assert shopping_list.items[0].unit == "piece"


async def test_remove_item_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    assert len(shopping_list.items) == 1

    item_id = shopping_list.items[0].id

    await hass.services.async_call(
        DOMAIN,
        "remove_item",
        {
            "store": "carrefour",
            "item_id": item_id,
        },
        blocking=True,
    )

    assert shopping_list.items == []

    restored = await hass.data[DOMAIN]["storage"].async_load()
    assert restored.lists[0].items == []


async def test_update_item_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    item_id = shopping_list.items[0].id

    await hass.services.async_call(
        DOMAIN,
        "update_item",
        {
            "store": "carrefour",
            "item_id": item_id,
            "quantity": 5,
            "unit": "kg",
            "bio": True,
            "promotion": True,
            "large_quantity": True,
        },
        blocking=True,
    )

    item = shopping_list.items[0]

    assert item.quantity == 5
    assert item.unit == "kg"
    assert item.bio is True
    assert item.promotion is True
    assert item.large_quantity is True

    restored = await hass.data[DOMAIN]["storage"].async_load()
    restored_item = restored.lists[0].items[0]

    assert restored_item.quantity == 5
    assert restored_item.unit == "kg"
    assert restored_item.bio is True
    assert restored_item.promotion is True
    assert restored_item.large_quantity is True


async def test_complete_item_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    item = shopping_list.items[0]

    await hass.services.async_call(
        DOMAIN,
        "complete_item",
        {
            "store": "carrefour",
            "item_id": item.id,
        },
        blocking=True,
    )

    assert item.checked is True

    product = repository.get_product("bananes")
    assert product is not None
    assert product.purchase_count == 1
    assert product.last_purchased is not None

    history = repository.get_history()
    assert len(history) == 1
    assert history[0].product_id == "bananes"
    assert history[0].product_name == "Bananes"
    assert history[0].quantity == 2

    restored = await hass.data[DOMAIN]["storage"].async_load()

    restored_item = restored.lists[0].items[0]
    assert restored_item.checked is True

    restored_product = restored.products[0]
    assert restored_product.purchase_count == 1
    assert restored_product.last_purchased is not None

    assert len(restored.history) == 1


async def test_uncomplete_item_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    item = shopping_list.items[0]

    await hass.services.async_call(
        DOMAIN,
        "complete_item",
        {
            "store": "carrefour",
            "item_id": item.id,
        },
        blocking=True,
    )

    assert item.checked is True

    await hass.services.async_call(
        DOMAIN,
        "uncomplete_item",
        {
            "store": "carrefour",
            "item_id": item.id,
        },
        blocking=True,
    )

    assert item.checked is False

    restored = await hass.data[DOMAIN]["storage"].async_load()
    assert restored.lists[0].items[0].checked is False


async def test_clear_list_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "pommes",
            "quantity": 3,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    assert len(shopping_list.items) == 2

    await hass.services.async_call(
        DOMAIN,
        "clear_list",
        {"store": "carrefour"},
        blocking=True,
    )

    assert shopping_list.items == []

    restored = await hass.data[DOMAIN]["storage"].async_load()
    assert restored.lists[0].items == []


async def test_delete_list_service(hass) -> None:
    from custom_components.mon_panier import async_setup

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "product": "bananes",
            "quantity": 2,
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]

    assert repository.get_list("carrefour") is not None
    assert len(repository.get_list("carrefour").items) == 1

    await hass.services.async_call(
        DOMAIN,
        "delete_list",
        {"store": "carrefour"},
        blocking=True,
    )

    assert repository.get_list("carrefour") is None

    restored = await hass.data[DOMAIN]["storage"].async_load()
    assert restored.lists == []

async def test_add_item_service_creates_openfoodfacts_confirmation(hass) -> None:
    from unittest.mock import AsyncMock

    from custom_components.mon_panier import async_setup
    from custom_components.mon_panier.integrations.openfoodfacts import (
        OpenFoodFactsProduct,
    )

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    external_product = OpenFoodFactsProduct(
        barcode="3564700299067",
        name="Sauce mexicaine medium",
        brands="Marque Repère, Tables du Monde",
        quantity="315 g",
        product_quantity=315.0,
        product_quantity_unit="g",
        packaging="Verre, Bocal",
        packaging_tags=["en:glass", "en:jar"],
    )

    product_service = hass.data[DOMAIN]["product_service"]
    product_service.openfoodfacts = AsyncMock()

    product_service.openfoodfacts.search_products.return_value = [
        external_product,
    ]

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "text": "sauce mexicaine",
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]

    shopping_list = repository.get_list("carrefour")
    assert shopping_list is not None
    assert shopping_list.items == []

    assert repository.get_product("sauce_mexicaine_medium") is None

    pending = hass.data[DOMAIN]["pending_confirmations"]

    assert "3564700299067" in pending
    assert pending["3564700299067"]["store"] == "carrefour"
    assert pending["3564700299067"]["quantity"] == 1
    assert pending["3564700299067"]["unit"] == "piece"
    assert pending["3564700299067"]["external_product"] == external_product

async def test_confirm_product_service_memorizes_and_adds_product(hass) -> None:
    from unittest.mock import AsyncMock

    from custom_components.mon_panier import async_setup
    from custom_components.mon_panier.integrations.openfoodfacts import (
        OpenFoodFactsProduct,
    )

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    external_product = OpenFoodFactsProduct(
        barcode="3564700299067",
        name="Sauce mexicaine medium",
        brands="Marque Repère, Tables du Monde",
        quantity="315 g",
        product_quantity=315.0,
        product_quantity_unit="g",
        packaging="Verre, Bocal",
        packaging_tags=["en:glass", "en:jar"],
    )

    product_service = hass.data[DOMAIN]["product_service"]
    product_service.openfoodfacts = AsyncMock()
    product_service.openfoodfacts.search_products.return_value = [
        external_product,
    ]

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "text": "sauce mexicaine",
        },
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "confirm_product",
        {
            "confirmation_id": "3564700299067",
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]

    product = repository.get_product("sauce_mexicaine_medium")
    assert product is not None
    assert product.name == "Sauce mexicaine medium"
    assert product.source == "openfoodfacts"
    assert product.brand == "Marque Repère, Tables du Monde"
    assert product.quantity == "315 g"
    assert product.product_quantity == 315.0
    assert product.product_quantity_unit == "g"
    assert product.packaging == "Verre, Bocal"
    assert product.packaging_tags == ["en:glass", "en:jar"]

    assert "3564700299067" in product.barcodes

    shopping_list = repository.get_list("carrefour")
    assert shopping_list is not None
    assert len(shopping_list.items) == 1
    assert shopping_list.items[0].product_id == "sauce_mexicaine_medium"
    assert shopping_list.items[0].quantity == 1
    assert shopping_list.items[0].unit == "piece"

    assert "3564700299067" not in hass.data[DOMAIN]["pending_confirmations"]

async def test_confirm_product_service_keeps_purchase_quantity_and_unit(
    hass,
) -> None:
    """Confirming a parsed package input keeps the purchase quantity."""
    from unittest.mock import AsyncMock

    from custom_components.mon_panier import async_setup
    from custom_components.mon_panier.integrations.openfoodfacts import (
        OpenFoodFactsProduct,
    )

    await async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        "create_store",
        {"name": "Carrefour"},
        blocking=True,
    )

    external_product = OpenFoodFactsProduct(
        barcode="3564700299067",
        name="Sauce mexicaine medium",
        brands="Marque Repère, Tables du Monde",
        quantity="315 g",
        product_quantity=315.0,
        product_quantity_unit="g",
        packaging="Verre, Bocal",
        packaging_tags=["en\:glass", "en\:jar"],
    )

    product_service = hass.data[DOMAIN]["product_service"]
    product_service.openfoodfacts = AsyncMock()
    product_service.openfoodfacts.search_products.return_value = [
        external_product,
    ]

    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {
            "store": "carrefour",
            "text": "2 pots de 300g de sauce mexicaine",
        },
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        "confirm_product",
        {
            "confirmation_id": "3564700299067",
        },
        blocking=True,
    )

    repository = hass.data[DOMAIN]["repository"]
    shopping_list = repository.get_list("carrefour")

    assert shopping_list is not None
    assert len(shopping_list.items) == 1

    item = shopping_list.items[0]
    assert item.product_id == "sauce_mexicaine_medium"
    assert item.quantity == 2
    assert item.unit == "pot"
