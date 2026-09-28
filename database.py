import os

try:
    import mysql.connector
    from mysql.connector import Error
except ModuleNotFoundError:
    mysql = None
    Error = ModuleNotFoundError

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "product_inventory")


class Database:
    def __init__(self):
        if mysql is None:
            raise RuntimeError(
                "MySQL Connector/Python is not installed. Run: "
                "pip install mysql-connector-python"
            )
        self.host = MYSQL_HOST
        self.port = MYSQL_PORT
        self.user = MYSQL_USER
        self.password = MYSQL_PASSWORD
        self.database = MYSQL_DATABASE
        self._initialize()

    def _server_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
        )

    def _connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def _initialize(self):
        if mysql is None:
            raise RuntimeError(
                "MySQL Connector/Python is not installed. Run: "
                "pip install -r requirements.txt"
            )
        connection = None
        cursor = None
        try:
            connection = self._server_connection()
            cursor = connection.cursor()
            database_name = self.database.replace("`", "``")
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.commit()
        except Error as exc:
            raise RuntimeError(
                "Could not connect to MySQL. Start MySQL in XAMPP and "
                "check the settings at the top of database.py."
            ) from exc
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        connection = None
        cursor = None
        try:
            connection = self._connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INT NOT NULL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(12, 2) NOT NULL,
                    quantity INT NOT NULL DEFAULT 0,
                    category VARCHAR(100) NOT NULL,
                    CONSTRAINT chk_products_price CHECK (price >= 0),
                    CONSTRAINT chk_products_quantity CHECK (quantity >= 0)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NULL,
                    product_id_at_sale INT NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(12, 2) NOT NULL,
                    total_amount DECIMAL(24, 2) NOT NULL,
                    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_sales_sale_date (sale_date),
                    CONSTRAINT fk_sales_product FOREIGN KEY (product_id)
                        REFERENCES products(id) ON DELETE SET NULL,
                    CONSTRAINT chk_sales_quantity CHECK (quantity > 0)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stock_history (
                    stock_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NULL,
                    product_id_at_stock INT NOT NULL,
                    quantity_added INT NOT NULL,
                    stock_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_stock_history_date (stock_date),
                    CONSTRAINT fk_stock_history_product FOREIGN KEY (product_id)
                        REFERENCES products(id) ON DELETE SET NULL,
                    CONSTRAINT chk_stock_history_quantity CHECK (quantity_added > 0)
                )
                """
            )
            connection.commit()
        except Error as exc:
            raise RuntimeError(f"Could not initialize the products table: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def execute(self, query, parameters=(), fetch=False):
        connection = None
        cursor = None
        try:
            connection = self._connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, parameters)
            if fetch:
                return cursor.fetchall()
            connection.commit()
            return cursor.rowcount
        except Error:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def transaction(self, operation):
        connection = None
        cursor = None
        try:
            connection = self._connection()
            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()
            result = operation(cursor)
            connection.commit()
            return result
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()


def get_connection():
    if mysql is None:
        raise RuntimeError(
            "MySQL Connector/Python is not installed. Run: "
            "pip install mysql-connector-python"
        )
    try:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
    except Error as exc:
        raise RuntimeError(
            "Could not connect to MySQL. Start MySQL in XAMPP and check "
            "the settings at the top of database.py."
        ) from exc


def get_database():
    return Database()