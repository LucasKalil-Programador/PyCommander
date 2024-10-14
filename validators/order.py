import re

from flask import request, jsonify


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
