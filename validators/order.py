import re
from flask import request, jsonify

from database import PaymentMethod


# Ensures 'order_number' is a valid integer (> 0)
def require_number(func):
    def wrapper(*args, **kwargs):
        number = request.json.get('order_number')

        if not isinstance(number, int):
            return jsonify(error=f"Invalid order_number type, expected int got {type(number)}."), 401

        if number <= 0:
            return jsonify(error="Order number must be greater than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'order_id' is an integer
def require_order_id(func):
    def wrapper(*args, **kwargs):
        order_id = request.json.get('order_id')

        if not isinstance(order_id, int):
            return jsonify(error=f"Invalid order_id type, expected int got {type(order_id)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'payment_method' is a valid string and matches a payment method
def require_payment(func):
    def wrapper(*args, **kwargs):
        payment = request.json.get('payment_method')

        if not isinstance(payment, str):
            return jsonify(error=f"Invalid payment_method type, expected string got {type(payment)}."), 401

        if payment not in [r.value for r in PaymentMethod]:
            return jsonify(error="Invalid payment method."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'note' is an optional string up to 255 alphanumeric characters
def optional_note(func):
    def wrapper(*args, **kwargs):
        note = request.json.get('note', '')

        if not isinstance(note, str):
            return jsonify(error=f"Invalid note type, expected string got {type(note)}."), 401

        if not re.fullmatch(r"^[\w\s]{0,255}$", note):
            return jsonify(error="Invalid note format."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'product_id', if provided, is an integer
def optional_product_id(func):
    def wrapper(*args, **kwargs):
        product_id = request.json.get('product_id')
        if product_id is None:
            return func(*args, **kwargs)

        if not isinstance(product_id, int):
            return jsonify(error=f"Invalid product_id type, expected int got {type(product_id)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Ensures 'product_per_kg_id', if provided, is an integer
def optional_product_per_kg_id(func):
    def wrapper(*args, **kwargs):
        product_per_kg_id = request.json.get('product_per_kg_id')
        if product_per_kg_id is None:
            return func(*args, **kwargs)

        if not isinstance(product_per_kg_id, int):
            return jsonify(error=f"Invalid product_per_kg_id type, expected int got {type(product_per_kg_id)}."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
