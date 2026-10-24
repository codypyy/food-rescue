from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory.models import FoodItem, Reservation


@transaction.atomic
def reserve_food_item(*, food_item_id, volunteer):
    food_item = FoodItem.objects.select_for_update().get(id=food_item_id)

    if food_item.status != FoodItem.Status.AVAILABLE:
        raise ValidationError(
            "This food item is not available."
        )

    if food_item.expiry_date < timezone.localdate():
        raise ValidationError(
            "Expired food cannot be reserved."
        )

    if Reservation.objects.filter(
        food_item=food_item,
        status=Reservation.Status.ACTIVE
    ).exists():
        raise ValidationError(
            "This food item already has an active reservation."
        )
    
    reservation = Reservation.objects.create(
        food_item=food_item,
        volunteer=volunteer,
        status=Reservation.Status.ACTIVE
    )

    food_item.status = FoodItem.Status.RESERVED
    food_item.save(
        update_fields=["status"]
    )

    return reservation


@transaction.atomic
def donate_reserved_food(*, reservation_id):

    food_item_id = Reservation.objects.values_list(
        "food_item_id",
        flat=True
    ).get(id=reservation_id)

    food_item = FoodItem.objects.select_for_update().get(
        id=food_item_id
    )

    reservation = Reservation.objects.select_for_update.get(
        id=reservation_id,
        food_item=food_item
    )

    if reservation.status != Reservation.Status.ACTIVE:
        raise ValidationError(
            "Reservation is not active."
        )

    if food_item.status != FoodItem.Status.RESERVED:
        raise ValidationError(
            "This food item is not reserved."
        )

    reservation.status = Reservation.Status.COMPLETED
    reservation.save(update_fields=["status"])

    food_item.status = FoodItem.Status.DONATED
    food_item.save(update_fields=["status"])

    return reservation
