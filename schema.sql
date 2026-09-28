CREATE DATABASE IF NOT EXISTS product_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE product_inventory;

CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    category VARCHAR(100) NOT NULL,
    CONSTRAINT chk_products_price CHECK (price >= 0),
    CONSTRAINT chk_products_quantity CHECK (quantity >= 0)
);

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
);

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
);