"""
Module for managing restaurant orders in a database using MariaDB.

This module contains the `RestaurantOrderRepository` class, which provides
methods to insert, update, delete, and retrieve restaurant orders from
the database. It also includes functionality for calculating total amounts
for orders and checking the existence of open orders by their number.
"""
import datetime

import mariadb

from database import RestaurantOrder


class RestaurantOrderRepository:
    """
        A repository class for performing CRUD operations on restaurant orders.

        Attributes:
            db: A database connection object.

        Methods:
            insert(order: RestaurantOrder) -> bool: Inserts a new order into the database.
            select_by_id(order_id: int) -> RestaurantOrder | None: Retrieves an order by its ID.
            select_by_number_open(number: int) -> RestaurantOrder | None: Retrieves an open order by its number.
            select_all() -> Generator[RestaurantOrder, None, None]: Yields all orders in the database.
            select_all_open_paged(limit: int, offset: int) -> Generator[RestaurantOrder, None, None]:
                Yields open orders with pagination.
            select_all_close_paged(limit: int, offset: int) -> Generator[RestaurantOrder, None, None]:
                Yields closed orders with pagination.
            delete_by_id(order_id: int) -> bool: Deletes an order by its ID.
            update(order: RestaurantOrder) -> bool: Updates an existing order in the database.
            exists_number_open(number: int) -> bool: Checks if an open order exists by its number.
            calc_total(order_id: int) -> float | None: Calculates the total amount for a specific order.
            get_payment_summary(entry_date: datetime.datetime, exit_date: datetime.datetime) -> dict
                create a summary of payment methods
    """
    def __init__(self, db):
        self.db = db

    def insert(self, order: RestaurantOrder) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO RestaurantOrder (Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order.number, order.entry_time, order.exit_time, order.status.value,
                  order.note, order.payment_method.value if order.payment_method else None,
                  order.total_amount, order.paid))

            order.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting order: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, order_id: int) -> RestaurantOrder | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid
                FROM RestaurantOrder
                WHERE ID = ?
            """, (order_id,))
            row = cursor.fetchone()

            if row:
                return RestaurantOrder(
                    id=row[0],
                    number=row[1],
                    entry_time=row[2],
                    exit_time=row[3],
                    status=row[4],
                    note=row[5],
                    payment_method=row[6],
                    total_amount=row[7],
                    paid=row[8]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching order by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_by_number_open(self, number: int) -> RestaurantOrder | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid
                FROM RestaurantOrder
                WHERE Number = ? AND Status = 'Open'
            """, (number,))
            row = cursor.fetchone()

            if row:
                return RestaurantOrder(
                    id=row[0],
                    number=row[1],
                    entry_time=row[2],
                    exit_time=row[3],
                    status=row[4],
                    note=row[5],
                    payment_method=row[6],
                    total_amount=row[7],
                    paid=row[8]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching order by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_all(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid
                FROM RestaurantOrder
            """)
            for row in cursor:
                yield RestaurantOrder(
                    id=row[0],
                    number=row[1],
                    entry_time=row[2],
                    exit_time=row[3],
                    status=row[4],
                    note=row[5],
                    payment_method=row[6],
                    total_amount=row[7],
                    paid=row[8]
                )
        except mariadb.Error as e:
            print(f"Error fetching all orders: {e}")
        finally:
            cursor.close()

    def select_all_open_paged(self, limit: int, offset: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid
                FROM RestaurantOrder WHERE Status = 'Open' LIMIT ? OFFSET ?
            """, (limit, offset))
            for row in cursor:
                yield RestaurantOrder(
                    id=row[0],
                    number=row[1],
                    entry_time=row[2],
                    exit_time=row[3],
                    status=row[4],
                    note=row[5],
                    payment_method=row[6],
                    total_amount=row[7],
                    paid=row[8]
                )
        except mariadb.Error as e:
            print(f"Error fetching all orders: {e}")
        finally:
            cursor.close()

    def select_all_close_paged(self, limit: int, offset: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Number, Entry_Time, Exit_Time, Status, Note, Payment_Method, Total_Amount, Paid
                FROM RestaurantOrder WHERE Status = 'Closed' LIMIT ? OFFSET ?
            """, (limit, offset))
            for row in cursor:
                yield RestaurantOrder(
                    id=row[0],
                    number=row[1],
                    entry_time=row[2],
                    exit_time=row[3],
                    status=row[4],
                    note=row[5],
                    payment_method=row[6],
                    total_amount=row[7],
                    paid=row[8]
                )
        except mariadb.Error as e:
            print(f"Error fetching all orders: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, order_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM RestaurantOrder WHERE ID = ?", (order_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error delete order by ID: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def update(self, order: RestaurantOrder) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE RestaurantOrder SET Number = ?, Entry_Time = ?, Exit_Time = ?, Status = ?, Note = ?, 
                Payment_Method = ?, Total_Amount = ?, Paid = ? WHERE ID = ?
            """, (order.number, order.entry_time, order.exit_time, order.status.value,
                  order.note, order.payment_method.value if order.payment_method else None,
                  order.total_amount, order.paid, order.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating order: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def exists_number_open(self, number: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                        SELECT EXISTS (SELECT 1 FROM RestaurantOrder WHERE Number = ? AND Status = 'Open')
                    """, (number,))
            row = cursor.fetchone()
            return bool(row[0])
        except mariadb.Error as e:
            print(f"Error on checking if number open exist: {e}")
            return False
        finally:
            cursor.close()

    def calc_total(self, order_id: int):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                        SELECT 
                            (SELECT SUM(OrderItem.Quantity * Product.Price) 
                             FROM OrderItem 
                             INNER JOIN RestaurantOrder ON RestaurantOrder.ID = OrderItem.RestaurantOrderID 
                             INNER JOIN Product ON OrderItem.ProductID = Product.ID 
                             WHERE RestaurantOrder.ID = ?) 
                            +
                            (SELECT SUM(OrderItem.Quantity * ProductPerKg.PricePerKg * ProductPerKg.Weight) 
                             FROM OrderItem 
                             INNER JOIN RestaurantOrder ON RestaurantOrder.ID = OrderItem.RestaurantOrderID 
                             INNER JOIN ProductPerKg ON OrderItem.ProductPerKgID = ProductPerKg.ID 
                             WHERE RestaurantOrder.ID = ?) 
                        AS Total;
                    """, (order_id, order_id))
            row = cursor.fetchone()

            if row:
                return row[0] if row[0] is not None else 0
            return None
        except mariadb.Error as e:
            print(f"Error fetching order by ID: {e}")
            return None
        finally:
            cursor.close()

    def get_payment_summary(self, entry_date: datetime.datetime, exit_date: datetime.datetime):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    Payment_Method,
                    COUNT(*) AS Count,
                    SUM(Total_Amount) AS Total_Sum
                FROM
                    RestaurantOrder
                WHERE
                    Paid = 1
                    AND Entry_Time BETWEEN ? AND ?
                    AND Payment_Method IN ('Pix', 'Card', 'Cash', 'Others')
                GROUP BY
                    Payment_Method;
            """, (entry_date, exit_date))
            rows = cursor.fetchall()

            if rows:
                return [
                        {
                            "Payment_Method": row[0],
                            "Count": row[1],
                            "Total_Sum": row[2]
                        } for row in rows
                    ]
            return None
        except mariadb.Error as e:
            print(f"Error fetching payment summary: {e}")
            return None
        finally:
            cursor.close()

    def get_order_stats(self, entry_date: datetime.datetime, exit_date: datetime.datetime):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    SUM(Total_Amount) AS Total_Sum,
                    AVG(Total_Amount) AS Average_Amount,
                    MAX(Total_Amount) AS Max_Amount,
                    MIN(Total_Amount) AS Min_Amount,
                    SUM(TIMESTAMPDIFF(SECOND, Entry_Time, Exit_Time)) AS Total_Duration_Seconds,
                    AVG(TIMESTAMPDIFF(SECOND, Entry_Time, Exit_Time)) AS Average_Duration_Seconds,
                    MAX(TIMESTAMPDIFF(SECOND, Entry_Time, Exit_Time)) AS Max_Duration_Seconds,
                    MIN(TIMESTAMPDIFF(SECOND, Entry_Time, Exit_Time)) AS Min_Duration_Seconds
                FROM
                    RestaurantOrder
                WHERE
                    Paid = 1
                    AND Entry_Time BETWEEN ? AND ?;
            """, (entry_date, exit_date))
            row = cursor.fetchone()

            if row:
                return {
                    "Total_Sum": row[0],
                    "Average_Amount": row[1],
                    "Max_Amount": row[2],
                    "Min_Amount": row[3],
                    "Total_Duration_Seconds": row[4],
                    "Average_Duration_Seconds": row[5],
                    "Max_Duration_Seconds": row[6],
                    "Min_Duration_Seconds": row[7]
                }
            return None
        except mariadb.Error as e:
            print(f"Error fetching order statistics: {e}")
            return None
        finally:
            cursor.close()