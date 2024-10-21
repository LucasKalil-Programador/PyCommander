import re
from flask import request, jsonify


# region require

# Ensures 'name' is a string and matches a specific format (1-255 alphanumeric characters)
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


# Ensures 'price' is a float and greater than zero
def require_price(func):
    def wrapper(*args, **kwargs):
        price = request.json.get('price')

        if not isinstance(price, float):
            return jsonify(error=f"Invalid price type, expected float got {type(price)}."), 401

        if price <= 0:
            return jsonify(error="price must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'stock' is an integer and greater or equal to zero
def require_stock(func):
    def wrapper(*args, **kwargs):
        stock = request.json.get('stock')

        if not isinstance(stock, int):
            return jsonify(error=f"Invalid stock type, expected int got {type(stock)}."), 401

        if stock < 0:
            return jsonify(error="Stock must be greater or equal to zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'category' is a string and matches a specific format (1-255 alphanumeric characters)
def required_category(func):
    def wrapper(*args, **kwargs):
        category = request.json.get('category')

        if not isinstance(category, str):
            return jsonify(error=f"Invalid category type, expected string got {type(category)}."), 401

        if not re.fullmatch(r"^[\w\s]{1,255}$", category):
            return jsonify(error="Invalid category format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'id' is an integer
def require_id(func):
    def wrapper(*args, **kwargs):
        pid = request.json.get('id')

        if not isinstance(pid, int):
            return jsonify(error=f"Invalid id type, expected int got {type(pid)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'kg_price_id' is an integer
def require_kg_price_id(func):
    def wrapper(*args, **kwargs):
        kg_price_id = request.json.get('kg_price_id')

        if not isinstance(kg_price_id, int):
            return jsonify(error=f"Invalid kg_price_id type, expected int got {type(kg_price_id)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'weight' is a float and greater than zero
def require_weight(func):
    def wrapper(*args, **kwargs):
        weight = request.json.get('weight')

        if not isinstance(weight, float):
            return jsonify(error=f"Invalid weight type, expected float got {type(weight)}."), 401

        if weight <= 0:
            return jsonify(error="Weight must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# endregion

# region optional

# Ensures 'weight', if provided, is a valid float greater than zero
def optional_weight(func):
    def wrapper(*args, **kwargs):
        weight = request.json.get('weight')
        if weight is None:
            return func(*args, **kwargs)

        if not isinstance(weight, float):
            return jsonify(error=f"Invalid weight type, expected float got {type(weight)}."), 401

        if weight <= 0:
            return jsonify(error="Weight must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'name', if provided, is a string and matches a specific format (1-255 alphanumeric characters)
def optional_name(func):
    def wrapper(*args, **kwargs):
        name = request.json.get('name')
        if name is None:
            return func(*args, **kwargs)
        if not isinstance(name, str):
            return jsonify(error=f"Invalid name type, expected string got {type(name)}."), 401

        if not re.fullmatch(r"^[\w\s]{1,255}$", name):
            return jsonify(error="Invalid name format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'kg_price_id', if provided, is a valid integer
def optional_kg_price_id(func):
    def wrapper(*args, **kwargs):
        kg_price_id = request.json.get('kg_price_id')
        if kg_price_id is None:
            return func(*args, **kwargs)

        if not isinstance(kg_price_id, int):
            return jsonify(error=f"Invalid kg_price_id type, expected int got {type(kg_price_id)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'active' is a boolean, defaults to False
def optional_active(func):
    def wrapper(*args, **kwargs):
        active = request.json.get('active', False)

        if not isinstance(active, bool):
            return jsonify(error=f"Invalid active type, expected bool got {type(active)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'category', if provided, is a string and matches a specific format (0-255 alphanumeric characters)
def optional_category(func):
    def wrapper(*args, **kwargs):
        category = request.json.get('category', '')

        if not isinstance(category, str):
            return jsonify(error=f"Invalid category type, expected string got {type(category)}."), 401

        if not re.fullmatch(r"^[\w\s]{0,255}$", category):
            return jsonify(error="Invalid category format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'stock', if provided, is an integer and greater or equal to zero
def optional_stock(func):
    def wrapper(*args, **kwargs):
        stock = request.json.get('stock')
        if stock is None:
            return func(*args, **kwargs)

        if not isinstance(stock, int):
            return jsonify(error=f"Invalid stock type, expected int got {type(stock)}."), 401

        if stock < 0:
            return jsonify(error="Stock must be greater or equal to zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'quantity', if provided, is a valid integer greater than zero (defaults to 1)
def optional_quantity(func):
    def wrapper(*args, **kwargs):
        quantity = request.json.get('quantity', 1)

        if not isinstance(quantity, int):
            return jsonify(error=f"Invalid quantity type, expected int got {type(quantity)}."), 401

        if quantity <= 0:
            return jsonify(error="Quantity must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'description', if provided, is a string and matches a specific format (0-255 alphanumeric characters)
def optional_description(func):
    def wrapper(*args, **kwargs):
        description = request.json.get('description', '')

        if not isinstance(description, str):
            return jsonify(error=f"Invalid description type, expected string got {type(description)}."), 401

        if not re.fullmatch(r"^[\w\s]{0,255}$", description):
            return jsonify(error="Invalid description format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'price', if provided, is a valid float greater than zero
def optional_price(func):
    def wrapper(*args, **kwargs):
        price = request.json.get('price')
        if price is None:
            return func(*args, **kwargs)

        if not isinstance(price, float):
            return jsonify(error=f"Invalid price type, expected float got {type(price)}."), 401

        if price <= 0:
            return jsonify(error="Price must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

# endregion
