from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token

import os

import dotenv
from database import *
from http_status import HttpStatus
from security_utils import generate_bcrypt_hash, verify_bcrypt_password, role_required
from validators import user, order, product, utils

dotenv.load_dotenv()

db = DB(
    host_ip=os.getenv("db_host_ip"),
    port=int(os.getenv("db_port")),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    db_name=os.getenv("db_name")
)

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES")))
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS")))
jwt = JWTManager(app)


# region / 'auth'

def add_default_user():
    if db.user_repository.select_all():
        return

    default_user = User(
        name="default",
        username=os.getenv("DEFAULT_USER"),
        password_hash=generate_bcrypt_hash(os.getenv("DEFAULT_PASSWORD")),
        email="default@hotmail.com",
        role=UserRole.ADMIN,
        active=True
    )
    db.user_repository.insert(default_user)
    print("Default user created please create another user and delete this")


@app.route('/login', methods=['POST'])
@user.require_username
@user.require_password
def login():
    username = request.json.get('username')
    password_raw = request.json.get('password')

    temp_user = db.user_repository.select_by_username(username)

    if temp_user is not None and temp_user.active:
        if verify_bcrypt_password(password_raw, temp_user.password_hash):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            expires_at = datetime.now() + app.config['JWT_REFRESH_TOKEN_EXPIRES']
            jwt_item = JWTItem(jti=refresh_token, user_id=temp_user.id, expires_at=expires_at)

            db.jwt_list_repository.delete_by_user_id(temp_user.id)
            db.jwt_list_repository.insert(jwt_item)

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify(msg='Wrong username or password'), 401


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    token = request.headers['Authorization'].replace("Bearer ", "")
    if not db.jwt_list_repository.exists_by_jti(token):
        return jsonify(error="Invalid or expired token. Please log in again."), 401

    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@app.route('/register', methods=['POST'])
@user.require_name
@user.require_email
@user.require_username
@user.require_password
@user.require_active
@user.require_user_role
@role_required(db, [UserRole.ADMIN])
def register_user():
    new_user = User(
        name=request.json.get('name'),
        email=request.json.get('email'),
        username=request.json.get('username'),
        password_hash=generate_bcrypt_hash(request.json.get('password')),
        active=request.json.get('active'),
        role=UserRole(request.json.get('user_role'))
    )

    # if username exist
    if db.user_repository.user_name_exists(new_user.username):
        return jsonify(error="Username already exists."), 409

    # if email exist
    if db.user_repository.email_exists(new_user.email):
        return jsonify(error="Email already exists."), 409

    # try insert
    if db.user_repository.insert(new_user):
        return jsonify(success="User registered successfully."), 200

    # if insertion fail
    return jsonify(error="User registration failed."), 500


# endregion

# region /order


@app.route('/order/checkin', methods=['POST'])
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


@app.route('/order/add_item', methods=['POST'])
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
        return jsonify(error="Either 'product_id' or 'product_per_kg_id' must be provided, but not both."), HttpStatus.CONFLICT.value
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


@app.route('/order/total', methods=['Get'])
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


@app.route('/order/items', methods=['Get'])
@order.require_number
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_items():
    r_order = db.restaurant_order_repository.select_by_number_open(request.json.get('order_number'))
    if r_order is None:
        return jsonify(error="order number not found"), HttpStatus.NOT_FOUND.value

    products, products_per_kg = db.order_item_repository.select_all_items_special_format(r_order.id)
    total = db.restaurant_order_repository.calc_total(r_order.id)
    return jsonify(success="All order items", total=total, items={"products": products, "products_per_kg": products_per_kg})

# endregion

# /product/create POST   Admin
# /product/update POST   Admin
# /product/delete DELETE Admin
# /product/get    GET    ADMIN, CASHIER, WAITER, COOK
# region /product


@app.route('/product/create', methods=['POST'])
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


@app.route('/product/update', methods=['POST'])
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


@app.route('/product/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_product():
    status, rowcount = db.product_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(success="Product not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="Product delete successfully."), HttpStatus.OK.value

    return jsonify(error="Product delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@app.route('/product/get', methods=['GET'])
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


# endregion

# /product_per_kg/create POST   Admin, Cashier, Waiter, Cook
# /product_per_kg/update POST   Admin
# /product_per_kg/delete DELETE Admin
# /product_per_kg/get    GET    Admin, Cashier, Waiter, Cook
# region /product per kg

@app.route('/product_per_kg/create', methods=['POST'])
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
        return jsonify(success="Product per kg creation successfully.", new_product_per_kg=new_product), HttpStatus.CREATED.value

    return jsonify(error="Product per kg creation error"), 500


@app.route('/product_per_kg/update', methods=['POST'])
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
        return jsonify(success="Product per kg update successfully.", new_product_per_kg=new_product), HttpStatus.OK.value

    return jsonify(error="Product per kg update error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@app.route('/per_kg_product/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_per_kg_product():
    limit = 100
    offset = request.json.get('offset', 0)
    per_kg_products = [p for p in db.product_per_kg_repository.select_all_paged(limit=limit, offset=offset)]
    if len(per_kg_products) == 100:
        return jsonify(per_kg_products=per_kg_products, next_page_offset=offset + limit, has_next=True), HttpStatus.OK.value
    else:
        return jsonify(per_kg_products=per_kg_products, has_next=False), HttpStatus.OK.value


@app.route('/per_kg_product/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_per_kg_product():
    status, rowcount = db.product_per_kg_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(success="per_kg_product not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="per_kg_product successfully."), HttpStatus.OK.value

    return jsonify(error="per_kg_product delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value

# endregion

# /kg_price/create POST   Admin
# /kg_price/update POST   Admin
# /kg_price/delete DELETE Admin
# /kg_price/get    GET    Admin, Cashier, Waiter, Cook
# region /KgPrice


@app.route('/kg_price/create', methods=['POST'])
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


@app.route('/kg_price/update', methods=['POST'])
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


@app.route('/kg_price/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_kg_price():
    status, rowcount = db.kg_price_repository.delete_by_id(int(request.json.get('id')))
    if status:
        if rowcount <= 0:
            return jsonify(success="kg price not found."), HttpStatus.NOT_FOUND.value
        return jsonify(success="kg price delete successfully."), HttpStatus.OK.value

    return jsonify(error="kg price delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@app.route('/kg_price/get', methods=['GET'])
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


# endregion

if __name__ == '__main__':
    app.run(debug=True)
    add_default_user()
