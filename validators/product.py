import re

from flask import request, jsonify


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


def require_stock(func):
    def wrapper(*args, **kwargs):
        stock = request.json.get('stock')

        if not isinstance(stock, int):
            return jsonify(error=f"Invalid stock type, expected int got {type(stock)}."), 401

        if stock < 0:
            return jsonify(error="Order number must be greater o equals zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


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


def optional_active(func):
    def wrapper(*args, **kwargs):
        active = request.json.get('active', False)

        if not isinstance(active, bool):
            return jsonify(error=f"Invalid active type, expected bool got {type(active)}."), 401

        if active not in [True, False]:
            return jsonify(error="Active must be a boolean."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_id(func):
    def wrapper(*args, **kwargs):
        pid = request.json.get('id')

        if not isinstance(pid, int):
            return jsonify(error=f"Invalid id type, expected int got {type(pid)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def require_weight(func):
    def wrapper(*args, **kwargs):
        weight = request.json.get('weight')

        if not isinstance(weight, float):
            return jsonify(error=f"Invalid weight type, expected float got {type(weight)}."), 401

        if weight <= 0:
            return jsonify(error="weight must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
