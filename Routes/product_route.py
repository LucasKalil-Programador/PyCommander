"""
This module defines a set of endpoints for managing products in a Flask application.
It allows users to create, update, retrieve, and delete products. Access to these endpoints
is restricted based on user roles, ensuring that only authorized users can make changes to
the product database.

Endpoints:
- POST   /product/create: Create a new product (Admin access required).
- POST   /product/update: Update an existing product (Admin access required).
- DELETE /product/delete: Delete a product (Admin access required).
- GET    /product/get:    Retrieve a paginated list of products (Admin, Cashier, Waiter, Cook access required).

Dependencies:
- Flask: For routing and handling HTTP requests.
- Database module: For accessing and managing product data in the repository.
- Utilities: For handling HTTP status codes and role-based access control.
- Validators: For validating input data related to products.

Usage:
1. Initialize the Blueprint in your Flask app.
2. Ensure that appropriate user roles are enforced for each endpoint using the role_required decorator.
3. Utilize the provided validators to validate product data when creating or updating products.
4. Implement pagination for the product retrieval endpoint to manage large datasets efficiently.

Notes:
- Ensure that the database and repository methods used for product management are correctly defined
  in the database module to handle CRUD operations effectively.
"""
from flask import Blueprint, jsonify, request

from database import *
from utils import HttpStatus, role_required
from validators import product, utils
from database import db

# /product/create POST   Admin
# /product/update POST   Admin
# /product/delete DELETE Admin
# /product/get    GET    ADMIN, CASHIER, WAITER, COOK

product_blueprint = Blueprint('product', __name__)


@product_blueprint.route('/create', methods=['POST'])
@product.require_name
@product.require_price
@product.require_stock
@product.optional_category
@product.optional_description
@product.optional_active
@role_required(db, [UserRole.ADMIN])
def create_product():
    new_product = Product(
        name=request.json.get('name'),
        price=request.json.get('price'),
        stock=request.json.get('stock'),
        category=request.json.get('category', ''),
        description=request.json.get('description', ''),
        active=request.json.get('active', False)
    )

    if db.product_repository.insert(new_product):
        return jsonify(success="Product creation successfully.", new_product=new_product), HttpStatus.CREATED.value

    return jsonify(error="Product creation error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@product_blueprint.route('/update', methods=['POST'])
@product.require_id
@product.optional_name
@product.optional_price
@product.optional_stock
@product.optional_category
@product.optional_description
@product.optional_active
@role_required(db, [UserRole.ADMIN])
def update_product():
    base_product = db.product_repository.select_by_id(request.json.get('id'))

    if base_product is None:
        return jsonify(error="Product not found."), HttpStatus.NOT_FOUND.value

    updated_product = Product(
        id=base_product.id,
        name=request.json.get('name', base_product.name),
        price=request.json.get('price', base_product.price),
        stock=request.json.get('stock', base_product.stock),
        category=request.json.get('category', base_product.category),
        description=request.json.get('description', base_product.description),
        active=request.json.get('active', base_product.active)
    )

    if db.product_repository.update(updated_product):
        return jsonify(success="Product update successfully.", updated_product=updated_product), HttpStatus.OK.value

    return jsonify(error="Product update error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@product_blueprint.route('/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_product():
    status, rowcount = db.product_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(error="Product not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="Product delete successfully."), HttpStatus.OK.value

    return jsonify(error="Product delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@product_blueprint.route('/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_products():
    limit = 100
    offset = request.json.get('offset', 0)
    products = [p for p in db.product_repository.select_all_paged(limit=limit, offset=offset)]
    if len(products) == 100:
        return jsonify(products=products, next_page_offset=offset + limit, has_next=True), HttpStatus.OK.value
    else:
        return jsonify(products=products, has_next=False), HttpStatus.OK.value
