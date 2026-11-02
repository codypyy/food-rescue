
from django.contrib import admin
from django.urls import path

from inventory.views import dashboard, reserve_food, food_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('food_list/', food_list, name="food_list"),
    path('reserver/<int:pk>/', reserve_food, name="reserve_food"),
    path('dashboard/', dashboard, name="dashboard"),
]
