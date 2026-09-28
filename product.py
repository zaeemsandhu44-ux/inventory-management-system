import math


class product:
    def __init__(self, name, product_id, quantity, price, category="Uncategorized"):
        if isinstance(product_id, bool):
            raise ValueError("Product ID must be a positive integer.")
        try:
            parsed_id = int(product_id)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Product ID must be a positive integer.") from exc
        if not isinstance(product_id, str) and product_id != parsed_id:
            raise ValueError("Product ID must be a positive integer.")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be a non-negative integer.")
        try:
            parsed_price = float(price)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Price must be a valid non-negative number.") from exc

        self.name = str(name).strip() if name is not None else ""
        self.product_id = parsed_id
        self.quantity = quantity
        self.price = parsed_price
        self.category = str(category).strip() if category is not None else ""

        if not self.name:
            raise ValueError("Product name cannot be empty.")
        if self.product_id <= 0:
            raise ValueError("Product ID must be a positive integer.")
        if not isinstance(self.quantity, int) or self.quantity < 0:
            raise ValueError("Quantity must be a non-negative integer.")
        if not math.isfinite(self.price) or self.price < 0:
            raise ValueError("Price must be a valid non-negative number.")
        if not self.category:
            raise ValueError("Category cannot be empty.")

    def __str__(self):
        return (
            f"{self.name} (ID: {self.product_id}) - {self.quantity} units, "
            f"{self.price:.2f} each, Category: {self.category}"
        )

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        return self.quantity

    def total_value(self):
        return self.quantity * self.price