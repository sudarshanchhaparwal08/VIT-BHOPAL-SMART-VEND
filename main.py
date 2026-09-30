from data import VENDING_MACHINES, PRODUCTS, INVENTORY

from database import (
    create_tables,
    insert_initial_stock,
    load_stock_from_db,
    insert_initial_prices,
    get_machine_price,
    update_machine_price,
    get_machine_prices,
    get_all_machine_prices,
    save_order,
    update_stock,
    get_orders,
    get_order_items,
    get_database_stock,
    get_low_stock,
    get_total_revenue,
    get_total_orders,
    get_total_items_sold,
    get_machine_wise_sales
)

import math
import random
import sys
from datetime import datetime


# ---------------------------------------------------------
# TERMINAL ENCODING
# ---------------------------------------------------------

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError, OSError):
    pass


# ---------------------------------------------------------
# GLOBAL VARIABLES
# ---------------------------------------------------------

ORDER_HISTORY = []
ADMIN_PASSWORD = "admin123"


# ---------------------------------------------------------
# COMMON FUNCTIONS
# ---------------------------------------------------------

def show_header(title=None):
    print("\n" + "=" * 75)

    if title:
        print(f"{title:^75}")
    else:
        print(f"{'VIT BHOPAL SMART VEND':^75}")

    print("=" * 75)


def pause():
    input("\nPress Enter to continue...")


# ---------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------

def show_menu():
    show_header()

    print("1.  View All Vending Machines")
    print("2.  View Product Catalogue")
    print("3.  View Machine Inventory")
    print("4.  Search Product")
    print("5.  Find Nearest Machine")
    print("6.  Compare Product Prices")
    print("7.  View Hot Sellers")
    print("8.  View Unique Products")
    print("9.  Smart Budget Recommendation")
    print("10. Cart & Purchase")
    print("11. Order History")
    print("12. Admin Panel")
    print("13. Exit")

    print("=" * 75)


# ---------------------------------------------------------
# 1. VIEW ALL VENDING MACHINES
# ---------------------------------------------------------

def view_machines():
    show_header("ALL VENDING MACHINES")

    for machine_id, machine in VENDING_MACHINES.items():

        print(f"\nMachine ID : {machine_id}")
        print(f"Name       : {machine['name']}")
        print(f"Location   : {machine['location']}")
        print(f"Coordinates: ({machine['x']}, {machine['y']})")

        print("-" * 60)

    pause()


# ---------------------------------------------------------
# 2. VIEW PRODUCT CATALOGUE
# ---------------------------------------------------------

def view_products():
    show_header("PRODUCT CATALOGUE")

    print(
        f"{'ID':<8}"
        f"{'Product Name':<28}"
        f"{'Category':<20}"
        f"{'Base Price':>12}"
    )

    print("-" * 75)

    for product_id, product in PRODUCTS.items():

        print(
            f"{product_id:<8}"
            f"{product['name']:<28}"
            f"{product['category']:<20}"
            f"Rs.{product['price']:>8.2f}"
        )

    print("\n" + "=" * 75)
    print("MACHINE-SPECIFIC PRICES")
    print("=" * 75)

    print(
        "\nThe base price is shown above."
        "\nActual selling price can vary by vending machine."
    )

    for product_id, product in PRODUCTS.items():

        print("\n" + "-" * 75)

        print(
            f"{product_id} - {product['name']}"
        )

        print(
            f"Category: {product['category']}"
        )

        print("Machine Prices:")

        for machine_id, machine in VENDING_MACHINES.items():

            if product_id not in INVENTORY[machine_id]:
                continue

            try:
                price = get_machine_price(
                    machine_id,
                    product_id,
                    PRODUCTS
                )
            except Exception:
                price = product["price"]

            stock = INVENTORY[machine_id][product_id]["stock"]

            if stock > 0:
                status = "Available"
            else:
                status = "Out of Stock"

            print(
                f"  {machine_id:<6}"
                f"{machine['location']:<30}"
                f"Rs.{price:<8.2f}"
                f"{status}"
            )

    pause()


# ---------------------------------------------------------
# 3. VIEW MACHINE INVENTORY
# ---------------------------------------------------------

def view_machine_inventory():

    show_header("MACHINE INVENTORY")

    print("Available Vending Machines:\n")

    for machine_id, machine in VENDING_MACHINES.items():

        print(
            f"{machine_id} - "
            f"{machine['name']} - "
            f"{machine['location']}"
        )

    machine_id = input(
        "\nEnter Machine ID: "
    ).strip().upper()

    if machine_id not in INVENTORY:

        print("\nInvalid Machine ID.")
        pause()
        return

    print(
        f"\nInventory for "
        f"{VENDING_MACHINES[machine_id]['name']}"
    )

    print("-" * 80)

    print(
        f"{'Product ID':<12}"
        f"{'Product Name':<30}"
        f"{'Stock':>10}"
        f"{'Sold':>10}"
        f"{'Status':>15}"
    )

    print("-" * 80)

    for product_id, item in INVENTORY[machine_id].items():

        if item["stock"] == 0:
            status = "OUT OF STOCK"

        elif item["stock"] <= 5:
            status = "LOW STOCK"

        else:
            status = "AVAILABLE"

        product_name = PRODUCTS[product_id]["name"]

        print(
            f"{product_id:<12}"
            f"{product_name:<30}"
            f"{item['stock']:>10}"
            f"{item['sold']:>10}"
            f"{status:>15}"
        )

    pause()


# ---------------------------------------------------------
# 4. SEARCH PRODUCT
# ---------------------------------------------------------

def search_product():

    show_header("SEARCH PRODUCT")

    keyword = input(
        "Enter product name or category: "
    ).strip().lower()

    if not keyword:

        print("\nPlease enter a search term.")
        pause()
        return

    found = False

    for product_id, product in PRODUCTS.items():

        if (
            keyword in product["name"].lower()
            or keyword in product["category"].lower()
        ):

            found = True

            print("\n" + "=" * 75)

            print(
                f"{product['name']} "
                f"({product_id})"
            )

            print("=" * 75)

            print(
                f"Category   : {product['category']}"
            )

            print(
                f"Base Price : Rs.{product['price']:.2f}"
            )

            print("\nMachine-Specific Prices")
            print("-" * 75)

            print(
                f"{'Machine':<10}"
                f"{'Location':<30}"
                f"{'Price':<12}"
                f"{'Stock':<10}"
                f"{'Status':<15}"
            )

            print("-" * 75)

            machine_found = False

            for machine_id, machine in VENDING_MACHINES.items():

                if product_id not in INVENTORY[machine_id]:
                    continue

                machine_found = True

                try:

                    price = get_machine_price(
                        machine_id,
                        product_id,
                        PRODUCTS
                    )

                except Exception:

                    price = product["price"]

                stock = INVENTORY[machine_id][product_id]["stock"]

                if stock == 0:
                    status = "OUT OF STOCK"

                elif stock <= 5:
                    status = "LOW STOCK"

                else:
                    status = "AVAILABLE"

                print(
                    f"{machine_id:<10}"
                    f"{machine['location']:<30}"
                    f"Rs.{price:<8.2f}"
                    f"{stock:<10}"
                    f"{status:<15}"
                )

            if not machine_found:

                print(
                    "\nThis product is not available "
                    "in any vending machine."
                )

    if not found:

        print(
            "\nNo matching product found."
        )

    pause()


# ---------------------------------------------------------
# 5. FIND NEAREST MACHINE
# ---------------------------------------------------------

def find_nearest_machine():

    show_header("FIND NEAREST VENDING MACHINE")

    try:

        user_x = float(
            input("Enter your X coordinate: ")
        )

        user_y = float(
            input("Enter your Y coordinate: ")
        )

    except ValueError:

        print("\nInvalid coordinates.")
        pause()
        return

    nearest_machine = None
    shortest_distance = float("inf")

    for machine_id, machine in VENDING_MACHINES.items():

        distance = math.sqrt(
            (machine["x"] - user_x) ** 2
            + (machine["y"] - user_y) ** 2
        )

        if distance < shortest_distance:

            shortest_distance = distance
            nearest_machine = machine_id

    if nearest_machine:

        machine = VENDING_MACHINES[nearest_machine]

        distance_km = shortest_distance / 100

        print("\nNearest Vending Machine")
        print("-" * 50)

        print(
            f"Machine ID : {nearest_machine}"
        )

        print(
            f"Name       : {machine['name']}"
        )

        print(
            f"Location   : {machine['location']}"
        )

        print(
            f"Distance   : {distance_km:.2f} km"
        )

    pause()


# ---------------------------------------------------------
# 6. COMPARE PRODUCT PRICES
# ---------------------------------------------------------

def compare_prices():

    show_header("COMPARE PRODUCT PRICES")

    product_id = input(
        "Enter Product ID: "
    ).strip().upper()

    if product_id not in PRODUCTS:

        print("\nInvalid Product ID.")
        pause()
        return

    product_name = PRODUCTS[product_id]["name"]

    print(
        f"\nPrice comparison for: {product_name}"
    )

    print("-" * 80)

    prices = []

    for machine_id, machine in VENDING_MACHINES.items():

        if product_id not in INVENTORY[machine_id]:
            continue

        try:

            price = get_machine_price(
                machine_id,
                product_id,
                PRODUCTS
            )

        except Exception:

            price = PRODUCTS[product_id]["price"]

        stock = INVENTORY[machine_id][product_id]["stock"]

        print(
            f"{machine_id:<8}"
            f"{machine['location']:<30}"
            f"Rs.{price:<10.2f}"
            f"Stock: {stock}"
        )

        prices.append(
            (machine_id, price)
        )

    if prices:

        lowest = min(
            prices,
            key=lambda x: x[1]
        )

        highest = max(
            prices,
            key=lambda x: x[1]
        )

        difference = highest[1] - lowest[1]

        print("\n" + "-" * 80)

        print(
            f"Lowest Price : "
            f"Rs.{lowest[1]:.2f} "
            f"at {lowest[0]}"
        )

        print(
            f"Highest Price: "
            f"Rs.{highest[1]:.2f} "
            f"at {highest[0]}"
        )

        print(
            f"Difference   : "
            f"Rs.{difference:.2f}"
        )

    pause()


# ---------------------------------------------------------
# 7. HOT SELLERS
# ---------------------------------------------------------

def hot_sellers():

    show_header("HOT SELLERS")

    sales = []

    for machine_id, inventory in INVENTORY.items():

        for product_id, item in inventory.items():

            sales.append(
                (
                    product_id,
                    item["sold"]
                )
            )

    sales.sort(
        key=lambda x: x[1],
        reverse=True
    )

    unique_products_seen = set()

    print(
        f"{'Rank':<8}"
        f"{'Product':<30}"
        f"{'Category':<20}"
        f"{'Units Sold':>12}"
    )

    print("-" * 75)

    rank = 1

    for product_id, sold in sales:

        if product_id in unique_products_seen:
            continue

        unique_products_seen.add(product_id)

        product = PRODUCTS[product_id]

        print(
            f"{rank:<8}"
            f"{product['name']:<30}"
            f"{product['category']:<20}"
            f"{sold:>12}"
        )

        rank += 1

        if rank > 10:
            break

    pause()


# ---------------------------------------------------------
# 8. UNIQUE PRODUCTS
# ---------------------------------------------------------

def unique_products():

    show_header("UNIQUE / LIMITED PRODUCTS")

    found = False

    for machine_id, inventory in INVENTORY.items():

        for product_id, item in inventory.items():

            if item.get("unique", False):

                found = True

                product = PRODUCTS[product_id]
                machine = VENDING_MACHINES[machine_id]

                print("\n" + "-" * 65)

                print(
                    f"Machine     : {machine_id}"
                )

                print(
                    f"Location    : {machine['location']}"
                )

                print(
                    f"Product ID  : {product_id}"
                )

                print(
                    f"Product     : {product['name']}"
                )

                print(
                    f"Category    : {product['category']}"
                )

                print(
                    f"Base Price  : Rs.{product['price']}"
                )

                print(
                    f"Stock       : {item['stock']}"
                )

    if not found:

        print("\nNo unique products found.")

    pause()


# ---------------------------------------------------------
# 9. SMART BUDGET RECOMMENDATION
# ---------------------------------------------------------

def smart_budget_recommendation():

    show_header("SMART BUDGET RECOMMENDATION")

    print("Available Vending Machines")
    print("-" * 75)

    for machine_id, machine in VENDING_MACHINES.items():

        print(
            f"{machine_id} - "
            f"{machine['name']} - "
            f"{machine['location']}"
        )

    machine_id = input(
        "\nEnter Machine ID: "
    ).strip().upper()

    if machine_id not in VENDING_MACHINES:

        print("\nInvalid Machine ID.")
        pause()
        return

    try:

        budget = float(
            input("\nEnter your budget in Rs.: ")
        )

    except ValueError:

        print("\nInvalid budget.")
        pause()
        return

    if budget <= 0:

        print(
            "\nBudget must be greater than zero."
        )

        pause()
        return

    available_products = []

    for product_id, item in INVENTORY[machine_id].items():

        stock = item["stock"]

        if stock <= 0:
            continue

        if product_id not in PRODUCTS:
            continue

        product = PRODUCTS[product_id]

        try:

            price = get_machine_price(
                machine_id,
                product_id,
                PRODUCTS
            )

        except Exception:

            price = product["price"]

        if price <= budget:

            available_products.append(
                {
                    "product_id": product_id,
                    "name": product["name"],
                    "category": product["category"],
                    "price": price,
                    "stock": stock
                }
            )

    available_products.sort(
        key=lambda x: x["price"]
    )

    machine = VENDING_MACHINES[machine_id]

    print("\n" + "=" * 75)
    print("BUDGET RECOMMENDATION")
    print("=" * 75)

    print(
        f"Machine : "
        f"{machine_id} - {machine['name']}"
    )

    print(
        f"Location: {machine['location']}"
    )

    print(
        f"Budget  : Rs.{budget:.2f}"
    )

    if not available_products:

        print(
            "\nNo products are available "
            "within your budget at this machine."
        )

        pause()
        return

    # SINGLE PRODUCT OPTIONS

    print("\n" + "=" * 75)
    print("SINGLE PRODUCT OPTIONS")
    print("=" * 75)

    print(
        f"{'Product':<30}"
        f"{'Price':<12}"
        f"{'Qty':<8}"
        f"{'Total':<12}"
        f"{'Remaining':<12}"
    )

    print("-" * 75)

    for item in available_products:

        price = item["price"]
        stock = item["stock"]

        quantity = min(
            stock,
            int(budget // price)
        )

        if quantity <= 0:
            continue

        total_cost = quantity * price
        remaining = budget - total_cost

        print(
            f"{item['name']:<30}"
            f"Rs.{price:<8.2f}"
            f"{quantity:<8}"
            f"Rs.{total_cost:<8.2f}"
            f"Rs.{remaining:<8.2f}"
        )

    # PRODUCT DETAILS

    print("\n" + "=" * 75)
    print("PRODUCT OPTIONS")
    print("=" * 75)

    for item in available_products:

        price = item["price"]

        max_quantity = min(
            item["stock"],
            int(budget // price)
        )

        total_cost = max_quantity * price
        remaining = budget - total_cost

        print(f"\n{item['name']}")

        print(
            f"Category       : "
            f"{item['category']}"
        )

        print(
            f"Price          : "
            f"Rs.{price:.2f}"
        )

        print(
            f"Available Stock: "
            f"{item['stock']}"
        )

        print(
            f"Maximum Qty    : "
            f"{max_quantity}"
        )

        print(
            f"Total Cost     : "
            f"Rs.{total_cost:.2f}"
        )

        print(
            f"Remaining      : "
            f"Rs.{remaining:.2f}"
        )

        print("-" * 60)

    # TWO PRODUCT COMBINATIONS

    print("\n" + "=" * 75)
    print("TWO-PRODUCT COMBINATIONS")
    print("=" * 75)

    combinations = []

    for i in range(len(available_products)):

        for j in range(
            i + 1,
            len(available_products)
        ):

            product1 = available_products[i]
            product2 = available_products[j]

            total = (
                product1["price"]
                + product2["price"]
            )

            if total <= budget:

                remaining = budget - total

                combinations.append(
                    {
                        "product1": product1,
                        "product2": product2,
                        "total": total,
                        "remaining": remaining
                    }
                )

    combinations.sort(
        key=lambda x: x["total"],
        reverse=True
    )

    if not combinations:

        print(
            "\nNo two-product combination "
            "is available within your budget."
        )

    else:

        for combination in combinations[:10]:

            product1 = combination["product1"]
            product2 = combination["product2"]

            total = combination["total"]
            remaining = combination["remaining"]

            print(
                f"\n{product1['name']} "
                f"(Rs.{product1['price']:.2f})"
            )

            print(
                f"+ {product2['name']} "
                f"(Rs.{product2['price']:.2f})"
            )

            print(
                f"Total Cost : "
                f"Rs.{total:.2f}"
            )

            print(
                f"Remaining  : "
                f"Rs.{remaining:.2f}"
            )

            print("-" * 60)

    # THREE PRODUCT COMBINATIONS

    print("\n" + "=" * 75)
    print("THREE-PRODUCT COMBINATIONS")
    print("=" * 75)

    three_combinations = []

    for i in range(len(available_products)):

        for j in range(
            i + 1,
            len(available_products)
        ):

            for k in range(
                j + 1,
                len(available_products)
            ):

                product1 = available_products[i]
                product2 = available_products[j]
                product3 = available_products[k]

                total = (
                    product1["price"]
                    + product2["price"]
                    + product3["price"]
                )

                if total <= budget:

                    remaining = budget - total

                    three_combinations.append(
                        {
                            "products": [
                                product1,
                                product2,
                                product3
                            ],
                            "total": total,
                            "remaining": remaining
                        }
                    )

    three_combinations.sort(
        key=lambda x: x["total"],
        reverse=True
    )

    if not three_combinations:

        print(
            "\nNo three-product combination "
            "is available within your budget."
        )

    else:

        for combination in three_combinations[:10]:

            products = combination["products"]

            total = combination["total"]
            remaining = combination["remaining"]

            product_names = " + ".join(
                [
                    f"{p['name']} "
                    f"(Rs.{p['price']:.2f})"
                    for p in products
                ]
            )

            print(f"\n{product_names}")

            print(
                f"Total Cost : "
                f"Rs.{total:.2f}"
            )

            print(
                f"Remaining  : "
                f"Rs.{remaining:.2f}"
            )

            print("-" * 60)

    print(
        "\nRecommendation is based on the "
        "selected machine's actual prices and stock."
    )

    pause()


# ---------------------------------------------------------
# 10. CART & PURCHASE
# ---------------------------------------------------------

def cart_and_purchase():

    cart = []

    while True:

        show_header("CART & PURCHASE")

        print("1. Add Product to Cart")
        print("2. View Cart")
        print("3. Remove Product from Cart")
        print("4. Checkout")
        print("5. Back")

        choice = input(
            "\nEnter choice: "
        ).strip()

        # ADD PRODUCT

        if choice == "1":

            machine_id = input(
                "Enter Machine ID: "
            ).strip().upper()

            if machine_id not in VENDING_MACHINES:

                print("\nInvalid Machine ID.")
                pause()
                continue

            product_id = input(
                "Enter Product ID: "
            ).strip().upper()

            if product_id not in PRODUCTS:

                print("\nInvalid Product ID.")
                pause()
                continue

            if product_id not in INVENTORY[machine_id]:

                print(
                    "\nThis product is not available "
                    "in the selected machine."
                )

                pause()
                continue

            stock = INVENTORY[machine_id][product_id]["stock"]

            if stock <= 0:

                print("\nProduct is out of stock.")
                pause()
                continue

            try:

                price = get_machine_price(
                    machine_id,
                    product_id,
                    PRODUCTS
                )

            except Exception:

                price = PRODUCTS[product_id]["price"]

            print("\nProduct Information")
            print("-" * 50)

            print(
                f"Product : "
                f"{PRODUCTS[product_id]['name']}"
            )

            print(
                f"Machine : "
                f"{VENDING_MACHINES[machine_id]['name']}"
            )

            print(
                f"Location: "
                f"{VENDING_MACHINES[machine_id]['location']}"
            )

            print(
                f"Price   : Rs.{price:.2f}"
            )

            print(
                f"Stock   : {stock}"
            )

            try:

                quantity = int(
                    input("\nEnter quantity: ")
                )

            except ValueError:

                print("\nInvalid quantity.")
                pause()
                continue

            if quantity <= 0:

                print(
                    "\nQuantity must be greater than zero."
                )

                pause()
                continue

            existing_quantity = 0

            for item in cart:

                if (
                    item["machine_id"] == machine_id
                    and item["product_id"] == product_id
                ):

                    existing_quantity += item["quantity"]

            if existing_quantity + quantity > stock:

                print(
                    f"\nOnly "
                    f"{stock - existing_quantity} "
                    f"more item(s) available."
                )

                pause()
                continue

            subtotal = price * quantity

            cart.append(
                {
                    "machine_id": machine_id,
                    "product_id": product_id,
                    "name": PRODUCTS[product_id]["name"],
                    "quantity": quantity,
                    "price": price,
                    "subtotal": subtotal
                }
            )

            print(
                "\nProduct added to cart successfully."
            )

            print(
                f"Price per item : Rs.{price:.2f}"
            )

            print(
                f"Quantity       : {quantity}"
            )

            print(
                f"Subtotal       : Rs.{subtotal:.2f}"
            )

            pause()

        # VIEW CART

        elif choice == "2":

            view_cart(cart)

        # REMOVE PRODUCT

        elif choice == "3":

            if not cart:

                print("\nCart is empty.")
                pause()
                continue

            view_cart(cart)

            try:

                index = int(
                    input(
                        "\nEnter cart item number to remove: "
                    )
                ) - 1

            except ValueError:

                print("\nInvalid input.")
                pause()
                continue

            if 0 <= index < len(cart):

                removed = cart.pop(index)

                print(
                    f"\nRemoved "
                    f"{removed['name']} "
                    f"from cart."
                )

            else:

                print(
                    "\nInvalid cart item number."
                )

            pause()

        # CHECKOUT

        elif choice == "4":

            if not cart:

                print("\nCart is empty.")
                pause()
                continue

            purchase_successful = process_purchase(cart)

            if purchase_successful:
                cart.clear()

            pause()

        # BACK

        elif choice == "5":

            break

        else:

            print(
                "\nInvalid choice. "
                "Please select 1-5."
            )

            pause()


# ---------------------------------------------------------
# VIEW CART
# ---------------------------------------------------------

def view_cart(cart):

    show_header("YOUR CART")

    if not cart:

        print("Cart is empty.")
        pause()
        return

    total = 0

    print(
        f"{'#':<5}"
        f"{'Product':<30}"
        f"{'Qty':<8}"
        f"{'Price':<12}"
        f"{'Subtotal':<12}"
    )

    print("-" * 75)

    for index, item in enumerate(
        cart,
        start=1
    ):

        print(
            f"{index:<5}"
            f"{item['name']:<30}"
            f"{item['quantity']:<8}"
            f"Rs.{item['price']:<9.2f}"
            f"Rs.{item['subtotal']:<10.2f}"
        )

        total += item["subtotal"]

    print("-" * 75)

    print(
        f"{'TOTAL':>55}: "
        f"Rs.{total:.2f}"
    )

    pause()


# ---------------------------------------------------------
# PROCESS PURCHASE
# ---------------------------------------------------------

def process_purchase(cart):

    show_header("CHECKOUT")

    if not cart:

        print("\nCart is empty.")
        return False

    machine_id = cart[0]["machine_id"]

    for item in cart:

        if item["machine_id"] != machine_id:

            print(
                "\nAll products in one order must "
                "be purchased from the same machine."
            )

            print(
                "Please create separate orders "
                "for different machines."
            )

            return False

    # Check stock before changing anything

    for item in cart:

        product_id = item["product_id"]

        current_stock = (
            INVENTORY[machine_id][product_id]["stock"]
        )

        if item["quantity"] > current_stock:

            print(
                f"\nNot enough stock for "
                f"{item['name']}."
            )

            print(
                f"Available stock: {current_stock}"
            )

            return False

    print("ORDER SUMMARY")
    print("-" * 80)

    print(
        f"{'Product':<30}"
        f"{'Machine':<12}"
        f"{'Qty':<8}"
        f"{'Price':<12}"
        f"{'Subtotal':<12}"
    )

    print("-" * 80)

    total = 0

    for item in cart:

        print(
            f"{item['name']:<30}"
            f"{item['machine_id']:<12}"
            f"{item['quantity']:<8}"
            f"Rs.{item['price']:<9.2f}"
            f"Rs.{item['subtotal']:<10.2f}"
        )

        total += item["subtotal"]

    print("-" * 80)

    print(
        f"{'TOTAL AMOUNT':>55}: "
        f"Rs.{total:.2f}"
    )

    print("\nPayment Methods")
    print("1. UPI")
    print("2. Cash")
    print("3. Card")

    payment_choice = input(
        "\nSelect payment method: "
    ).strip()

    payment_methods = {
        "1": "UPI",
        "2": "Cash",
        "3": "Card"
    }

    if payment_choice not in payment_methods:

        print("\nInvalid payment method.")
        return False

    payment_method = payment_methods[payment_choice]

    machine = VENDING_MACHINES[machine_id]

    order_id = (
        "ORD"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
        + str(
            random.randint(100, 999)
        )
    )

    order = {
        "order_id": order_id,
        "date_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "machine_id": machine_id,
        "location": machine["location"],
        "total": total,
        "payment_method": payment_method,
        "items": cart.copy()
    }

    # Update stock ONCE

    for item in cart:

        product_id = item["product_id"]
        quantity = item["quantity"]

        current_stock = (
            INVENTORY[machine_id][product_id]["stock"]
        )

        current_sold = (
            INVENTORY[machine_id][product_id]["sold"]
        )

        new_stock = current_stock - quantity
        new_sold = current_sold + quantity

        INVENTORY[machine_id][product_id]["stock"] = new_stock
        INVENTORY[machine_id][product_id]["sold"] = new_sold

        update_stock(
            machine_id,
            product_id,
            new_stock,
            new_sold
        )

    # Save order ONCE

    save_order(order)

    ORDER_HISTORY.append(order)

    print("\n" + "=" * 75)
    print("PURCHASE SUCCESSFUL")
    print("=" * 75)

    print(
        f"Order ID     : {order_id}"
    )

    print(
        f"Machine      : {machine_id}"
    )

    print(
        f"Location     : {machine['location']}"
    )

    print(
        f"Payment      : {payment_method}"
    )

    print(
        f"Total Amount : Rs.{total:.2f}"
    )

    print("\nItems Purchased")
    print("-" * 60)

    for item in cart:

        print(
            f"{item['name']} "
            f"x {item['quantity']} "
            f"@ Rs.{item['price']:.2f} "
            f"= Rs.{item['subtotal']:.2f}"
        )

    print("-" * 60)

    print(
        f"TOTAL: Rs.{total:.2f}"
    )

    print(
        "\nMachine-specific price successfully "
        "applied to this purchase."
    )

    print(
        "\nThank you for using "
        "VIT Bhopal Smart Vend!"
    )

    return True


# ---------------------------------------------------------
# 11. ORDER HISTORY
# ---------------------------------------------------------

def order_history():

    show_header("ORDER HISTORY")

    orders = get_orders()

    if not orders:

        print("\nNo orders found.")
        pause()
        return

    for order in orders:

        (
            order_id,
            date_time,
            machine_id,
            location,
            total,
            payment_method
        ) = order

        print("\n" + "=" * 70)

        print(
            f"Order ID      : {order_id}"
        )

        print(
            f"Date & Time   : {date_time}"
        )

        print(
            f"Machine       : {machine_id}"
        )

        print(
            f"Location      : {location}"
        )

        print(
            f"Total         : Rs.{total:.2f}"
        )

        print(
            f"Payment       : {payment_method}"
        )

        print("\nItems:")

        items = get_order_items(order_id)

        for item in items:

            product_name, quantity, price, subtotal = item

            print(
                f"  {product_name} "
                f"x {quantity} "
                f"@ Rs.{price:.2f} "
                f"= Rs.{subtotal:.2f}"
            )

    pause()


# ---------------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------------

def admin_login():

    show_header("ADMIN LOGIN")

    password = input(
        "Enter admin password: "
    )

    if password == ADMIN_PASSWORD:

        print("\nLogin successful.")
        pause()

        admin_panel()

    else:

        print("\nIncorrect password.")
        pause()


# ---------------------------------------------------------
# ADMIN MACHINE PRICE MANAGEMENT
# ---------------------------------------------------------

def admin_manage_prices():

    while True:

        show_header("MANAGE MACHINE PRICES")

        print("1. View All Machine Prices")
        print("2. Change Product Price")
        print("3. View Machine Prices")
        print("4. Back to Admin Panel")

        choice = input(
            "\nEnter choice: "
        ).strip()

        if choice == "1":

            print("\n" + "=" * 90)
            print("ALL MACHINE-SPECIFIC PRICES")
            print("=" * 90)

            try:

                rows = get_all_machine_prices(
                    PRODUCTS
                )

                if not rows:

                    print(
                        "\nNo machine prices found."
                    )

                else:

                    print(
                        f"{'Machine':<10}"
                        f"{'Product ID':<12}"
                        f"{'Product Name':<30}"
                        f"{'Price':>12}"
                    )

                    print("-" * 90)

                    for row in rows:

                        if len(row) >= 4:

                            machine_id = row[0]
                            product_id = row[1]
                            product_name = row[2]
                            price = row[3]

                            print(
                                f"{machine_id:<10}"
                                f"{product_id:<12}"
                                f"{product_name:<30}"
                                f"Rs.{price:>8.2f}"
                            )

            except Exception as e:

                print(
                    "\nUnable to load prices."
                )

                print(
                    "Error:",
                    e
                )

            pause()

        elif choice == "2":

            print("\nAvailable Machines:")

            for machine_id, machine in VENDING_MACHINES.items():

                print(
                    f"{machine_id} - "
                    f"{machine['name']} - "
                    f"{machine['location']}"
                )

            machine_id = input(
                "\nEnter Machine ID: "
            ).strip().upper()

            if machine_id not in VENDING_MACHINES:

                print("\nInvalid Machine ID.")
                pause()
                continue

            product_id = input(
                "Enter Product ID: "
            ).strip().upper()

            if product_id not in PRODUCTS:

                print("\nInvalid Product ID.")
                pause()
                continue

            try:

                old_price = get_machine_price(
                    machine_id,
                    product_id,
                    PRODUCTS
                )

            except Exception:

                old_price = PRODUCTS[product_id]["price"]

            print(
                f"\nProduct: "
                f"{PRODUCTS[product_id]['name']}"
            )

            print(
                f"Current Price: "
                f"Rs.{old_price:.2f}"
            )

            try:

                new_price = float(
                    input(
                        "Enter new price: Rs."
                    )
                )

            except ValueError:

                print("\nInvalid price.")
                pause()
                continue

            if new_price <= 0:

                print(
                    "\nPrice must be greater than zero."
                )

                pause()
                continue

            try:

                update_machine_price(
                    machine_id,
                    product_id,
                    new_price
                )

                print(
                    f"\nPrice successfully changed "
                    f"from Rs.{old_price:.2f} "
                    f"to Rs.{new_price:.2f}"
                )

            except Exception as e:

                print(
                    "\nUnable to update price."
                )

                print(
                    "Error:",
                    e
                )

            pause()

        elif choice == "3":

            machine_id = input(
                "Enter Machine ID: "
            ).strip().upper()

            if machine_id not in VENDING_MACHINES:

                print("\nInvalid Machine ID.")
                pause()
                continue

            print(
                f"\nPrices at "
                f"{VENDING_MACHINES[machine_id]['name']}"
            )

            print("-" * 75)

            try:

                prices = get_machine_prices(
                    machine_id,
                    PRODUCTS
                )

                print(
                    f"{'Product ID':<12}"
                    f"{'Product Name':<30}"
                    f"{'Price':>15}"
                )

                print("-" * 75)

                for row in prices:

                    if len(row) >= 3:

                        product_id = row[0]
                        product_name = row[1]
                        price = row[2]

                        print(
                            f"{product_id:<12}"
                            f"{product_name:<30}"
                            f"Rs.{price:>10.2f}"
                        )

            except Exception as e:

                print(
                    "\nUnable to load machine prices."
                )

                print(
                    "Error:",
                    e
                )

            pause()

        elif choice == "4":

            break

        else:

            print("\nInvalid choice.")
            pause()


# ---------------------------------------------------------
# ADMIN VIEW INVENTORY
# ---------------------------------------------------------

def admin_view_inventory():

    show_header("ADMIN INVENTORY")

    for machine_id, machine in VENDING_MACHINES.items():

        print("\n" + "=" * 70)

        print(
            f"{machine_id} - "
            f"{machine['name']} - "
            f"{machine['location']}"
        )

        print("=" * 70)

        for product_id, item in INVENTORY[machine_id].items():

            product_name = PRODUCTS[product_id]["name"]

            print(
                f"{product_id:<8}"
                f"{product_name:<30}"
                f"Stock: {item['stock']:<5}"
                f"Sold: {item['sold']}"
            )

    pause()


# ---------------------------------------------------------
# ADMIN ADD STOCK
# ---------------------------------------------------------

def add_stock():

    show_header("ADD STOCK")

    machine_id = input(
        "Enter Machine ID: "
    ).strip().upper()

    if machine_id not in INVENTORY:

        print("\nInvalid Machine ID.")
        pause()
        return

    product_id = input(
        "Enter Product ID: "
    ).strip().upper()

    if product_id not in INVENTORY[machine_id]:

        print(
            "\nProduct not available "
            "in this machine."
        )

        pause()
        return

    try:

        quantity = int(
            input("Enter quantity to add: ")
        )

    except ValueError:

        print("\nInvalid quantity.")
        pause()
        return

    if quantity <= 0:

        print(
            "\nQuantity must be greater than zero."
        )

        pause()
        return

    item = INVENTORY[machine_id][product_id]

    item["stock"] += quantity

    update_stock(
        machine_id,
        product_id,
        item["stock"],
        item["sold"]
    )

    print(
        f"\nAdded {quantity} units successfully."
    )

    print(
        f"New stock: {item['stock']}"
    )

    pause()


# ---------------------------------------------------------
# ADMIN REMOVE STOCK
# ---------------------------------------------------------

def remove_stock():

    show_header("REMOVE STOCK")

    machine_id = input(
        "Enter Machine ID: "
    ).strip().upper()

    if machine_id not in INVENTORY:

        print("\nInvalid Machine ID.")
        pause()
        return

    product_id = input(
        "Enter Product ID: "
    ).strip().upper()

    if product_id not in INVENTORY[machine_id]:

        print(
            "\nProduct not available "
            "in this machine."
        )

        pause()
        return

    try:

        quantity = int(
            input("Enter quantity to remove: ")
        )

    except ValueError:

        print("\nInvalid quantity.")
        pause()
        return

    if quantity <= 0:

        print(
            "\nQuantity must be greater than zero."
        )

        pause()
        return

    item = INVENTORY[machine_id][product_id]

    if quantity > item["stock"]:

        print(
            f"\nCannot remove {quantity} units."
        )

        print(
            f"Current stock: {item['stock']}"
        )

        pause()
        return

    item["stock"] -= quantity

    update_stock(
        machine_id,
        product_id,
        item["stock"],
        item["sold"]
    )

    print(
        f"\nRemoved {quantity} units successfully."
    )

    print(
        f"New stock: {item['stock']}"
    )

    pause()


# ---------------------------------------------------------
# DATABASE STOCK REPORT
# ---------------------------------------------------------

def admin_database_stock():

    show_header("DATABASE STOCK REPORT")

    rows = get_database_stock()

    if not rows:

        print(
            "\nNo database stock records found."
        )

        pause()
        return

    print(
        f"{'Machine':<10}"
        f"{'Product':<12}"
        f"{'Product Name':<30}"
        f"{'Stock':>10}"
        f"{'Sold':>10}"
    )

    print("-" * 80)

    for row in rows:

        machine_id, product_id, stock, sold = row

        product_name = PRODUCTS.get(
            product_id,
            {}
        ).get(
            "name",
            "Unknown"
        )

        print(
            f"{machine_id:<10}"
            f"{product_id:<12}"
            f"{product_name:<30}"
            f"{stock:>10}"
            f"{sold:>10}"
        )

    pause()


# ---------------------------------------------------------
# LOW STOCK REPORT
# ---------------------------------------------------------

def admin_low_stock_report():

    show_header("LOW STOCK REPORT")

    try:

        threshold = int(
            input(
                "Enter low-stock threshold "
                "(default 5): "
            )
            or "5"
        )

    except ValueError:

        print("\nInvalid threshold.")
        pause()
        return

    if threshold < 0:

        print(
            "\nThreshold cannot be negative."
        )

        pause()
        return

    rows = get_low_stock(threshold)

    if not rows:

        print(
            f"\nNo products have "
            f"stock <= {threshold}."
        )

        pause()
        return

    print(
        f"\nProducts with stock <= {threshold}"
    )

    print("-" * 75)

    print(
        f"{'Machine':<10}"
        f"{'Product':<12}"
        f"{'Product Name':<30}"
        f"{'Stock':>10}"
        f"{'Sold':>10}"
    )

    print("-" * 75)

    for row in rows:

        machine_id, product_id, stock, sold = row

        product_name = PRODUCTS.get(
            product_id,
            {}
        ).get(
            "name",
            "Unknown"
        )

        print(
            f"{machine_id:<10}"
            f"{product_id:<12}"
            f"{product_name:<30}"
            f"{stock:>10}"
            f"{sold:>10}"
        )

    pause()


# ---------------------------------------------------------
# SALES REPORT
# ---------------------------------------------------------

def admin_sales_report():

    show_header("SALES REPORT")

    revenue = get_total_revenue()
    total_orders = get_total_orders()
    total_items = get_total_items_sold()

    print("\n" + "=" * 60)

    print(
        f"Total Revenue      : "
        f"Rs.{revenue:.2f}"
    )

    print(
        f"Total Orders       : "
        f"{total_orders}"
    )

    print(
        f"Total Items Sold   : "
        f"{total_items}"
    )

    if total_orders > 0:

        average_order = revenue / total_orders

        print(
            f"Average Order Value: "
            f"Rs.{average_order:.2f}"
        )

    else:

        print(
            "Average Order Value: Rs.0.00"
        )

    print("=" * 60)

    pause()


# ---------------------------------------------------------
# MACHINE-WISE SALES
# ---------------------------------------------------------

def admin_machine_wise_sales():

    show_header("MACHINE-WISE SALES")

    rows = get_machine_wise_sales()

    if not rows:

        print(
            "\nNo sales data available."
        )

        pause()
        return

    print(
        f"{'Machine':<12}"
        f"{'Location':<30}"
        f"{'Orders':>12}"
        f"{'Revenue':>15}"
    )

    print("-" * 75)

    for row in rows:

        machine_id, location, orders, revenue = row

        revenue = revenue or 0

        print(
            f"{machine_id:<12}"
            f"{location:<30}"
            f"{orders:>12}"
            f"Rs.{revenue:>11.2f}"
        )

    pause()


# ---------------------------------------------------------
# DATABASE ORDERS
# ---------------------------------------------------------

def admin_database_orders():

    show_header("DATABASE ORDERS")

    orders = get_orders()

    if not orders:

        print("\nNo orders found.")
        pause()
        return

    for order in orders:

        (
            order_id,
            date_time,
            machine_id,
            location,
            total,
            payment_method
        ) = order

        print("\n" + "-" * 70)

        print(
            f"Order ID    : {order_id}"
        )

        print(
            f"Date        : {date_time}"
        )

        print(
            f"Machine     : {machine_id}"
        )

        print(
            f"Location    : {location}"
        )

        print(
            f"Total       : Rs.{total:.2f}"
        )

        print(
            f"Payment     : {payment_method}"
        )

        print("\nItems:")

        items = get_order_items(order_id)

        for item in items:

            product_name, quantity, price, subtotal = item

            print(
                f"  {product_name} "
                f"x {quantity} "
                f"@ Rs.{price:.2f} "
                f"= Rs.{subtotal:.2f}"
            )

    pause()


# ---------------------------------------------------------
# ADMIN PANEL
# ---------------------------------------------------------

def admin_panel():

    while True:

        show_header("ADMIN PANEL")

        print("1. View Inventory")
        print("2. Add Stock")
        print("3. Remove Stock")
        print("4. Low Stock Report")
        print("5. Sales Report")
        print("6. Machine-Wise Sales")
        print("7. Database Stock Report")
        print("8. View Database Orders")
        print("9. Manage Machine Prices")
        print("10. Exit Admin Panel")

        choice = input(
            "\nEnter admin choice: "
        ).strip()

        if choice == "1":

            admin_view_inventory()

        elif choice == "2":

            add_stock()

        elif choice == "3":

            remove_stock()

        elif choice == "4":

            admin_low_stock_report()

        elif choice == "5":

            admin_sales_report()

        elif choice == "6":

            admin_machine_wise_sales()

        elif choice == "7":

            admin_database_stock()

        elif choice == "8":

            admin_database_orders()

        elif choice == "9":

            admin_manage_prices()

        elif choice == "10":

            break

        else:

            print(
                "\nInvalid choice."
            )

            pause()


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    while True:

        show_menu()

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            view_machines()

        elif choice == "2":

            view_products()

        elif choice == "3":

            view_machine_inventory()

        elif choice == "4":

            search_product()

        elif choice == "5":

            find_nearest_machine()

        elif choice == "6":

            compare_prices()

        elif choice == "7":

            hot_sellers()

        elif choice == "8":

            unique_products()

        elif choice == "9":

            smart_budget_recommendation()

        elif choice == "10":

            cart_and_purchase()

        elif choice == "11":

            order_history()

        elif choice == "12":

            admin_login()

        elif choice == "13":

            show_header("THANK YOU")

            print(
                "\nThank you for using "
                "VIT Bhopal Smart Vend!"
            )

            print(
                "\nProgram closed successfully."
            )

            break

        else:

            print(
                "\nInvalid choice. "
                "Please enter a number from 1 to 13."
            )

            pause()


# ---------------------------------------------------------
# PROGRAM START
# ---------------------------------------------------------

if __name__ == "__main__":

    create_tables()

    insert_initial_stock()

    insert_initial_prices(PRODUCTS)

    load_stock_from_db()

    main()