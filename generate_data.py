import sqlite3
import random
from datetime import date, timedelta

def main() -> None:
    db_path = "sales_data.db"

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")

        cur = conn.cursor()

        cur.executescript(
            """
            DROP TABLE IF EXISTS sales;
            DROP TABLE IF EXISTS products;

            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0)
            );

            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                sale_date TEXT NOT NULL,
                region TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE INDEX idx_sales_product_id ON sales(product_id);
            CREATE INDEX idx_sales_sale_date ON sales(sale_date);
            CREATE INDEX idx_sales_region ON sales(region);
            """
        )

        products = [
            ("Gaming Laptop", "Electronics", 1499.99),
            ("Mechanical Keyboard", "Electronics", 129.99),
            ("Wireless Mouse", "Electronics", 39.99),
            ("27-inch 4K Monitor", "Electronics", 329.99),
            ("Noise-Cancelling Headphones", "Electronics", 199.99),
            ("USB-C Docking Station", "Electronics", 119.99),
            ("Portable SSD 1TB", "Electronics", 99.99),
            ("Smartphone", "Electronics", 899.00),
            ("Fitness Smartwatch", "Electronics", 249.99),
            ("Wi-Fi Router", "Electronics", 89.99),
            ("Ergonomic Office Chair", "Furniture", 279.99),
            ("Standing Desk", "Furniture", 499.99),
            ("LED Desk Lamp", "Furniture", 34.99),
            ("Bookshelf", "Furniture", 159.99),
            ("Coffee Table", "Furniture", 129.99),
            ("Stainless Steel Water Bottle", "Accessories", 24.99),
            ("Backpack", "Accessories", 59.99),
            ("Phone Case", "Accessories", 19.99),
            ("Running Shoes", "Apparel", 89.99),
            ("Hoodie", "Apparel", 54.99),
        ]

        cur.executemany(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            products,
        )

        regions = ["North", "South", "East", "West", "Central"]

        random.seed(42)
        start_date = date.today() - timedelta(days=120)

        # Insert 50 sales rows referencing the 20 products above
        sales_rows = []
        for _ in range(50):
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 8)
            sale_dt = start_date + timedelta(days=random.randint(0, 120))
            region = random.choice(regions)
            sales_rows.append((product_id, quantity, sale_dt.isoformat(), region))

        cur.executemany(
            "INSERT INTO sales (product_id, quantity, sale_date, region) VALUES (?, ?, ?, ?)",
            sales_rows,
        )

        conn.commit()

        # Quick sanity check: total rows
        products_count = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        sales_count = cur.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        print(f"Created {db_path} with {products_count} products and {sales_count} sales rows.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
