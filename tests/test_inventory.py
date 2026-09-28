import unittest
from unittest.mock import Mock

from inventory import inventory
from product import product


class InventoryTransactionTests(unittest.TestCase):
    def setUp(self):
        self.database = Mock()
        self.service = inventory(self.database)

    def test_add_product_records_opening_stock(self):
        cursor = Mock()
        self.database.transaction.side_effect = lambda operation: operation(cursor)
        item = product("Widget", 12, 6, 2.50, "Tools")

        self.assertIs(self.service.add_product(item), item)

        self.assertEqual(cursor.execute.call_count, 2)
        self.assertIn("INSERT INTO products", cursor.execute.call_args_list[0].args[0])
        self.assertIn("INSERT INTO stock_history", cursor.execute.call_args_list[1].args[0])
        self.assertEqual(cursor.execute.call_args_list[1].args[1], (12, 12, 6))

    def test_add_stock_updates_quantity_and_records_history(self):
        cursor = Mock()
        cursor.fetchone.return_value = {"id": 12}
        self.database.transaction.side_effect = lambda operation: operation(cursor)

        self.assertTrue(self.service.add_stock(12, 4))

        self.assertEqual(cursor.execute.call_count, 3)
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertIn("UPDATE products SET quantity = quantity + %s", statements[1])
        self.assertIn("INSERT INTO stock_history", statements[2])
        self.assertEqual(cursor.execute.call_args_list[2].args[1], (12, 12, 4))

    def test_add_stock_missing_product_does_not_write_history(self):
        cursor = Mock()
        cursor.fetchone.return_value = None
        self.database.transaction.side_effect = lambda operation: operation(cursor)

        with self.assertRaisesRegex(LookupError, "Product not found"):
            self.service.add_stock(12, 4)

        self.assertEqual(cursor.execute.call_count, 1)

    def test_sale_checks_stock_deducts_and_records_total(self):
        cursor = Mock()
        cursor.fetchone.return_value = {
            "id": 12,
            "name": "Widget",
            "price": "2.50",
            "quantity": 9,
        }
        cursor.rowcount = 1
        self.database.transaction.side_effect = lambda operation: operation(cursor)

        self.assertEqual(self.service.sell_product(12, 3), 7.50)

        self.assertEqual(cursor.execute.call_count, 3)
        self.assertIn("FOR UPDATE", cursor.execute.call_args_list[0].args[0])
        self.assertIn("UPDATE products SET quantity = quantity - %s", cursor.execute.call_args_list[1].args[0])
        self.assertIn("INSERT INTO sales", cursor.execute.call_args_list[2].args[0])
        self.assertEqual(cursor.execute.call_args_list[2].args[1], (12, 12, "Widget", 3, 2.5, 7.5))

    def test_sale_rejects_insufficient_stock_before_writes(self):
        cursor = Mock()
        cursor.fetchone.return_value = {
            "id": 12,
            "name": "Widget",
            "price": "2.50",
            "quantity": 2,
        }
        self.database.transaction.side_effect = lambda operation: operation(cursor)

        with self.assertRaisesRegex(ValueError, "Insufficient stock"):
            self.service.sell_product(12, 3)

        self.assertEqual(cursor.execute.call_count, 1)

    def test_transaction_errors_propagate_for_rollback_by_database_layer(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            self.service.sell_product(12, 0)
        self.database.transaction.assert_not_called()


class ProductValidationTests(unittest.TestCase):
    def test_rejects_whitespace_name(self):
        with self.assertRaisesRegex(ValueError, "name cannot be empty"):
            product("  ", 1, 0, 1.0, "Food")

    def test_rejects_fractional_identifier_and_boolean_quantity(self):
        with self.assertRaisesRegex(ValueError, "Product ID"):
            product("Widget", 1.5, 1, 1.0, "Food")
        with self.assertRaisesRegex(ValueError, "Quantity"):
            product("Widget", 1, True, 1.0, "Food")

    def test_trims_fields_and_rejects_whitespace_category(self):
        item = product(" Widget ", "7", 2, "1.25", " Goods ")
        self.assertEqual((item.name, item.product_id, item.category), ("Widget", 7, "Goods"))
        with self.assertRaisesRegex(ValueError, "Category cannot be empty"):
            product("Widget", 7, 2, 1.25, "  ")


if __name__ == "__main__":
    unittest.main()