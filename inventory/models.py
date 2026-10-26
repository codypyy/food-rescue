from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class FoodLocation(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FoodItem(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available" 
        RESERVED = "reserved", "Reserved"
        EXPIRED = "expired", "Expired"
        DONATED = "donated", "Donated"

    class Units(models.TextChoices):
        PIECE = "piece", "Piece" 
        KG = "kg", "KG"
        LITER = "liter", "Liter"

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="food_item"
    )

    location = models.ForeignKey(
        FoodLocation,
        on_delete=models.PROTECT,
        related_name="food_item"
    )

    quantity = models.PositiveIntegerField()
    unit = models.CharField(
        max_length=30,
        choices=Units.choices,
        default=Units.PIECE
    )
    expiry_date = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_food_item"
    ) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["expiry_date"]

        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="fooditem_quantity_gt_zero"
            )
        ]
        indexes = [
            models.Index(
                fields=["expiry_date", "quantity"],
                name="food_expiry_idx"
            ),
            models.Index(
                fields=["expiry_date", "status"],
                name="food_expiry_status_idx"
            )
        ]
        permissions = [
            ("view_food_reports", "Can view food reports"),
        ]

    @property
    def days_until_expiry(self):
        return (
            self.expiry_date - timezone.localdate()
        ).days

    @property
    def is_expired(self):
        return self.expiry_date < timezone.localdate()

    @property
    def is_near_expiry(self):
        days = self.days_until_expiry
        return 0 <= days <= 3

    def __str__(self):
        return f"{self.title}-{self.quantity}-{self.expiry_date}"


class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active" 
        CANCEL = "cancel", "Cancel"
        COMPLETED = "completed", "Completed"

    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=['volunteer', 'food_item'],
                condition=Q(status="active"),
                name='unique_active_reservation'
            )
        ]

    def __str__(self):
        return(
            f"{self.food_item.title} - "
            f"{self.volunteer} - "
            f"{self.get_status_display()}"
        )
