import mariadb

from database.objects import RestaurantOrder, PaymentMethod, User, UserRole, Product, ProductPerKg, OrderStatusHistory, \
    OrderStatus, OrderItem, JWTItem, KgPrice


class DB:
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
        return KgPriceRepository(self)

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


class RestaurantOrderRepository:
    def __init__(self, db: DB):
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


class UserRepository:
    def __init__(self, db: DB):
        self.db = db

    def insert(self, user: User) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `User` (Name, Username, Email, PasswordHash, Role, Active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.name, user.username, user.email, user.password_hash,
                  user.role.value, user.active))

            user.id = cursor.lastrowid
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting user: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def select_by_id(self, user_id: int) -> User | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Username, Email, PasswordHash, Role, Active
                FROM `User`
                WHERE ID = ?
            """, (user_id,))
            row = cursor.fetchone()

            if row:
                return User(
                    id=row[0],
                    name=row[1],
                    username=row[2],
                    email=row[3],
                    password_hash=row[4],
                    role=UserRole[row[5].upper()],
                    active=row[6]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching user by ID: {e}")
            return None
        finally:
            cursor.close()

    def select_by_username(self, username: str) -> User | None:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Username, Email, PasswordHash, Role, Active
                FROM `User`
                WHERE Username = ?
            """, (username,))
            row = cursor.fetchone()

            if row:
                return User(
                    id=row[0],
                    name=row[1],
                    username=row[2],
                    email=row[3],
                    password_hash=row[4],
                    role=UserRole[row[5].upper()],
                    active=row[6]
                )
            return None
        except mariadb.Error as e:
            print(f"Error fetching user by Username: {e}")
            return None
        finally:
            cursor.close()

    def select_all(self):
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Name, Username, Email, PasswordHash, Role, Active
                FROM `User`
            """)
            for row in cursor:
                yield User(
                    id=row[0],
                    name=row[1],
                    username=row[2],
                    email=row[3],
                    password_hash=row[4],
                    role=UserRole[row[5].upper()],
                    active=row[6]
                )
        except mariadb.Error as e:
            print(f"Error fetching all users: {e}")
        finally:
            cursor.close()

    def delete_by_id(self, user_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `User` WHERE ID = ?", (user_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting user by ID: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def update(self, user: User) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE `User` SET Name = ?, Username = ?, Email = ?, PasswordHash = ?, Role = ?, Active = ?
                WHERE ID = ?
            """, (user.name, user.username, user.email, user.password_hash,
                  user.role.value, user.active, user.id))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error updating user: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def user_name_exists(self, username: str) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                        SELECT EXISTS (SELECT 1 FROM User WHERE Username = ?)
                    """, (username, ))
            row = cursor.fetchone()
            return bool(row[0])
        except mariadb.Error as e:
            print(f"Error on checking if username exist: {e}")
            return False
        finally:
            cursor.close()

    def email_exists(self, email: str) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                        SELECT EXISTS (SELECT 1 FROM User WHERE Email = ?)
                    """, (email, ))
            row = cursor.fetchone()
            return bool(row[0])
        except mariadb.Error as e:
            print(f"Error on checking if email exist: {e}")
            return False
        finally:
            cursor.close()


class ProductRepository:
    def __init__(self, db: DB):
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

    def delete_by_id(self, product_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `Product` WHERE ID = ?", (product_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting product by ID: {e}")
            self.db.conn.rollback()
            return False
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


class ProductPerKgRepository:
    def __init__(self, db: DB):
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

    def delete_by_id(self, product_per_kg_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `ProductPerKg` WHERE ID = ?", (product_per_kg_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting product per kg by ID: {e}")
            self.db.conn.rollback()
            return False
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


class KgPriceRepository:
    def __init__(self, db: DB):
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

    def delete_by_id(self, kg_price_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `KgPrice` WHERE ID = ?", (kg_price_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting kg price by ID: {e}")
            self.db.conn.rollback()
            return False
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


class OrderStatusHistoryRepository:
    def __init__(self, db: DB):
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


class OrderItemRepository:
    def __init__(self, db: DB):
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


class JWTListRepository:
    def __init__(self, db):
        self.db = db

    def insert(self, jwt: JWTItem) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO `JWTList` (jti, user_id, expires_at)
                VALUES (?, ?, ?)
            """, (jwt.jti, jwt.user_id, jwt.expires_at))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error inserting JWT: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

    def exists_by_jti(self, jti: str) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(""" 
                SELECT EXISTS (
                    SELECT 1 
                    FROM `JWTList` 
                    WHERE jti = ?
                )
            """, (jti,))
            exists = cursor.fetchone()[0]
            return bool(exists)
        except mariadb.Error as e:
            print(f"Error checking existence of JWT by jti: {e}")
            return False
        finally:
            cursor.close()

    def delete_by_user_id(self, user_id: int) -> bool:
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("DELETE FROM `JWTList` WHERE user_id = ?", (user_id,))
            self.db.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error deleting JWT by user_id: {e}")
            self.db.conn.rollback()
            return False
        finally:
            cursor.close()

