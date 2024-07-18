from enum import Enum


class GetObjectTemplateTypeType(str, Enum):
    COLLECTION = "collection"
    FOLDER = "folder"
    ITEM = "item"
    ITEM_CARD = "item.card"
    ITEM_COLLECTIONS = "item-collections"
    ITEM_FIELD = "item.field"
    ITEM_IDENTITY = "item.identity"
    ITEM_LOGIN = "item.login"
    ITEM_LOGIN_URI = "item.login.uri"
    ITEM_SECURENOTE = "item.securenote"
    ORG_COLLECTION = "org-collection"

    def __str__(self) -> str:
        return str(self.value)
