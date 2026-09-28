from datetime import datetime

from custom_components.mon_panier.const import UNIT_PIECE
from custom_components.mon_panier.core.models import (
    ListItem,
    MonPanierData,
    Product,
    ShoppingList,
    Store,
)


def test_mon_panier_data_round_trip() -> None:
    created_at = datetime(2026, 9, 26, 20, 0, 0)

    data = MonPanierData(
        stores=[
            Store(
                id="carrefour",
                name="Carrefour",
                category_order=["fruits", "laitiers"],
            )
        ],
        lists=[
            ShoppingList(
                id="carrefour",
                store_id="carrefour",
                items=[
                    ListItem(
                        id="item1",
                        product_id="bananes",
                        quantity=5,
                        unit=UNIT_PIECE,
                        bio=True,
                        checked=False,
                        created_at=created_at,
                    )
                ],
            )
        ],
        products=[
            Product(
                id="bananes",
                name="Bananes",
                category="fruits",
            )
        ],
    )

    restored = MonPanierData.from_dict(data.to_dict())

    assert restored.schema_version == 1
    assert restored.stores[0].name == "Carrefour"
    assert restored.lists[0].items[0].product_id == "bananes"
    assert restored.lists[0].items[0].quantity == 5
    assert restored.lists[0].items[0].bio is True
    assert restored.lists[0].items[0].created_at == created_at
    assert restored.products[0].name == "Bananes"
