
class InventoryError(Exception):
    """Base exception for excepted business error"""



class FoodItemNotAvailableError(InventoryError):
    ...


class FoodItemExpiredError(InventoryError):
    ...