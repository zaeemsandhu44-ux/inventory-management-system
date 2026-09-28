import unittest
from unittest.mock import Mock

from database import Database


class DatabaseTransactionTests(unittest.TestCase):
    def setUp(self):
        self.database = Database.__new__(Database)
        self.connection = Mock()
        self.cursor = Mock()
        self.connection.cursor.return_value = self.cursor
        self.database._connection = Mock(return_value=self.connection)

    def test_successful_operation_commits_and_closes_resources(self):
        result = self.database.transaction(lambda cursor: "saved")

        self.assertEqual(result, "saved")
        self.connection.start_transaction.assert_called_once_with()
        self.connection.commit.assert_called_once_with()
        self.connection.rollback.assert_not_called()
        self.cursor.close.assert_called_once_with()
        self.connection.close.assert_called_once_with()

    def test_failed_operation_rolls_back_and_propagates(self):
        def fail(_cursor):
            raise ValueError("invalid operation")

        with self.assertRaisesRegex(ValueError, "invalid operation"):
            self.database.transaction(fail)

        self.connection.start_transaction.assert_called_once_with()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_called_once_with()
        self.cursor.close.assert_called_once_with()
        self.connection.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()