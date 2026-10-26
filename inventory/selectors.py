from django.utils import timezone

from inventory.models import FoodItem, Reservation


def get_available_food_items():
    return FoodItem.objects.filter(
        status=FoodItem.Status.AVAILABLE,
        expiry_date__gte=timezone.localdate()
    ).select_related(
        "category",
        "location"
    )


def get_user_reservations(user):
    return Reservation.objects.filter(
        volunteer=user
    ).select_related(
        "food_item"
    )
