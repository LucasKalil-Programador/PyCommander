import mariadb

from database import JWTItem


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
