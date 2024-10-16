import mariadb

from database import Product


class ProductRepository:
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
