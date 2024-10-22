"""
This module defines a series of decorators that validate incoming JSON request data for user-related attributes in a Flask application.

Decorators:
- `require_name`: Ensures the 'name' attribute is a valid string between 1 and 255 characters, containing only allowed characters (letters, digits, underscores, spaces).
- `require_email`: Validates that the 'email' attribute is a properly formatted string and does not exceed 255 characters.
- `require_username`: Validates that the 'username' attribute is a valid string between 1 and 255 characters, matching allowed characters.
- `require_password`: Ensures the 'password' attribute is a valid string with at least 8 characters.
- `require_active`: Validates that the 'active' attribute is a boolean value.
- `require_user_role`: Ensures the 'user_role' attribute is a valid string matching predefined user roles in the `UserRole` enumeration.

Optional Decorators:
- `optional_name`: Validates 'name' if provided, ensuring it meets the same criteria as `require_name`.
- `optional_email`: Validates 'email' if provided, ensuring it meets the same criteria as `require_email`.
- `optional_password`: Validates 'password' if provided, ensuring it meets the same criteria as `require_password`.
- `optional_active`: Validates 'active' if provided, ensuring it meets the same criteria as `require_active`.
- `optional_user_role`: Validates 'user_role' if provided, ensuring it meets the same criteria as `require_user_role`.
- `optional_new_username`: Validates 'new_username' if provided, ensuring it meets the same criteria as `require_username`.

Each decorator returns a JSON response with an error message and a status code of 401 if the validation fails. If validation passes, the decorated function is called with the original arguments.
"""
import re
from flask import jsonify, request
from database import UserRole


# region require

# Ensures 'name' is a valid string between 1 and 255 characters, matching allowed characters
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


# Ensures 'email' is a valid string format and does not exceed 255 characters
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


# Ensures 'username' is a valid string between 1 and 255 characters, matching allowed characters
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


# Ensures 'password' is a valid string with at least 8 characters
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


# Ensures 'active' is a valid boolean value
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


# Ensures 'user_role' is a valid string and matches defined user roles
def require_user_role(func):
    def wrapper(*args, **kwargs):
        user_role = request.json.get('user_role')

        if not isinstance(user_role, str):
            return jsonify(error=f"Invalid user role type, expected string got {type(user_role)}."), 401

        if user_role not in [r.value for r in UserRole]:
            return jsonify(error="Invalid user role."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# endregion

# region optional


# Ensures 'name', if provided, is a valid string between 1 and 255 characters, matching allowed characters
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


# Ensures 'email', if provided, is a valid string format and does not exceed 255 characters
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


# Ensures 'password', if provided, is a valid string with at least 8 characters
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


# Ensures 'active', if provided, is a valid boolean value
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


# Ensures 'user_role', if provided, is a valid string and matches defined user roles
def optional_user_role(func):
    def wrapper(*args, **kwargs):
        user_role = request.json.get('user_role', None)

        if user_role is None:
            return func(*args, **kwargs)

        if not isinstance(user_role, str):
            return jsonify(error=f"Invalid user role type, expected string got {type(user_role)}."), 401

        if user_role not in [r.value for r in UserRole]:
            return jsonify(error="Invalid user role."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'new_username', if provided, is a valid string between 1 and 255 characters, matching allowed characters
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

# endregion
