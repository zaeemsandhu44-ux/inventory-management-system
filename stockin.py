class stock:
    def __init__(self, product, new_quantity):
        self.product = product
        self.new_quantity = new_quantity

        if new_quantity <= 0:
            raise ValueError("Quantity added must be greater than zero.")

        product.quantity += new_quantity

    def __str__(self):
        return f"Stock added to {self.product.product_id}: {self.new_quantity} units"