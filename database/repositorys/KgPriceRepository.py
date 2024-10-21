"""
kg_price_repository.py

This module provides the `KgPriceRepository` class for managing kg price records
in a MariaDB database. It offers methods to insert, select, update, delete,
and check the existence of kg price records.

Classes:
    KgPriceRepository: A repository for CRUD operations on KgPrice records.
"""
import mariadb

from database import KgPrice


class KgPriceRepository:
    """
        A repository for managing KgPrice records in a MariaDB database.

        Attributes:
            db: A database connection instance.

        Methods:
            insert(kg_price: KgPrice) -> bool: Inserts a new kg price into the database.
            select_by_id(kg_price_id: int) -> KgPrice | None: Retrieves a kg price by its ID.
            select_all(): Yields all kg prices from the database.
            select_all_paged(limit: int, offset: int): Yields kg prices with pagination.
            delete_by_id(kg_price_id: int) -> (bool, int): Deletes a kg price by its ID.
            update(kg_price: KgPrice) -> bool: Updates an existing kg price in the database.
            exists_by_id(kg_price_id: int) -> bool: Checks if a kg price exists by its ID.
    """
    def __init__(self, db):
        self.db = db

    def insert(self, kg_price: KgPrice) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `KgPrice` (Price, Category)
                VALUES (?, ?)
            """, (kg_price.price, kg_price.category))

            kg_price.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting kg price: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, kg_price_id: int) -> KgPrice | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Price, Category
                FROM `KgPrice`
                WHERE ID = ?
            """, (kg_price_id,))
            row = cursor.fetchone()

            if row:
                return KgPrice(
                    id=row[0],
                    price=row[1],
                    category=row[2]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching kg price by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_all(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Price, Category
                FROM `KgPrice`
            """)
            for row in cursor:
                yield KgPrice(
                    id=row[0],
                    price=row[1],
                    category=row[2]
                )
        except mariadb.Error as e:
            print(f"Error fetching all kg prices: {e}")
        finally:
            cursor.close()

    def select_all_paged(self, limit: int, offset: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Price, Category
                FROM `KgPrice` LIMIT ? OFFSET ?
            """, (limit, offset))
            for row in cursor:
                yield KgPrice(
                    id=row[0],
                    price=row[1],
                    category=row[2]
                )
        except mariadb.Error as e:
            print(f"Error fetching all kg prices: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, kg_price_id: int) -> (bool, int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `KgPrice` WHERE ID = ?", (kg_price_id,))
            self.db.conn.commit()
            return True, cursor.rowcount
        except mariadb.Error as e:
            print(f"Error deleting kg price by ID: {e}")
            self.db.conn.rollback()
            return False, 0
        finally:
            cursor.close()

    def update(self, kg_price: KgPrice) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `KgPrice` SET Price = ?, Category = ?
                WHERE ID = ?
            """, (kg_price.price, kg_price.category, kg_price.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating kg price: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def exists_by_id(self, kg_price_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT 1
                FROM `KgPrice`
                WHERE ID = ?
                LIMIT 1
            """, (kg_price_id,))
            return cursor.fetchone() is not None
        except mariadb.Error as e:
            print(f"Error checking existence of kg price by ID: {e}")
            return False
        finally:
            cursor.close()
