from django.db.models import Count, Q

from inventory.models import FoodItem


def get_category_report():
    return (
        FoodItem.objects
        .values("category__title")
        .annotate(
            total = Count("id"),
            donated = Count("id", filter=Q(status=FoodItem.Status.DONATED))
        )
        .order_by("-total")
    )
