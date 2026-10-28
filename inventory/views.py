import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.utils import timezone


from inventory.exceptions import InventoryError
from inventory.forms import FoodItemForm
from inventory.models import FoodItem, Reservation
from inventory.reports import get_category_report
from inventory.services import reserve_food_item, donate_reserved_food


logger = logging.getLogger(__name__)


@login_required
def reserve_food(request, pk):
    
    logger.info("reserved submitted")

    item = get_object_or_404(FoodItem, pk=pk)

    if request.method != "POST":
        logger.warning("reservation rejected")
        return redirect("food_detail", pk=item.pk)
    
    try:
        reserve_food_item(food_item_id=pk, volunteer=request.user)
    except InventoryError as exc:
        logger.error("reservation process failed")
        messages.error(request, str(exc))
    except ValidationError as exc:
        logger.exception("validation error for reservatin") 
        messages.error(request, exc.message)
    else:
        messages.success(request, "رزرو با موفقیت انجام شد.")

    return redirect("food_detail", pk=item.pk)


@login_required
def donate_food(request, pk):

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET"])

    try:
        donate_reserved_food(reservation_id=pk)
    except ValidationError as exc:
        messages.error(request, exc.message)
    else:
        messages.success(request, "تحویل با موفقیت انجام شد.")

    return redirect("reservation_list")


@login_required
@permission_required(
    "inventory.view_food_reports",
    raise_exception=True
)
def dashboard(request):
    category_report = get_category_report()

    return render(
        request,
        "dashboard.html",
        {"category_report": category_report}
    )


@login_required
@permission_required(
    "inventory.add_fooditem",
    raise_exception=True
)
def create_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST)

        if form.is_valid():
            food = form.save(commit=False)

            food.created_by = request.user
            food.status = FoodItem.Status.AVAILABLE

            food.save()

            messages.success(
                request,
                "ماده غذایی ثبت شد."
            )

            return redirect("food_list")
    else:
        form = FoodItemForm()

    return render(
        request,
        "food_form.html",
        {"form": form}
    )



@login_required
def update_food(request, pk):

    food = get_object_or_404(FoodItem, pk=pk)

    if request.method == "POST":
        form = FoodItemForm(
            request.POST,
            instance=food
        )

        if form.is_valid():
            form.save()
            return redirect("food_list")

    else:
        form = FoodItemForm(instance=food)

    return render(
        request,
        "foodrescue/food_form.html",
        {"form": form}
    )