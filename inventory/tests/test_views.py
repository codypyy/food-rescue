from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from inventory.models import (
    Category,
    FoodLocation,
    FoodItem,
    Reservation,
)

User = get_user_model()

class FoodViewTests(TestCase):

    def test_food_list_page(self):
        url = reverse("food_list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )
        self.assertTemplateUsed(
            response,
            "food_list.html"
        )


class DashboardViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="volunteer",
            password="test-pass-123"
        )

    def test_dashboard_login_required(self):
        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(response.status_code, 302)

    def test_dashboard_login_required_check_redirect(self):
        response = self.client.get(
            reverse("dashboard")
        )

        self.assertRedirects(
            response,
            f"{settings.LOGIN_URL}?next="
            f"{reverse("dashboard")}",
            fetch_redirect_response=False
        )


class DashboardPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            username="manager",
            password="test-pass-123"
        )

        cls.volunteer = User.objects.create_user(
            username="volunteer",
            password="test-pass-123"
        )

        permission = Permission.objects.get(
            codename="view_food_reports",
            content_type__app_label="inventory",
            content_type__model="fooditem",
        )

        cls.manager.user_permissions.add(permission)

    def test_volunteer_gets_403(self):
        self.client.force_login(self.volunteer)

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_open_dashboard(self):
        self.client.force_login(self.manager)

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(response.status_code, 200)


class ReserveFoodViewTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager"
        )

        self.volunteer = User.objects.create_user(
            username="volunteer"
        )

        self.category = Category.objects.create(
            title="Bakery"
        )

        self.location = FoodLocation.objects.create(
            title="Main Kitchen"
        )

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

    def test_volunteer_can_reserve_available_food(self):
        self.client.force_login(self.volunteer)

        response = self.client.post(
            #"/reserve/1/"
            reverse(
                "reserve_food",
                kwargs={"pk": self.food.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

        self.food.refresh_from_db()

        self.assertEqual(
            self.food.status,
            FoodItem.Status.RESERVED
        )

        self.assertTrue(
            Reservation.objects.filter(
                food_item=self.food,
                volunteer=self.volunteer,
                status=Reservation.Status.ACTIVE
            ).exists()
        )

        self.assertEqual(
            Reservation.objects.count(),
            1
        )

    def test_get_request_does_not_reserve_food(self):
        self.client.force_login(self.volunteer)

        response = self.client.get(
            reverse(
                "reserve_food",
                kwargs={"pk": self.food.pk}
            )
        )

        self.assertIn(
            response.status_code,
            [302, 405]
        )

        self.food.refresh_from_db()

        self.assertEqual(
            self.food.status,
            FoodItem.Status.AVAILABLE
        )

        self.assertFalse(
            Reservation.objects.filter(
                food_item=self.food
            ).exists()
        )

    def test_food_cannot_be_reserved_twice(self):
        self.client.force_login(self.volunteer)

        url = reverse(
            "reserve_food",
            kwargs={"pk": self.food.pk}
        )

        self.client.post(url)
        self.client.post(url)

        self.food.refresh_from_db()

        self.assertEqual(
            self.food.status,
            FoodItem.Status.RESERVED
        )

        self.assertEqual(
            Reservation.objects.filter(
                food_item=self.food,
                status=Reservation.Status.ACTIVE
            ).count(),
            1
        )

    def test_anonymous_user_cannot_reserve(self):

        response = self.client.post(
            reverse(
                "reserve_food",
                kwargs={"pk": self.food.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Reservation.objects.filter(
                food_item=self.food
            ).exists()
        )
        