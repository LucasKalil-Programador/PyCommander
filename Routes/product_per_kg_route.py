"""
This module defines a set of endpoints for managing products sold by kilogram within a Flask application.
It allows users to create, update, retrieve, and delete products that are priced based on weight.
The endpoints are accessible to users with specific roles, including Admin, Cashier, Waiter, and Cook.

Endpoints:
- POST   /product_per_kg/create: Create a new product priced per kilogram (Admin, Cashier, Waiter, Cook access required).
- POST   /product_per_kg/update: Update an existing product priced per kilogram (Admin access required).
- DELETE /product_per_kg/delete: Delete a product priced per kilogram (Admin access required).
- GET    /product_per_kg/get:    Retrieve a paginated list of products priced per kilogram (Admin, Cashier, Waiter, Cook access required).

Dependencies:
- Flask: For routing and handling HTTP requests.
- Database module: For accessing and managing product data in the repository.
- Utilities: For handling HTTP status codes and role-based access control.
- Validators: For validating input data related to products.

Usage:
1. Initialize the Blueprint in your Flask app.
2. Ensure that appropriate user roles are enforced for each endpoint.
3. Use the provided validators to ensure the integrity of product data when creating or updating.
4. Implement pagination for the product retrieval endpoint to manage large datasets efficiently.
"""
from flask import Blueprint
from flask import jsonify, request

from database import *
from utils import HttpStatus, role_required
from validators import product, utils

# /product_per_kg/create POST   Admin, Cashier, Waiter, Cook
# /product_per_kg/update POST   Admin
# /product_per_kg/delete DELETE Admin
# /product_per_kg/get    GET    Admin, Cashier, Waiter, Cook

product_per_kg_blueprint = Blueprint('product_per_kg', __name__)


@product_per_kg_blueprint.route('/create', methods=['POST'])
@product.require_weight
@product.require_kg_price_id
@product.optional_description
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def create_per_kg_product():
    kg_price = db.kg_price_repository.select_by_id(request.json.get('kg_price_id'))

    if kg_price is None:
        return jsonify(error="Price per kilogram not found"), HttpStatus.NOT_FOUND.value

    new_product = ProductPerKg(
        weight=request.json.get('weight'),
        price_per_kg=kg_price.price,
        category=kg_price.category,
        description=request.json.get('description', ''),
    )

    if db.product_per_kg_repository.insert(new_product):
        return jsonify(success="Product per kg creation successfully.",
                       new_product_per_kg=new_product), HttpStatus.CREATED.value

    return jsonify(error="Product per kg creation error"), 500


@product_per_kg_blueprint.route('/update', methods=['POST'])
@product.require_id
@product.optional_weight
@product.optional_kg_price_id
@product.optional_description
@role_required(db, [UserRole.ADMIN])
def update_per_kg_product():
    base_per_kg_product = db.product_per_kg_repository.select_by_id(request.json.get('id'))

    if base_per_kg_product is None:
        return jsonify(error="Per kg price not found"), HttpStatus.NOT_FOUND.value

    kg_price_id = request.json.get('kg_price_id')
    kg_price = None
    if kg_price_id is not None:
        kg_price = db.kg_price_repository.select_by_id(kg_price_id)
        if kg_price is None:
            return jsonify(error="kilogram price not found"), HttpStatus.NOT_FOUND.value

    new_product = ProductPerKg(
        id=request.json.get('id'),
        weight=request.json.get('weight', base_per_kg_product.weight),
        price_per_kg=base_per_kg_product.price_per_kg if kg_price is None else kg_price.price,
        category=base_per_kg_product.category if kg_price is None else kg_price.category,
        description=request.json.get('description', base_per_kg_product.description),
    )

    if db.product_per_kg_repository.update(new_product):
        return jsonify(success="Product per kg update successfully.",
                       new_product_per_kg=new_product), HttpStatus.OK.value

    return jsonify(error="Product per kg update error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@product_per_kg_blueprint.route('/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_per_kg_product():
    limit = 100
    offset = request.json.get('offset', 0)
    per_kg_products = [p for p in db.product_per_kg_repository.select_all_paged(limit=limit, offset=offset)]
    if len(per_kg_products) == 100:
        return jsonify(per_kg_products=per_kg_products, next_page_offset=offset + limit,
                       has_next=True), HttpStatus.OK.value
    else:
        return jsonify(per_kg_products=per_kg_products, has_next=False), HttpStatus.OK.value


@product_per_kg_blueprint.route('/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_per_kg_product():
    status, rowcount = db.product_per_kg_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(success="per_kg_product not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="per_kg_product successfully."), HttpStatus.OK.value

    return jsonify(error="per_kg_product delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value
