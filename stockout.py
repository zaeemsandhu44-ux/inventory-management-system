class stockout:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

    def is_stockout(self):
        return self.quantity <= 0

    def restock(self, amount):
        if amount > 0:
            self.quantity += amount
            return True
        return False

    def __str__(self):
        return f"Stockout for {self.product_id}: {self.quantity} units remaining"