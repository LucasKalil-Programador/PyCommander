"""
Module for managing product data access in a restaurant management system.

This module defines the `ProductRepository` class, which provides methods for
interacting with the `Product` table in the database. It includes functionalities
for inserting, updating, deleting, and retrieving product information.

Dependencies:
    mariadb: MariaDB connector for Python.
    database: Imports the Product class for product management.
"""
import mariadb

from database import Product


class ProductRepository:
    """
        A repository for managing Product records in a database.

        Methods:
            insert(product: Product) -> bool: Inserts a new product into the database.
            select_by_id(product_id: int) -> Product | None: Retrieves a product by its ID.
            select_all() -> Generator[Product]: Yields all products from the database.
            select_all_paged(limit: int, offset: int) -> Generator[Product]: Yields products with pagination support.
            delete_by_id(product_id: int) -> (bool, int): Deletes a product by its ID and returns success status and affected row count.
            update(product: Product) -> bool: Updates an existing product's details in the database.
            get_product_summary() -> tuple: Retrieves a summary of the products in the database,
                                      including the total value of products in stock
                                      and the total count of products.
    """
    def __init__(self, db):
        self.db = db

    def insert(self, product: Product) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `Product` (Name, Description, Price, Category, Stock, Active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product.name, product.description, product.price,
                  product.category, product.stock, product.active))

            product.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting product: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, product_id: int) -> Product | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Description, Price, Category, Stock, Active
                FROM `Product`
                WHERE ID = ?
            """, (product_id,))
            row = cursor.fetchone()

            if row:
                return Product(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    price=row[3],
                    category=row[4],
                    stock=row[5],
                    active=row[6]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching product by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_all(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Description, Price, Category, Stock, Active
                FROM `Product`
            """)
            for row in cursor:
                yield Product(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    price=row[3],
                    category=row[4],
                    stock=row[5],
                    active=row[6]
                )
        except mariadb.Error as e:
            print(f"Error fetching all products: {e}")
        finally:
            cursor.close()

    def select_all_paged(self, limit: int, offset: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Description, Price, Category, Stock, Active
                FROM `Product` LIMIT ? OFFSET ?
            """, (limit, offset))
            for row in cursor:
                yield Product(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    price=row[3],
                    category=row[4],
                    stock=row[5],
                    active=row[6]
                )
        except mariadb.Error as e:
            print(f"Error fetching all products: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, product_id: int) -> (bool, int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `Product` WHERE ID = ?", (product_id,))
            self.db.conn.commit()
            return True, cursor.rowcount
        except mariadb.Error as e:
            print(f"Error deleting product by ID: {e}")
            self.db.conn.rollback()
            return False, 0
        finally:
            cursor.close()

    def update(self, product: Product) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `Product` SET Name = ?, Description = ?, Price = ?, Category = ?, Stock = ?, Active = ?
                WHERE ID = ?
            """, (product.name, product.description, product.price,
                  product.category, product.stock, product.active, product.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating product: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def get_product_summary(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT SUM(Price * Stock), COUNT(*)
                FROM Product
            """)
            result = cursor.fetchone()
            if result:
                total_value = result[0] if result[0] is not None else 0
                total_count = result[1] if result[1] is not None else 0
                return total_value, total_count
            return 0, 0
        except mariadb.Error as e:
            print(f"Error fetching product summary: {e}")
        finally:
            cursor.close()