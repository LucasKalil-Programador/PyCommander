"""
This module provides utility functions and decorators for user authentication and role-based access control in a Flask application.

Functions:
- role_required(db: DB, required_roles: list[UserRole]): A decorator that checks if the current user has one of the required roles. If not, it returns a 403 error. Requires JWT authentication.
- generate_bcrypt_hash(data): Generates a bcrypt hash of the provided data (string).
- verify_bcrypt_password(plain_password, hashed_password): Verifies if the provided plain password matches the hashed password using bcrypt.

Dependencies:
- Flask: For creating the web application and managing requests.
- Flask-JWT-Extended: For handling JSON Web Tokens for user authentication.
- Bcrypt: For securely hashing passwords.
- Database: Custom database interactions for user role management.
"""

from functools import wraps

import bcrypt
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import UserRole, DB


def role_required(db: DB, required_roles: list[UserRole]):
    """
    Decorator to restrict access to a view based on user roles.

    Args:
        db (DB): The database instance for user role retrieval.
        required_roles (list[UserRole]): A list of roles allowed to access the decorated function.

    Returns:
        function: The wrapped function that checks user roles.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_username = get_jwt_identity()
            current_user = db.user_repository.select_by_username(current_username)

            if current_user is None:
                return jsonify({"msg": "User not found"}), 404

            if not (current_user.role in required_roles):
                return jsonify({"msg": "Access denied"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def generate_bcrypt_hash(data):
    """
    Generates a bcrypt hash for the given data.

    Args:
        data (str): The data (string) to be hashed.

    Returns:
        str: The bcrypt hashed representation of the data.
    """
    return bcrypt.hashpw(data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_bcrypt_password(plain_password, hashed_password):
    """
    Verifies if the plain password matches the hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
