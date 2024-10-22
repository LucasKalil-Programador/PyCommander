"""
This module provides a Flask decorator for validating the 'offset' parameter
in incoming JSON requests.

The `optional_offset` decorator ensures that if the 'offset' parameter is
present in the request, it is a valid non-negative integer. If 'offset' is
not provided, it defaults to 0. If the validation fails, an error response
is returned with a 401 status code.

Functions:
- optional_offset(func): Decorator that validates the 'offset' parameter.
"""
from flask import request, jsonify


# region optional


# Ensures 'offset', if provided, is a valid non-negative integer (default is 0)
def optional_offset(func):
    """
        Decorator that checks if 'offset', if provided, is a valid non-negative integer (default is 0).

        Args:
            func (callable): The function to be wrapped.

        Returns:
            callable: A wrapper function that includes offset validation before executing the original function.
        """
    def wrapper(*args, **kwargs):
        offset = request.json.get('offset', 0)

        if not isinstance(offset, int):
            return jsonify(error=f"Invalid offset type, expected int got {type(offset)}."), 401

        if offset < 0:
            return jsonify(error="offset must be greater or equal to zero."), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

# endregion
