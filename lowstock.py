class lowstock:
    def __init__(self, product_item, quantity, minimumstock):
        self.product = product_item
        self.quantity = quantity
        self.minimumstock = minimumstock

    def is_low_stock(self):
        return self.quantity <= self.minimumstock

    def __str__(self):
        return f"Low stock alert: {self.product.product_id} has {self.quantity} units left (minimum: {self.minimumstock})"