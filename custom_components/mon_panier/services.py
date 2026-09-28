"""Services for Mon Panier."""

from __future__ import annotations

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, EVENT_STORE_CREATED
from .core.parser import ShoppingInputParser


async def async_create_store(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Create a new Mon Panier store."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]
    name = call.data["name"]

    store = repository.create_store(name)

    await storage.async_save(repository.data)

    async_dispatcher_send(
        hass,
        EVENT_STORE_CREATED,
        store.id,
    )


async def async_rename_store(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Rename an existing Mon Panier store."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.rename_store(
        call.data["store"],
        call.data["name"],
    )

    await storage.async_save(repository.data)


async def async_delete_store(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Delete an existing Mon Panier store."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.delete_store(call.data["store"])

    await storage.async_save(repository.data)


async def async_add_item(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Add an item to a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]
    product_service = hass.data[DOMAIN]["product_service"]

    product_value = call.data.get("product") or call.data.get("text")

    if not product_value:
        raise ValueError("A product or text is required")

    quantity = call.data.get("quantity")
    unit = call.data.get("unit")

    parsed = None

    if call.data.get("text") and not call.data.get("product"):
        parsed = ShoppingInputParser().parse(product_value)
        product_value = parsed.text

        if quantity is None:
            quantity = parsed.quantity

        if unit is None:
            unit = parsed.unit

    result = await product_service.find_by_text(product_value)

    if result.requires_confirmation:
        external_product = result.external_product

        if external_product is None:
            raise ValueError(
                f"Product requires confirmation: {product_value}",
            )

        pending_id = external_product.barcode

        hass.data[DOMAIN]["pending_confirmations"][pending_id] = {
            "store": call.data["store"],
            "quantity": quantity if quantity is not None else 1,
            "unit": unit if unit is not None else "piece",
            "product_value": product_value,
            "external_product": external_product,
            "category": result.category,
        }

        details = [
            f"**Produit :** {external_product.name}",
        ]

        if external_product.brands:
            details.append(
                f"**Marque :** {external_product.brands}",
            )

        if external_product.quantity:
            details.append(
                f"**Quantité produit :** {external_product.quantity}",
            )

        if external_product.packaging:
            details.append(
                f"**Emballage :** {external_product.packaging}",
            )

        details.append(
            f"**Code-barres :** {external_product.barcode}",
        )

        details.append("")
        details.append(
            "Pour confirmer : "
            f"`mon_panier.confirm_product` avec "
            f"`confirmation_id: {pending_id}`.",
        )
        details.append(
            "Pour refuser : "
            f"`mon_panier.reject_product` avec "
            f"`confirmation_id: {pending_id}`.",
        )

        persistent_notification.async_create(
            hass,
            "\n\n".join(details),
            title="Mon Panier — produit trouvé",
            notification_id=f"{DOMAIN}_confirmation_{pending_id}",
        )

        return

    product = result.product

    if product is None:
        raise ValueError(f"Product not found: {product_value}")

    if repository.get_product(product.id) is None:
        repository.add_product(
            product.name,
            product.category,
            product_id=product.id,
            synonyms=product.synonyms,
            source=product.source,
        )

    repository.add_item(
        call.data["store"],
        product.id,
        quantity=quantity if quantity is not None else 1,
        unit=unit if unit is not None else "piece",
    )

    await storage.async_save(repository.data)


async def async_confirm_product(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Confirm and memorize a pending Open Food Facts product."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]
    product_service = hass.data[DOMAIN]["product_service"]
    pending_confirmations = hass.data[DOMAIN]["pending_confirmations"]

    confirmation_id = call.data["confirmation_id"]
    pending = pending_confirmations.get(confirmation_id)

    if pending is None:
        raise ValueError(
            f"Unknown product confirmation: {confirmation_id}",
        )

    external_product = pending["external_product"]
    category = pending["category"]

    if category is None:
        category = "autre"

    product = product_service.memorize_external_product(
        external_product,
        category,
    )

    repository.add_item(
        pending["store"],
        product.id,
        quantity=pending["quantity"],
        unit=pending["unit"],
    )

    await storage.async_save(repository.data)

    del pending_confirmations[confirmation_id]

    persistent_notification.async_dismiss(
        hass,
        notification_id=f"{DOMAIN}_confirmation_{confirmation_id}",
    )


async def async_reject_product(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Reject a pending Open Food Facts product."""
    pending_confirmations = hass.data[DOMAIN]["pending_confirmations"]

    confirmation_id = call.data["confirmation_id"]

    if confirmation_id not in pending_confirmations:
        raise ValueError(
            f"Unknown product confirmation: {confirmation_id}",
        )

    del pending_confirmations[confirmation_id]

    persistent_notification.async_dismiss(
        hass,
        notification_id=f"{DOMAIN}_confirmation_{confirmation_id}",
    )


async def async_remove_item(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Remove an item from a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.remove_item(
        call.data["store"],
        call.data["item_id"],
    )

    await storage.async_save(repository.data)


async def async_update_item(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Update an item in a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.update_item(
        call.data["store"],
        call.data["item_id"],
        quantity=call.data["quantity"],
        unit=call.data["unit"],
        bio=call.data["bio"],
        promotion=call.data["promotion"],
        large_quantity=call.data["large_quantity"],
    )

    await storage.async_save(repository.data)


async def async_complete_item(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Complete an item in a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.complete_item(
        call.data["store"],
        call.data["item_id"],
    )

    await storage.async_save(repository.data)


async def async_uncomplete_item(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Uncomplete an item in a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.uncomplete_item(
        call.data["store"],
        call.data["item_id"],
    )

    await storage.async_save(repository.data)


async def async_clear_list(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Clear a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.clear_list(call.data["store"])

    await storage.async_save(repository.data)


async def async_delete_list(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """Delete a Mon Panier shopping list."""
    repository = hass.data[DOMAIN]["repository"]
    storage = hass.data[DOMAIN]["storage"]

    repository.delete_list(call.data["store"])

    await storage.async_save(repository.data)