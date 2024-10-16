import mariadb

from database import RestaurantOrder


class RestaurantOrderRepository:
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
                return row[0]
            return None
        except mariadb.Error as e:
            print(f"Error fetching order by ID: {e}")
            return None
        finally:
            cursor.close()