"""
order_item_repository.py

This module provides a repository for managing OrderItem records in a MariaDB database.

Classes:
    OrderItemRepository: Handles CRUD operations for OrderItem entries in the `OrderItem` table.
"""
import mariadb

from database import OrderItem


class OrderItemRepository:
    """
        A repository for managing OrderItem records in a MariaDB database.

        Attributes:
            db: A database connection instance.

        Methods:
            insert(order_item: OrderItem) -> bool: Inserts a new order item into the database.
            select_by_id(order_item_id: int) -> OrderItem | None: Retrieves an order item by its ID.
            select_all_items_special_format(order_id: int) -> tuple | None: Retrieves order items in a special format for a specific restaurant order.
            select_by_order_id(restaurant_order_id: int): Yields all order items associated with a given restaurant order ID.
            delete_by_id(order_item_id: int) -> bool: Deletes an order item by its ID.
            update(order_item: OrderItem) -> bool: Updates an existing order item's details in the database.
        """
    def __init__(self, db):
        self.db = db

    def insert(self, order_item: OrderItem) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `OrderItem` (RestaurantOrderID, ProductID, ProductPerKgID, Quantity)
                VALUES (?, ?, ?, ?)
            """, (order_item.restaurant_order_id,
                  order_item.product_id,
                  order_item.product_per_kg_id,
                  order_item.quantity))

            order_item.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting order item: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, order_item_id: int) -> OrderItem | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, RestaurantOrderID, ProductID, ProductPerKgID, Quantity
                FROM `OrderItem`
                WHERE ID = ?
            """, (order_item_id,))
            row = cursor.fetchone()

            if row:
                return OrderItem(
                    id=row[0],
                    restaurant_order_id=row[1],
                    product_id=row[2],
                    product_per_kg_id=row[3],
                    quantity=row[4]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching order item by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_all_items_special_format(self, order_id: int) -> tuple | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT Name, Category, Price, Quantity, Product.ID FROM OrderItem 
                INNER JOIN RestaurantOrder ON RestaurantOrder.ID = OrderItem.RestaurantOrderID 
                INNER JOIN Product ON OrderItem.ProductID = Product.ID WHERE RestaurantOrder.ID = ?;
            """, (order_id,))
            items = []
            for row in cursor:
                item = {
                    "Name": row[0],
                    "Category": row[1],
                    "Price": row[2],
                    "Quantity": row[3],
                    "ProductID": row[4]
                }
                items.append(item)

            items_per_kg = []
            cursor.execute("""
                SELECT Weight, PricePerKg, (Weight * PricePerKg), Category, ProductPerKg.ID FROM OrderItem 
                INNER JOIN RestaurantOrder ON RestaurantOrder.ID = OrderItem.RestaurantOrderID 
                INNER JOIN ProductPerKg ON OrderItem.ProductPerKgID = ProductPerKg.ID WHERE RestaurantOrder.ID = ?;
            """, (order_id,))
            for row in cursor:
                item_per_kg = {
                    "Weight": row[0],
                    "PricePerKg": row[1],
                    "Total": row[2],
                    "Category": row[3],
                    "ProductPerKgID": row[4]
                }
                items_per_kg.append(item_per_kg)
            return items, items_per_kg
        except mariadb.Error as e:
            print(f"Error fetching order item by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_by_order_id(self, restaurant_order_id: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, RestaurantOrderID, ProductID, ProductPerKgID, Quantity
                FROM `OrderItem`
                WHERE RestaurantOrderID = ?
            """, (restaurant_order_id,))
            for row in cursor:
                yield OrderItem(
                    id=row[0],
                    restaurant_order_id=row[1],
                    product_id=row[2],
                    product_per_kg_id=row[3],
                    quantity=row[4]
                )
        except mariadb.Error as e:
            print(f"Error fetching order items by order ID: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, order_item_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `OrderItem` WHERE ID = ?", (order_item_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting order item by ID: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def update(self, order_item: OrderItem) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `OrderItem` 
                SET RestaurantOrderID = ?, ProductID = ?, ProductPerKgID = ?, Quantity = ?
                WHERE ID = ?
            """, (order_item.restaurant_order_id,
                  order_item.product_id,
                  order_item.product_per_kg_id,
                  order_item.quantity,
                  order_item.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating order item: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()
