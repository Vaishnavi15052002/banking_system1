-- Drop and recreate database
DROP DATABASE IF EXISTS bankdb;
CREATE DATABASE bankdb;
USE bankdb;

-- Customers table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_number VARCHAR(20) UNIQUE,
    account_type ENUM('savings','current') DEFAULT 'savings',
    balance DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    type ENUM('deposit','withdraw','transfer_in','transfer_out'),
    amount DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- View: Active Customers
CREATE VIEW active_customers AS
SELECT * FROM customers WHERE is_active = 1;

-- Stored Procedure: Add New Customer
DELIMITER //
CREATE PROCEDURE AddCustomer (
    IN fname VARCHAR(50),
    IN lname VARCHAR(50),
    IN email VARCHAR(100),
    IN phone VARCHAR(15),
    IN acc_type ENUM('savings','current')
)
BEGIN
    INSERT INTO customers(first_name, last_name, email, phone)
    VALUES(fname, lname, email, phone);
    SET @cid = LAST_INSERT_ID();
    INSERT INTO accounts(customer_id, account_number, account_type, balance)
    VALUES(@cid, CONCAT('AC', @cid), acc_type, 0.00);
END //
DELIMITER ;
