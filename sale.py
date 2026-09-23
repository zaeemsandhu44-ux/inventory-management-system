class sale:
    def __init__(self, product, quantity_sold):
        self.product = product
        self.quantity_sold = quantity_sold

        if quantity_sold <= 0:
            raise ValueError("Quantity sold must be greater than zero.")

        if quantity_sold > product.quantity:
            raise ValueError("Not enough stock available for sale.")

        product.quantity -= quantity_sold
        self.total_price = quantity_sold * product.price

    def __str__(self):
        return f"Sale for {self.product.product_id}: {self.quantity_sold} units, total = {self.total_price}"