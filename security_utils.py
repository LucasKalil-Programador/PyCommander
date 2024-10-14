from functools import wraps

import bcrypt
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import UserRole, DB


def role_required(db: DB, required_roles: list[UserRole]):
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
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(data.encode('utf-8'), salt).decode('utf-8')


def verify_bcrypt_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
