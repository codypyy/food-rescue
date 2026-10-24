from datetime import timedelta

from django.utils import timezone

from inventory.models import FoodItem


def get_near_expiry_items():
    today = timezone.localdate()
    end_date = today + timedelta(days=3)

    return FoodItem.objects.filter(
        expiry_date__range=(
            today, end_date
        )
    )
