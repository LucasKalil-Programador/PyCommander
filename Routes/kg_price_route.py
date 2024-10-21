from flask import Blueprint, jsonify, request

from database import *
from utils import HttpStatus, role_required
from validators import product, utils
from database import db

# /kg_price/create POST   Admin
# /kg_price/update POST   Admin
# /kg_price/delete DELETE Admin
# /kg_price/get    GET    Admin, Cashier, Waiter, Cook

kg_price_blueprint = Blueprint('kg_price', __name__)


@kg_price_blueprint.route('/create', methods=['POST'])
@product.require_price
@product.required_category
@role_required(db, [UserRole.ADMIN])
def create_kg_price():
    new_kg_price = KgPrice(
        price=request.json.get('price'),
        category=request.json.get('category'),
    )

    if db.kg_price_repository.insert(new_kg_price):
        return jsonify(success="kg price creation successfully.", new_product=new_kg_price), HttpStatus.CREATED.value

    return jsonify(error="kg price creation error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@kg_price_blueprint.route('/update', methods=['POST'])
@product.optional_category
@product.optional_price
@product.require_id
@role_required(db, [UserRole.ADMIN])
def update_kg_price():
    base_kg_price = db.kg_price_repository.select_by_id(request.json.get("id"))
    if base_kg_price is None:
        return jsonify(error="kg price not found"), HttpStatus.NOT_FOUND.value

    new_kg_price = KgPrice(
        id=base_kg_price.id,
        price=request.json.get('price', base_kg_price.price),
        category=request.json.get('category', base_kg_price.category),
    )

    if db.kg_price_repository.update(new_kg_price):
        return jsonify(success="kg price update successfully.", new_product=new_kg_price), HttpStatus.OK.value

    return jsonify(error="kg price update error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@kg_price_blueprint.route('/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_kg_price():
    status, rowcount = db.kg_price_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(success="kg price not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="kg price delete successfully."), HttpStatus.OK.value

    return jsonify(error="kg price delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@kg_price_blueprint.route('/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_kg_price():
    limit = 100
    offset = request.json.get('offset', 0)
    kg_prices = [p for p in db.kg_price_repository.select_all_paged(limit=limit, offset=offset)]
    if len(kg_prices) == 100:
        return jsonify(kg_prices=kg_prices, next_page_offset=offset + limit, has_next=True), HttpStatus.OK.value
    else:
        return jsonify(kg_prices=kg_prices, has_next=False), HttpStatus.OK.value