# views tasks:

1- get requests
2- auth/perm
3- get input data
4- call service function
5- response redirect ...



# near expiry

expiry date < 3
expiry date <= 3

expiry date 2025-10-18 00:00:00 utc | 2025-10-18 00:03:30 tehran


# sample is near expiry
today = timezone.localdate()
end_date = today + timedelta(days=3)

FoodItem.objects.filter(
    expiry_date__gte=today,
    expiry_date__lte=end_date,
)

# challange python :(
foods = FoodItem.objects.all()
for food in foods:
    print(food.is_near_expiry)


# Transaction atomic

reservation = Reservation.objects.create(
    food_item=food_item,
    volunteer=volunteer,
    status=Reservation.Status.ACTIVE
)

food_item.status = FoodItem.Status.RESERVED
food_item.save(
    update_fields=["status"]
)

SQl
transaction

insert (food_item, volunteer, status) values("milk", "user1", "active");
update set status='reserverd';

rollback;



# N + 1 query
simple

Query: FoodItems
Query: Category of item 1
Query: Location of item 1
Query: Category of item 2
Query: Location of item 2

SELECT "inventory_fooditem"."id", "inventory_fooditem"."title", "inventory_fooditem"."description", "inventory_fooditem"."category_id", "inventory_fooditem"."location_id", "inventory_fooditem"."quantity", "inventory_fooditem"."unit", "inventory_fooditem"."expiry_date", "inventory_fooditem"."status", "inventory_fooditem"."created_by_id", "inventory_fooditem"."created_at", "inventory_fooditem"."updated_at"
FROM "inventory_fooditem"
ORDER BY "inventory_fooditem"."expiry_date" ASC


select related:


Query: FoodItems
       + Category
       + Location
       
SELECT "inventory_fooditem"."id", "inventory_fooditem"."title", "inventory_fooditem"."description", "inventory_fooditem"."category_id", "inventory_fooditem"."location_id", "inventory_fooditem"."quantity", "inventory_fooditem"."unit", "inventory_fooditem"."expiry_date", "inventory_fooditem"."status", "inventory_fooditem"."created_by_id", "inventory_fooditem"."created_at", "inventory_fooditem"."updated_at", "inventory_category"."id", "inventory_category"."title", "inventory_foodlocation"."id", "inventory_foodlocation"."title", "inventory_foodlocation"."description"
FROM "inventory_fooditem"
INNER JOIN "inventory_category" ON ("inventory_fooditem"."category_id" = "inventory_category"."id")
INNER JOIN "inventory_foodlocation" ON ("inventory_fooditem"."location_id" = "inventory_foodlocation"."id")
ORDER BY "inventory_fooditem"."expiry_date" ASC