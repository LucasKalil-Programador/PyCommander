import re
from functools import wraps

from flask import jsonify, request

from database import UserRole


def require_name(func):
    def wrapper(*args, **kwargs):
        name = request.json.get('name')

        if not isinstance(name, str):
            return jsonify(error=f"Invalid name type, expected string got {type(name)}."), 401

        if not re.fullmatch(r"^[\w\s]{1,255}$", name):
            return jsonify(error="Invalid name format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_email(func):
    def wrapper(*args, **kwargs):
        email = request.json.get('email')

        if not isinstance(email, str):
            return jsonify(error=f"Invalid email type, expected string got {type(email)}."), 401

        if not re.fullmatch(r"^[\w\-.]+@([\w-]+\.)+[\w-]{2,4}$", email) or len(email) > 255:
            return jsonify(error="Invalid email format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_username(func):
    def wrapper(*args, **kwargs):
        username = request.json.get('username')

        if not isinstance(username, str):
            return jsonify(error=f"Invalid username type, expected string got {type(username)}."), 401

        if not re.fullmatch(r"^[\w\s-]{1,255}$", username):
            return jsonify(error="Invalid username format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_password(func):
    def wrapper(*args, **kwargs):
        password_raw = request.json.get('password')

        if not isinstance(password_raw, str):
            return jsonify(error=f"Invalid password type, expected string got {type(password_raw)}."), 401

        if len(password_raw) < 8:
            return jsonify(error="Password must be at least 8 characters long."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_active(func):
    def wrapper(*args, **kwargs):
        active = request.json.get('active')

        if not isinstance(active, bool):
            return jsonify(error=f"Invalid active type, expected bool got {type(active)}."), 401

        if active not in [True, False]:
            return jsonify(error="Active must be a boolean."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_user_role(func):
    def wrapper(*args, **kwargs):
        user_role = request.json.get('user_role')

        if not isinstance(user_role, str):
            return jsonify(error=f"Invalid password type, expected string got {type(user_role)}."), 401

        if user_role not in [r.value for r in UserRole]:
            return jsonify(error="Invalid user role."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_name(func):
    def wrapper(*args, **kwargs):
        name = request.json.get('name', None)
        if name is None:
            return func(*args, **kwargs)

        if not isinstance(name, str):
            return jsonify(error=f"Invalid name type, expected string got {type(name)}."), 401

        if not re.fullmatch(r"^[\w\s]{1,255}$", name):
            return jsonify(error="Invalid name format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_email(func):
    def wrapper(*args, **kwargs):
        email = request.json.get('email', None)

        if email is None:
            return func(*args, **kwargs)

        if not isinstance(email, str):
            return jsonify(error=f"Invalid email type, expected string got {type(email)}."), 401

        if not re.fullmatch(r"^[\w\-.]+@([\w-]+\.)+[\w-]{2,4}$", email) or len(email) > 255:
            return jsonify(error="Invalid email format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_password(func):
    def wrapper(*args, **kwargs):
        password_raw = request.json.get('password', None)

        if password_raw is None:
            return func(*args, **kwargs)

        if not isinstance(password_raw, str):
            return jsonify(error=f"Invalid password type, expected string got {type(password_raw)}."), 401

        if len(password_raw) < 8:
            return jsonify(error="Password must be at least 8 characters long."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_active(func):
    def wrapper(*args, **kwargs):
        active = request.json.get('active', None)

        if active is None:
            return func(*args, **kwargs)

        if not isinstance(active, bool):
            return jsonify(error=f"Invalid active type, expected bool got {type(active)}."), 401

        if active not in [True, False]:
            return jsonify(error="Active must be a boolean."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_user_role(func):
    def wrapper(*args, **kwargs):
        user_role = request.json.get('user_role', None)

        if user_role is None:
            return func(*args, **kwargs)

        if not isinstance(user_role, str):
            return jsonify(error=f"Invalid password type, expected string got {type(user_role)}."), 401

        if user_role not in [r.value for r in UserRole]:
            return jsonify(error="Invalid user role."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def optional_new_username(func):
    def wrapper(*args, **kwargs):
        username = request.json.get('new_username', None)

        if username is None:
            return func(*args, **kwargs)

        if not isinstance(username, str):
            return jsonify(error=f"Invalid new_username type, expected string got {type(username)}."), 401

        if not re.fullmatch(r"^[\w\s-]{1,255}$", username):
            return jsonify(error="Invalid new_username format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper