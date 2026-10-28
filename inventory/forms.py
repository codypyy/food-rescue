from django import forms

from inventory.models import FoodItem


class FoodItemForm(forms.ModelForm):
    class meta:
        model = FoodItem
        fields = [
            "title",
            "description",
            "category",
            "location",
            "quantity",
            "unit",
            "expiry_date"
        ]

