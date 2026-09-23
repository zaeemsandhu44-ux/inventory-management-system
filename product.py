class product:
    def __init__(self, name, product_id, quantity, price):
        self.name = name
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

        if not self.name:
            raise ValueError("Product name cannot be empty.")
        if not self.product_id:
            raise ValueError("Product ID cannot be empty.")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if self.price < 0:
            raise ValueError("Price cannot be negative.")

    def __str__(self):
        return f"{self.name} ({self.product_id}) - {self.quantity} units at {self.price} each"

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        return self.quantity

    def total_value(self):
        return self.quantity * self.price