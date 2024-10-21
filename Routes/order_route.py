from datetime import datetime

from flask import jsonify, request, Blueprint

from database import *
from utils import HttpStatus, role_required
from validators import order, product, utils

# /order/checkin       POST   ADMIN, CASHIER, WAITER
# /order/add_item      POST   ADMIN, CASHIER, WAITER
# /order/checkout      POST   ADMIN, CASHIER, WAITER
# /order/total         GET    ADMIN, CASHIER, WAITER
# /order/items         GET    ADMIN, CASHIER, WAITER, COOK
# /order/open_orders   GET    ADMIN, CASHIER, WAITER, COOK
# /order/closed_orders GET    ADMIN, CASHIER, WAITER, COOK

order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/checkin', methods=['POST'])
@order.require_number
@order.optional_note
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER])
def checkin():
    new_order = RestaurantOrder(
        number=request.json.get('order_number'),
        entry_time=datetime.now(),
        note=request.json.get('note', '')
    )

    # if number exist and order is open
    if db.restaurant_order_repository.exists_number_open(new_order.number):
        return jsonify(error="Order number already exists and is currently open."), HttpStatus.CONFLICT.value

    # try insert
    if db.restaurant_order_repository.insert(new_order):
        order_history = OrderStatusHistory(
            restaurant_order_id=new_order.id,
            status=new_order.status,
            note="Created"
        )
        if db.order_status_history_repository.insert(order_history):
            return jsonify(success="check in successfully."), 200

    # if insertion fail
    return jsonify(error="Failed to create the order."), 500


@order_blueprint.route('/checkout', methods=['POST'])
@order.require_number
@order.require_payment
@order.optional_note
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER])
def checkout():
    r_order = db.restaurant_order_repository.select_by_number_open(request.json.get('order_number'))
    if r_order is None:
        return jsonify(error="order number not found"), HttpStatus.NOT_FOUND.value

    r_order.payment_method = PaymentMethod(request.json.get('payment_method'))
    r_order.note = request.json.get('note', r_order.note)
    r_order.status = OrderStatus.CLOSED
    r_order.exit_time = datetime.now()
    r_order.paid = True

    r_order.total_amount = db.restaurant_order_repository.calc_total(r_order.id)
    if r_order.total_amount is None:
        return jsonify(error="error when calc total"), HttpStatus.NOT_FOUND.value

    if db.restaurant_order_repository.update(r_order):
        return jsonify(success="Checkout successfully"), HttpStatus.OK.value

    return jsonify(error="Checkout error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@order_blueprint.route('/add_item', methods=['POST'])
@order.require_number
@product.optional_quantity
@order.optional_product_id
@order.optional_product_per_kg_id
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER])
def add_item():
    r_order = db.restaurant_order_repository.select_by_number_open(request.json.get('order_number'))
    if r_order is None:
        return jsonify(error="order number not found"), HttpStatus.NOT_FOUND.value

    product_id = request.json.get('product_id')
    product_per_kg_id = request.json.get('product_per_kg_id')

    if (product_id is not None and product_per_kg_id is not None) or (product_id is None and product_per_kg_id is None):
        return jsonify(
            error="Either 'product_id' or 'product_per_kg_id' must be provided, but not both."), HttpStatus.CONFLICT.value
    elif product_id is not None:
        order_product = db.product_repository.select_by_id(product_id)
        if order_product is None:
            return jsonify(error="product not found"), HttpStatus.NOT_FOUND.value
        order_item = OrderItem(
            restaurant_order_id=r_order.id,
            quantity=request.json.get('quantity', 1),
            product_id=order_product.id
        )
        if db.order_item_repository.insert(order_item):
            return jsonify(success="Product added successfully", new_item=order_item), HttpStatus.OK.value
    elif product_per_kg_id is not None:
        order_product_per_kg = db.product_per_kg_repository.select_by_id(product_per_kg_id)
        if order_product_per_kg is None:
            return jsonify(error="product per kg not found"), HttpStatus.NOT_FOUND.value
        order_item = OrderItem(
            restaurant_order_id=r_order.id,
            quantity=request.json.get('quantity', 1),
            product_per_kg_id=order_product_per_kg.id
        )
        if db.order_item_repository.insert(order_item):
            return jsonify(success="Product per kg added successfully", new_item=order_item), HttpStatus.OK.value

    return jsonify(error="Failed to create the order item."), HttpStatus.INTERNAL_SERVER_ERROR.value


@order_blueprint.route('/total', methods=['Get'])
@order.require_number
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER])
def get_total():
    r_order = db.restaurant_order_repository.select_by_number_open(request.json.get('order_number'))
    if r_order is None:
        return jsonify(error="order number not found"), HttpStatus.NOT_FOUND.value

    total = db.restaurant_order_repository.calc_total(r_order.id)
    if total is not None:
        return jsonify(success="Success to retrieve order total", total=total), HttpStatus.OK.value
    return jsonify(error="error when calc total"), HttpStatus.NOT_FOUND.value


@order_blueprint.route('/items', methods=['Get'])
@order.require_number
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_items():
    r_order = db.restaurant_order_repository.select_by_number_open(request.json.get('order_number'))
    if r_order is None:
        return jsonify(error="order number not found"), HttpStatus.NOT_FOUND.value

    products, products_per_kg = db.order_item_repository.select_all_items_special_format(r_order.id)
    total = db.restaurant_order_repository.calc_total(r_order.id)
    return jsonify(success="All order items", total=total,
                   items={"products": products, "products_per_kg": products_per_kg})


@order_blueprint.route('/open_orders', methods=['Get'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_open_orders():
    limit = 100
    offset = request.json.get('offset', 0)
    products = [p for p in db.restaurant_order_repository.select_all_open_paged(limit=limit, offset=offset)]
    if len(products) == 100:
        return jsonify(products=products, next_page_offset=offset + limit, has_next=True), HttpStatus.OK.value
    else:
        return jsonify(products=products, has_next=False), HttpStatus.OK.value


@order_blueprint.route('/closed_orders', methods=['Get'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_close_orders():
    limit = 100
    offset = request.json.get('offset', 0)
    products = [p for p in db.restaurant_order_repository.select_all_close_paged(limit=limit, offset=offset)]
    if len(products) == 100:
        return jsonify(products=products, next_page_offset=offset + limit, has_next=True), HttpStatus.OK.value
    else:
        return jsonify(products=products, has_next=False), HttpStatus.OK.value
