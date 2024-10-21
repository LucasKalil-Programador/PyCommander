"""
jwt_repository.py

This module provides a repository for managing JSON Web Token (JWT) items in a MariaDB database.

Classes:
    JWTListRepository: Handles CRUD operations for JWT items in the `JWTList` table.
"""
import mariadb

from database import JWTItem


class JWTListRepository:
    """
        A repository for managing JWT items in a database.

        Methods:
            insert(jwt: JWTItem) -> bool: Inserts a new JWT item into the database.
            exists_by_jti(jti: str) -> bool: Checks if a JWT with the specified JTI exists.
            delete_by_user_id(user_id: int) -> bool: Deletes JWT items associated with a given user ID.
    """
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
