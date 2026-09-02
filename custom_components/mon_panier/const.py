"""Constants for the Mon Panier integration."""

DOMAIN = "mon_panier"
NAME = "Mon Panier"
VERSION = "0.1.0"

# Configuration
CONF_STORE = "store"

# Defaults
DEFAULT_STORE_NAME = "Mon magasin"

# Events
EVENT_ITEM_ADDED = f"{DOMAIN}_item_added"
EVENT_ITEM_COMPLETED = f"{DOMAIN}_item_completed"
EVENT_STORE_CREATED = f"{DOMAIN}_store_created"
EVENT_STORE_DELETED = f"{DOMAIN}_store_deleted"

# Services
SERVICE_ADD_ITEM = "add_item"
SERVICE_REMOVE_ITEM = "remove_item"
SERVICE_UPDATE_ITEM = "update_item"
SERVICE_COMPLETE_ITEM = "complete_item"
SERVICE_UNCOMPLETE_ITEM = "uncomplete_item"
SERVICE_CLEAR_LIST = "clear_list"
SERVICE_DELETE_LIST = "delete_list"
SERVICE_CREATE_STORE = "create_store"
SERVICE_RENAME_STORE = "rename_store"
SERVICE_DELETE_STORE = "delete_store"

# Product sources
SOURCE_BUILTIN = "builtin"
SOURCE_PERSONAL = "personal"
SOURCE_OPENFOODFACTS = "openfoodfacts"

# Units
UNIT_PIECE = "piece"
UNIT_PACKAGE = "paquet"
UNIT_BOX = "boîte"
UNIT_BOTTLE = "bouteille"
UNIT_CAN = "bidon"
UNIT_JAR = "pot"
UNIT_BAG = "sachet"
UNIT_TRAY = "barquette"
UNIT_ROLL = "rouleau"
UNIT_SET = "lot"

UNIT_GRAM = "g"
UNIT_KILOGRAM = "kg"
UNIT_MILLILITER = "ml"
UNIT_CENTILITER = "cl"
UNIT_LITER = "l"
