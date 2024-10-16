import mariadb

from database import User, UserRole


class UserRepository:
    def __init__(self, db):
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
