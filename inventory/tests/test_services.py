
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from inventory.exceptions import FoodItemNotAvailableError
from inventory.models import (
    Category,
    FoodLocation,
    FoodItem,
    Reservation,
)
from inventory.services import reserve_food_item

User = get_user_model()


class ReservationServiceTestCase(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(username="manager")
        self.volunteer = User.objects.create_user(username="volunteer")
        self.category = Category.objects.create(title="Bakery")
        self.location = FoodLocation.objects.create(title="Kitchen")
        self.food = FoodItem.objects.create(
            title="Sandwich",
            category=self.category,
            location=self.location,
            quantity=10,
            unit=FoodItem.Units.PIECE,
            expiry_date=(
                timezone.localdate()
                + timedelta(days=2)
            ),
            created_by=self.manager,
        )

    def test_reserve_available_food(self):

        reservation = reserve_food_item(
            food_item_id=self.food.pk,
            volunteer=self.volunteer
        )

        self.food.refresh_from_db()

        self.assertEqual(
            reservation.status,
            Reservation.Status.ACTIVE
        )

        self.assertEqual(
            self.food.status,
            FoodItem.Status.RESERVED
        )

        self.assertEqual(
            Reservation.objects.count(),
            1
        )

    def test_donated_food_cannot_be_reserved(self):

        self.food.status = FoodItem.Status.DONATED
        self.food.save(update_fields=["status"])

        with self.assertRaises(FoodItemNotAvailableError):

            reserve_food_item(
                food_item_id=self.food.pk,
                volunteer=self.volunteer
            )

        self.assertFalse(
            Reservation.objects.filter(
                food_item=self.food
            ).exists()
        )