"""
Module for managing products sold per kilogram in a database using MariaDB.

This module contains the `ProductPerKgRepository` class, which provides
methods for performing CRUD operations on products sold by weight.
It supports inserting, updating, deleting, and retrieving product
details from the database, including paginated retrieval of products.
"""
import mariadb

from database import ProductPerKg


class ProductPerKgRepository:
    """
        A repository class for managing products sold per kilogram.

        Attributes:
            db: A database connection object.

        Methods:
            insert(product_per_kg: ProductPerKg) -> bool: Inserts a new product per kg into the database.
            select_by_id(product_per_kg_id: int) -> ProductPerKg | None: Retrieves a product per kg by its ID.
            select_all() -> Generator[ProductPerKg, None, None]: Yields all products per kg in the database.
            select_all_paged(limit: int, offset: int) -> Generator[ProductPerKg, None, None]:
                Yields products per kg with pagination.
            delete_by_id(product_per_kg_id: int) -> (bool, int): Deletes a product per kg by its ID.
            update(product_per_kg: ProductPerKg) -> bool: Updates an existing product per kg in the database.
    """
    def __init__(self, db):
        self.db = db

    def insert(self, product_per_kg: ProductPerKg) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `ProductPerKg` (Description, Weight, PricePerKg, Category)
                VALUES (?, ?, ?, ?)
            """, (product_per_kg.description, product_per_kg.weight,
                  product_per_kg.price_per_kg, product_per_kg.category))

            product_per_kg.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting product per kg: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, product_per_kg_id: int) -> ProductPerKg | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Description, Weight, PricePerKg, Category, Total
                FROM `ProductPerKg`
                WHERE ID = ?
            """, (product_per_kg_id,))
            row = cursor.fetchone()

            if row:
                return ProductPerKg(
                    id=row[0],
                    description=row[1],
                    weight=row[2],
                    price_per_kg=row[3],
                    category=row[4]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching product per kg by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_all(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Description, Weight, PricePerKg, Category, Total
                FROM `ProductPerKg`
            """)
            for row in cursor:
                yield ProductPerKg(
                    id=row[0],
                    description=row[1],
                    weight=row[2],
                    price_per_kg=row[3],
                    category=row[4]
                )
        except mariadb.Error as e:
            print(f"Error fetching all products per kg: {e}")
        finally:
            cursor.close()

    def select_all_paged(self, limit: int, offset: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Description, Weight, PricePerKg, Category, Total
                FROM `ProductPerKg` LIMIT ? OFFSET ?
            """, (limit, offset))
            for row in cursor:
                yield ProductPerKg(
                    id=row[0],
                    description=row[1],
                    weight=row[2],
                    price_per_kg=row[3],
                    category=row[4]
                )
        except mariadb.Error as e:
            print(f"Error fetching all products per kg: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, product_per_kg_id: int) -> (bool, int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `ProductPerKg` WHERE ID = ?", (product_per_kg_id,))
            self.db.conn.commit()
            return True, cursor.rowcount
        except mariadb.Error as e:
            print(f"Error deleting product per kg by ID: {e}")
            self.db.conn.rollback()
            return False, 0
        finally:
            cursor.close()

    def update(self, product_per_kg: ProductPerKg) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `ProductPerKg` SET Description = ?, Weight = ?, PricePerKg = ?, Category = ?
                WHERE ID = ?
            """, (product_per_kg.description, product_per_kg.weight,
                  product_per_kg.price_per_kg, product_per_kg.category, product_per_kg.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating product per kg: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()
