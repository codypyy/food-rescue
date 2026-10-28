
from django.contrib import admin
from django.urls import path

from inventory.views import dashboard, reserve_food

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reserver/<int:pk>/', reserve_food),

]
