from inventory import inventory
from product import product


class main:
    def __init__(self):
        self.inventory = inventory()
        try:
            self.add_product("watch", "702", 10, 2500)
            self.add_product("phone", "101", 5, 1200)
        except ValueError:
            pass

    def add_product(self, name, product_id, quantity, price):
        item = product(name, product_id, quantity, price)
        self.inventory.add_product(item)
        return item

    def search_product(self, product_id):
        return self.inventory.search_by_id(product_id)

    def display_products(self):
        self.inventory.display_products()

    def run(self):
        while True:
            print("\nInventory Management System")
            print("1. Add Product")
            print("2. Search Product by ID")
            print("3. Display Products")
            print("0. Exit")

            try:
                choice = input("Enter your choice: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if choice == "1":
                try:
                    name = input("Enter product name: ").strip()
                    product_id = input("Enter product ID: ").strip()
                    quantity = int(input("Enter quantity: ").strip())
                    price = float(input("Enter price: ").strip())

                    item = self.add_product(name, product_id, quantity, price)
                    print(f"Product added: {item}")
                except (ValueError, TypeError):
                    print("Invalid input. Please enter valid product details.")

            elif choice == "2":
                try:
                    product_id = input("Enter product ID to search: ").strip()
                    print(self.search_product(product_id))
                except (EOFError, KeyboardInterrupt):
                    print("\nSession ended.")
                    break
                except Exception:
                    print("Unable to search product right now.")

            elif choice == "3":
                try:
                    self.display_products()
                except Exception:
                    print("Unable to display products.")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please choose again.")


