from flask import request, jsonify


def optional_offset(func):
    def wrapper(*args, **kwargs):
        offset = request.json.get('offset', 0)

        if not isinstance(offset, int):
            return jsonify(error=f"Invalid offset type, expected int got {type(offset)}."), 401

        if offset < 0:
            return jsonify(error="offset must be greater of equals than zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
