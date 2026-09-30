import sqlite3
from data import INVENTORY
DB_NAME = "smart_vend.db"
def connect_db():
    return sqlite3.connect(DB_NAME)
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        order_id TEXT PRIMARY KEY,
        date_time TEXT,
        machine_id TEXT,
        location TEXT,
        total REAL,
        payment_method TEXT)""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        subtotal REAL)""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock(
        machine_id TEXT,
        product_id TEXT,
        stock INTEGER,
        sold INTEGER,
        PRIMARY KEY(machine_id, product_id))""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS machine_prices(
        machine_id TEXT,
        product_id TEXT,
        price REAL,
        PRIMARY KEY(machine_id, product_id))""")
    conn.commit()
    conn.close()
def insert_initial_stock():
    conn = connect_db()
    cursor = conn.cursor()
    for machine_id, inventory in INVENTORY.items():
        for product_id, item in inventory.items():
            cursor.execute("""
            INSERT OR IGNORE INTO stock
            (machine_id, product_id, stock, sold)
            VALUES (?, ?, ?, ?)
            """, (
                machine_id,
                product_id,
                item["stock"],
                item["sold"]))
    conn.commit()
    conn.close()
def load_stock_from_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT machine_id, product_id, stock, sold
    FROM stock""")
    rows = cursor.fetchall()
    for machine_id, product_id, stock, sold in rows:
        if machine_id in INVENTORY:
            if product_id in INVENTORY[machine_id]:
                INVENTORY[machine_id][product_id]["stock"] = stock
                INVENTORY[machine_id][product_id]["sold"] = sold
    conn.close()
def insert_initial_prices(products):
    """
    Creates machine-specific prices.
    If a price already exists, it is not overwritten."""
    conn = connect_db()
    cursor = conn.cursor()
    for machine_id, inventory in INVENTORY.items():
        for product_id in inventory:
            if product_id in products:
                base_price = products[product_id]["price"]
                cursor.execute("""
                INSERT OR IGNORE INTO machine_prices
                (machine_id, product_id, price)
                VALUES (?, ?, ?)
                """, (
                    machine_id,
                    product_id,
                    base_price))
    conn.commit()
    conn.close()
def get_machine_price(machine_id, product_id, products):
    """
    Returns machine-specific price.
    If no machine-specific price exists,
    the original product price is returned."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT price
    FROM machine_prices
    WHERE machine_id = ?
    AND product_id = ?
    """, (
        machine_id,
        product_id))
    result = cursor.fetchone()
    conn.close()
    if result is not None:
        return result[0]
    return products[product_id]["price"]
def update_machine_price(machine_id, product_id, price):
    """
    Updates the price of a product at a specific machine.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO machine_prices
    (machine_id, product_id, price)
    VALUES (?, ?, ?)
    """, (
        machine_id,
        product_id,
        price))
    conn.commit()
    conn.close()
def get_machine_prices(machine_id, products):
    """
    Returns all products and their prices
    for one vending machine."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT product_id, price
    FROM machine_prices
    WHERE machine_id = ?
    ORDER BY product_id
    """, (machine_id,))
    rows = cursor.fetchall()
    conn.close()
    result = {}
    for product_id, price in rows:
        result[product_id] = price
    for product_id in products:
        if product_id not in result:
            result[product_id] = products[product_id]["price"]
    return result
def get_all_machine_prices():
    """
    Returns all machine-specific prices.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        machine_id,
        product_id,
        price
    FROM machine_prices
    ORDER BY machine_id, product_id""")
    rows = cursor.fetchall()
    conn.close()
    return rows
def save_order(order):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO orders
    (order_id, date_time, machine_id, location, total, payment_method)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        order["order_id"],
        order["date_time"],
        order["machine_id"],
        order["location"],
        order["total"],
        order["payment_method"]))
    for item in order["items"]:
        cursor.execute("""
        INSERT INTO order_items
        (order_id, product_name, quantity, price, subtotal)
        VALUES (?, ?, ?, ?, ?)
        """, (
            order["order_id"],
            item["name"],
            item["quantity"],
            item["price"],
            item["subtotal"]))
    conn.commit()
    conn.close()
def update_stock(machine_id, product_id, stock, sold):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE stock
    SET stock = ?,
        sold = ?
    WHERE machine_id = ?
    AND product_id = ?
    """, (
        stock,
        sold,
        machine_id,
        product_id))
    conn.commit()
    conn.close()
def get_orders():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        order_id,
        date_time,
        machine_id,
        location,
        total,
        payment_method
    FROM orders
    ORDER BY date_time DESC""")
    orders = cursor.fetchall()
    conn.close()
    return orders
def get_order_items(order_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        product_name,
        quantity,
        price,
        subtotal
    FROM order_items
    WHERE order_id = ?
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()
    return items
def get_database_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        machine_id,
        product_id,
        stock,
        sold
    FROM stock
    ORDER BY machine_id, product_id""")
    rows = cursor.fetchall()
    conn.close()
    return rows
def get_low_stock(threshold=5):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        machine_id,
        product_id,
        stock,
        sold
    FROM stock
    WHERE stock <= ?
    ORDER BY stock ASC
    """, (threshold,))
    rows = cursor.fetchall()
    conn.close()
    return rows
def get_total_revenue():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COALESCE(SUM(total), 0)
    FROM orders""")
    revenue = cursor.fetchone()[0]
    conn.close()
    return revenue
def get_total_orders():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COUNT(*)
    FROM orders""")
    total_orders = cursor.fetchone()[0]
    conn.close()
    return total_orders 
def get_total_items_sold():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COALESCE(SUM(quantity), 0)
    FROM order_items""")
    total_items = cursor.fetchone()[0]
    conn.close()
    return total_items
def get_machine_wise_sales():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        machine_id,
        location,
        COUNT(order_id) AS orders,
        SUM(total) AS revenue
    FROM orders
    GROUP BY machine_id, location
    ORDER BY revenue DESC""")
    rows = cursor.fetchall()
    conn.close()
    return rows