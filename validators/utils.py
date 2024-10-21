from flask import request, jsonify


# Ensures 'offset', if provided, is a valid non-negative integer (default is 0)
def optional_offset(func):
    def wrapper(*args, **kwargs):
        offset = request.json.get('offset', 0)

        if not isinstance(offset, int):
            return jsonify(error=f"Invalid offset type, expected int got {type(offset)}."), 401

        if offset < 0:
            return jsonify(error="offset must be greater or equal to zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
