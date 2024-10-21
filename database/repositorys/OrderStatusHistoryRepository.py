"""
Module for managing order status history in a database using MariaDB.

This module contains the `OrderStatusHistoryRepository` class, which provides
methods for performing CRUD operations on order status history records.
It supports inserting, updating, deleting, and retrieving order status changes
for specific restaurant orders.
"""
import mariadb

from database import OrderStatusHistory, OrderStatus


class OrderStatusHistoryRepository:
    """
        A repository class for managing order status history.

        Attributes:
            db: A database connection object.

        Methods:
            insert(history: OrderStatusHistory) -> bool: Inserts a new order status history record into the database.
            select_by_id(history_id: int) -> OrderStatusHistory | None: Retrieves an order status history record by its ID.
            select_by_order_id(restaurant_order_id: int) -> Generator[OrderStatusHistory, None, None]:
                Yields order status history records for a specific restaurant order ID.
            delete_by_id(history_id: int) -> bool: Deletes an order status history record by its ID.
            update(history: OrderStatusHistory) -> bool: Updates an existing order status history record in the database.
    """
    def __init__(self, db):
        self.db = db

    def insert(self, history: OrderStatusHistory) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `OrderStatusHistory` (RestaurantOrder_ID, Status, Change_Time, Note)
                VALUES (?, ?, ?, ?)
            """, (history.restaurant_order_id, history.status.value,
                  history.change_time, history.note))

            history.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting order status history: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, history_id: int) -> OrderStatusHistory | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, RestaurantOrder_ID, Status, Change_Time, Note
                FROM `OrderStatusHistory`
                WHERE ID = ?
            """, (history_id,))
            row = cursor.fetchone()

            if row:
                return OrderStatusHistory(
                    id=row[0],
                    restaurant_order_id=row[1],
                    status=OrderStatus(row[2]),
                    change_time=row[3],
                    note=row[4]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching order status history by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_by_order_id(self, restaurant_order_id: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, RestaurantOrder_ID, Status, Change_Time, Note
                FROM `OrderStatusHistory`
                WHERE RestaurantOrder_ID = ?
            """, (restaurant_order_id,))
            for row in cursor:
                yield OrderStatusHistory(
                    id=row[0],
                    restaurant_order_id=row[1],
                    status=OrderStatus(row[2]),
                    change_time=row[3],
                    note=row[4]
                )
        except mariadb.Error as e:
            print(f"Error fetching status history by order ID: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, history_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `OrderStatusHistory` WHERE ID = ?", (history_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting order status history by ID: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def update(self, history: OrderStatusHistory) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `OrderStatusHistory` SET RestaurantOrder_ID = ?, Status = ?, Change_Time = ?, Note = ?
                WHERE ID = ?
            """, (history.restaurant_order_id, history.status.value, history.change_time, history.note, history.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating order status history: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()
