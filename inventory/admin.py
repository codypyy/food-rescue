from django.contrib import admin
from inventory.models import FoodItem, Reservation, Category, FoodLocation



admin.site.register(FoodItem)
admin.site.register(Reservation)
admin.site.register(FoodLocation)
admin.site.register(Category)
