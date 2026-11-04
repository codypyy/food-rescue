from datetime import timedelta

from django.db import models
from django.utils import timezone

from inventory.constants import NEAR_EXPIRY_DAYS


class FoodItemQuerySet(models.QuerySet):
    
    def available(self):
        return self.filter(
            status="available"
        )

    def near_expiry(self):
        today = timezone.localdate()
        end_date = today + timedelta(
            days=NEAR_EXPIRY_DAYS
        )

        return self.filter(
            expiry_date__range=(today, end_date)
        )

# FoodItem.objects.filter(status='available')
# FoodItem.objects.available()