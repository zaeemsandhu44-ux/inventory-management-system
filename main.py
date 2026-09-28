from inventory import inventory
from product import product


class main:
    def __init__(self):
        self.inventory = inventory()
        try:
            self.inventory.get_products()
        except Exception as exc:
            raise RuntimeError(f"Could not load products from MySQL: {exc}") from exc

    def add_product(self, name, product_id, quantity, price, category="Uncategorized"):
        item = product(name, product_id, quantity, price, category)
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
            print("2. Show Products")
            print("3. Search Product")
            print("4. Add Stock")
            print("5. Sell Product")
            print("6. Update Product")
            print("7. Delete Product")
            print("0. Exit")

            try:
                choice = input("Enter your choice: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if choice == "1":
                product_id = None
                try:
                    product_id = int(input("Enter product ID: ").strip())
                    name = input("Enter product name: ").strip()
                    price = float(input("Enter price: ").strip())
                    quantity = int(input("Enter quantity: ").strip())
                    category = input("Enter category: ").strip()

                    item = self.add_product(name, product_id, quantity, price, category)
                    print(f"Product added: {item}")
                except (ValueError, TypeError) as exc:
                    message = str(exc).lower()
                    if "already exists" in message:
                        print(f"Product already exists: {product_id}")
                    else:
                        print(f"Invalid product details: {exc}")
                except Exception as exc:
                    print(f"Could not add product: {exc}")

            elif choice == "2":
                try:
                    self.display_products()
                except (EOFError, KeyboardInterrupt):
                    print("\nSession ended.")
                    break
                except Exception as exc:
                    print(f"Unable to display products: {exc}")

            elif choice == "3":
                try:
                    product_id = int(input("Enter product ID to search: ").strip())
                    print(self.search_product(product_id))
                except ValueError as exc:
                    print(f"Invalid product ID: {exc}")
                except Exception as exc:
                    print(f"Unable to search product: {exc}")

            elif choice == "4":
                try:
                    product_id = int(input("Enter product ID: ").strip())
                    quantity = int(input("Enter quantity to add: ").strip())
                    self.inventory.add_stock(product_id, quantity)
                    print("Stock added successfully.")
                except (ValueError, LookupError) as exc:
                    print(exc)
                except Exception as exc:
                    print(f"Could not add stock: {exc}")

            elif choice == "5":
                try:
                    product_id = int(input("Enter product ID: ").strip())
                    quantity = int(input("Enter quantity to sell: ").strip())
                    total = self.inventory.sell_product(product_id, quantity)
                    print(f"Sale successful. Total: {total:.2f}")
                except (ValueError, LookupError) as exc:
                    print(exc)
                except Exception as exc:
                    print(f"Could not complete sale: {exc}")

            elif choice == "6":
                try:
                    product_id = int(input("Enter product ID to update: ").strip())
                    if self.inventory.find_product(product_id) is None:
                        print("Product not found.")
                        continue
                    name = input("Enter new name: ").strip()
                    price = float(input("Enter new price: ").strip())
                    category = input("Enter new category: ").strip()
                    self.inventory.update_product(product_id, name, price, category)
                    print("Product updated successfully.")
                except ValueError as exc:
                    print(f"Invalid product details: {exc}")
                except Exception as exc:
                    print(f"Could not update product: {exc}")

            elif choice == "7":
                try:
                    product_id = int(input("Enter product ID to delete: ").strip())
                    if self.inventory.remove_product(product_id):
                        print("Product deleted successfully.")
                    else:
                        print("Product not found.")
                except ValueError as exc:
                    print(f"Invalid product ID: {exc}")
                except Exception as exc:
                    print(f"Could not delete product: {exc}")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please choose again.")


if __name__ == "__main__":
    from gui import launch_gui

    launch_gui(main)


