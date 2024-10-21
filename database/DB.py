"""
Module for managing database connections and operations for a restaurant management system.

This module defines the DB class, which establishes a connection to a MariaDB database and
creates the necessary tables for managing restaurant orders, products, users, and JSON Web Tokens (JWTs).
"""
import mariadb

from database.repositorys import *


class DB:
    """Database connection and management class for a restaurant management system.

        This class handles the connection to a MariaDB database and the creation of necessary
        tables for storing data related to restaurant orders, products, users, and JWTs.

        Attributes:
            conn (mariadb.Connection): The connection to the MariaDB database.
            db_name (str): The name of the database to be created or used.

        Methods:
            __create_tables(): Creates necessary tables for the restaurant management system
                               if they do not already exist.

        Properties:
            restaurant_order_repository: Provides access to the RestaurantOrder repository.
            user_repository: Provides access to the User repository.
            product_repository: Provides access to the Product repository.
            product_per_kg_repository: Provides access to the ProductPerKg repository.
            order_status_history_repository: Provides access to the OrderStatusHistory repository.
            order_item_repository: Provides access to the OrderItem repository.
            jwt_list_repository: Provides access to the JWTList repository.
            kg_price_repository: Provides access to the KgPrice repository.
    """
    def __init__(self, host_ip: str, port: int, user: str, password: str, db_name: str):
        self.conn = mariadb.connect(host=host_ip, port=port, user=user, password=password)
        self.db_name = db_name
        self.__create_tables()

    def __create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name};")
        self.conn.database = self.db_name
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `RestaurantOrder` (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Number INT NOT NULL,
            Entry_Time DATETIME NOT NULL,
            Exit_Time DATETIME DEFAULT NULL,
            Status ENUM('Open', 'Closed', 'Cancelled') DEFAULT 'Open',
            Note TEXT,
            Payment_Method ENUM('Cash', 'Card', 'Pix', 'Others') DEFAULT NULL,
            Total_Amount DECIMAL(10, 2) DEFAULT 0.00,
            Paid BOOLEAN DEFAULT FALSE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderStatusHistory (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            RestaurantOrder_ID INT NOT NULL,
            Status ENUM('Open', 'Closed', 'Cancelled') NOT NULL,
            Change_Time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            FOREIGN KEY (RestaurantOrder_ID) REFERENCES `RestaurantOrder`(ID)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Description TEXT,
            Price DECIMAL(10, 2) NOT NULL,
            Category VARCHAR(255),
            Stock INT NOT NULL,
            Active BOOLEAN DEFAULT TRUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProductPerKg (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Description TEXT,
            Weight DECIMAL(10, 2) NOT NULL,
            PricePerKg DECIMAL(10, 2) NOT NULL,
            Total DECIMAL(10, 2) GENERATED ALWAYS AS (Weight * PricePerKg) STORED,
            Category VARCHAR(255)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS KgPrice (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Price DECIMAL(10, 2) NOT NULL,
            Category VARCHAR(255) NOT NULL
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderItem (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            RestaurantOrderID INT,
            ProductID INT,
            ProductPerKgID INT,
            Quantity INT DEFAULT 1,
            FOREIGN KEY (RestaurantOrderID) REFERENCES `RestaurantOrder`(ID),
            FOREIGN KEY (ProductID) REFERENCES Product(ID),
            FOREIGN KEY (ProductPerKgID) REFERENCES ProductPerKg(ID),
            CHECK ((ProductID IS NOT NULL AND ProductPerKgID IS NULL) OR (ProductPerKgID IS NOT NULL AND ProductID IS NULL))
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `User` (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Username VARCHAR(255) NOT NULL UNIQUE,
            Email VARCHAR(255) NOT NULL UNIQUE,
            PasswordHash VARCHAR(255) NOT NULL,
            Role ENUM('Admin', 'Waiter', 'Cook', 'Cashier') DEFAULT 'Cashier',
            Active BOOLEAN DEFAULT TRUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS  JWTList (
            user_id INT NOT NULL PRIMARY KEY, 
            jti VARCHAR(2047) NOT NULL UNIQUE, 
            expires_at TIMESTAMP NOT NULL, 
            CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES User(ID)
        );""")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON User (Username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jti ON JWTList (jti);")
        self.conn.commit()
        cursor.close()

    @property
    def restaurant_order_repository(self):
        return RestaurantOrderRepository(self)

    @property
    def user_repository(self):
        return UserRepository(self)

    @property
    def product_repository(self):
        return ProductRepository(self)

    @property
    def product_per_kg_repository(self):
        return ProductPerKgRepository(self)

    @property
    def order_status_history_repository(self):
        return OrderStatusHistoryRepository(self)

    @property
    def order_item_repository(self):
        return OrderItemRepository(self)

    @property
    def jwt_list_repository(self):
        return JWTListRepository(self)

    @property
    def kg_price_repository(self):
        return KgPriceRepository(self)
