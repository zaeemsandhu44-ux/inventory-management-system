from decimal import Decimal

from database import get_database
from product import product


class inventory:
    def __init__(self, database=None):
        self.database = database or get_database()

    def add_product(self, product_item):
        try:
            def add_product_transaction(cursor):
                cursor.execute(
                    "INSERT INTO products (id, name, price, quantity, category) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        product_item.product_id,
                        product_item.name,
                        product_item.price,
                        product_item.quantity,
                        product_item.category,
                    ),
                )
                if product_item.quantity > 0:
                    cursor.execute(
                        "INSERT INTO stock_history "
                        "(product_id, product_id_at_stock, quantity_added) "
                        "VALUES (%s, %s, %s)",
                        (
                            product_item.product_id,
                            product_item.product_id,
                            product_item.quantity,
                        ),
                    )

            self.database.transaction(add_product_transaction)
        except Exception as exc:
            if getattr(exc, "errno", None) == 1062:
                raise ValueError(
                    f"Product with ID '{product_item.product_id}' already exists."
                ) from exc
            raise
        return product_item

    def find_product(self, product_id):
        rows = self.database.execute(
            "SELECT id, name, price, quantity, category FROM products WHERE id = %s",
            (product_id,),
            fetch=True,
        )
        if not rows:
            return None
        return self._product_from_row(rows[0])

    def _product_from_row(self, row):
        return product(
            row["name"], row["id"], row["quantity"], row["price"], row["category"]
        )

    def get_products(self, search=""):
        search = str(search).strip()
        query = "SELECT id, name, price, quantity, category FROM products"
        parameters = ()
        if search:
            query += (
                " WHERE CAST(id AS CHAR) LIKE %s OR name LIKE %s OR category LIKE %s"
            )
            pattern = f"%{search}%"
            parameters = (pattern, pattern, pattern)
        rows = self.database.execute(query + " ORDER BY name", parameters, fetch=True)
        return [self._product_from_row(row) for row in rows]

    def remove_product(self, product_id):
        product_id = self._positive_integer(product_id, "Product ID")
        if self.find_product(product_id) is None:
            return False
        return self.database.execute(
            "DELETE FROM products WHERE id = %s", (product_id,)
        ) > 0

    def add_stock(self, product_id, quantity):
        product_id = self._positive_integer(product_id, "Product ID")
        quantity = self._positive_integer(quantity, "Quantity to add")

        def add_stock_transaction(cursor):
            cursor.execute(
                "SELECT id FROM products WHERE id = %s FOR UPDATE", (product_id,)
            )
            if cursor.fetchone() is None:
                raise LookupError("Product not found.")
            cursor.execute(
                "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                (quantity, product_id),
            )
            cursor.execute(
                "INSERT INTO stock_history "
                "(product_id, product_id_at_stock, quantity_added) "
                "VALUES (%s, %s, %s)",
                (product_id, product_id, quantity),
            )
            return True

        return self.database.transaction(add_stock_transaction)

    def sell_product(self, product_id, quantity):
        product_id = self._positive_integer(product_id, "Product ID")
        quantity = self._positive_integer(quantity, "Quantity to sell")

        def sell_product_transaction(cursor):
            cursor.execute(
                "SELECT id, name, price, quantity FROM products "
                "WHERE id = %s FOR UPDATE",
                (product_id,),
            )
            item = cursor.fetchone()
            if item is None:
                raise LookupError("Product not found.")
            if item["quantity"] < quantity:
                raise ValueError("Insufficient stock available.")

            price = Decimal(str(item["price"]))
            total = price * quantity
            cursor.execute(
                "UPDATE products SET quantity = quantity - %s "
                "WHERE id = %s AND quantity >= %s",
                (quantity, product_id, quantity),
            )
            if cursor.rowcount != 1:
                raise ValueError("Insufficient stock available.")
            cursor.execute(
                "INSERT INTO sales "
                "(product_id, product_id_at_sale, product_name, quantity, price, total_amount) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (product_id, product_id, item["name"], quantity, price, total),
            )
            return total

        return self.database.transaction(sell_product_transaction)

    def update_product(self, product_id, name, price, category):
        product_id = self._positive_integer(product_id, "Product ID")
        if self.find_product(product_id) is None:
            return False
        updated_product = product(name, product_id, 0, price, category)
        self.database.execute(
            "UPDATE products SET name = %s, price = %s, category = %s WHERE id = %s",
            (updated_product.name, updated_product.price, updated_product.category, product_id),
        )
        return True

    def get_low_stock_items(self, minimum_stock):
        minimum_stock = self._positive_integer(minimum_stock, "Minimum stock", allow_zero=True)
        rows = self.database.execute(
            "SELECT id, name, price, quantity, category FROM products WHERE quantity <= %s",
            (minimum_stock,),
            fetch=True,
        )
        return [self._product_from_row(row) for row in rows]

    def total_inventory_value(self):
        rows = self.database.execute(
            "SELECT COALESCE(SUM(quantity * price), 0) AS total FROM products",
            fetch=True,
        )
        return Decimal(str(rows[0]["total"]))

    def get_dashboard_stats(self, minimum_stock):
        minimum_stock = self._positive_integer(minimum_stock, "Minimum stock", allow_zero=True)
        rows = self.database.execute(
            "SELECT COUNT(*) AS total_products, "
            "COALESCE(SUM(quantity), 0) AS total_stock, "
            "COALESCE(SUM(CASE WHEN quantity <= %s THEN 1 ELSE 0 END), 0) "
            "AS low_stock_products, "
            "(SELECT COALESCE(SUM(total_amount), 0) FROM sales) AS total_sales "
            "FROM products",
            (minimum_stock,),
            fetch=True,
        )
        return rows[0]

    def get_sales_history(self):
        return self.database.execute(
            "SELECT sale_id, product_id_at_sale AS product_id, product_name, "
            "quantity, price, total_amount, sale_date "
            "FROM sales ORDER BY sale_date DESC, sale_id DESC",
            fetch=True,
        )

    def get_stock_history(self):
        return self.database.execute(
            "SELECT stock_id, product_id_at_stock AS product_id, quantity_added, "
            "stock_date FROM stock_history ORDER BY stock_date DESC, stock_id DESC",
            fetch=True,
        )

    @staticmethod
    def _positive_integer(value, field_name, allow_zero=False):
        if isinstance(value, bool):
            raise ValueError(f"{field_name} must be a whole number.")
        try:
            parsed = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{field_name} must be a whole number.") from exc
        if not isinstance(value, str) and value != parsed:
            raise ValueError(f"{field_name} must be a whole number.")
        minimum = 0 if allow_zero else 1
        if parsed < minimum:
            qualifier = "non-negative" if allow_zero else "greater than zero"
            raise ValueError(f"{field_name} must be {qualifier}.")
        return parsed

    def search_by_id(self, product_id):
        item = self.find_product(product_id)
        if item is None:
            return "Product not found."
        return f"Found: {item}"

    def display_products(self):
        products = self.get_products()
        if not products:
            print("No products in inventory.")
            return

        print("\nInventory List:")
        for item in products:
            print(item)
