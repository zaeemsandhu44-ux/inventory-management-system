class inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product_item):
        self.products.append(product_item)
        return product_item

    def find_product(self, product_id):
        for item in self.products:
            if item.product_id == product_id:
                return item
        return None

    def remove_product(self, product_id):
        item = self.find_product(product_id)
        if item is None:
            return False
        self.products.remove(item)
        return True

    def get_low_stock_items(self, minimum_stock):
        return [item for item in self.products if item.quantity <= minimum_stock]

    def total_inventory_value(self):
        return sum(item.quantity * item.price for item in self.products)

    def search_by_id(self, product_id):
        item = self.find_product(product_id)
        if item is None:
            return "Product not found"
        return f"Found: {item.name} | ID: {item.product_id} | Qty: {item.quantity} | Price: {item.price}"

    def display_products(self):
        if not self.products:
            print("No products in inventory.")
            return

        print("\nInventory List:")
        for item in self.products:
            print(f"{item.name} | ID: {item.product_id} | Qty: {item.quantity} | Price: {item.price}")
