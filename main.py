from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token, \
    get_jwt, get_jti

import os

import dotenv
from database import DB, User, UserRole, JWTItem, RestaurantOrder, Product, OrderStatusHistory, ProductPerKg, KgPrice
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
        return jsonify(error="Order number already exists and is currently open."), 409

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

# endregion

# /product/create POST
# /product/update POST
# /product/delete DELETE
# /product/get    GET
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
        return jsonify(success="Product creation successfully.", new_product=new_product), 200

    return jsonify(error="Product creation error"), 500


@app.route('/product/update', methods=['POST'])
@product.require_id
@product.require_name
@product.require_price
@product.require_stock
@product.optional_category
@product.optional_description
@product.optional_active
@role_required(db, [UserRole.ADMIN])
def update_product():
    updated_product = Product(
        id=request.json.get('id'),
        name=request.json.get('name'),
        price=request.json.get('price'),
        stock=request.json.get('stock'),
        category=request.json.get('category', ''),
        description=request.json.get('description', ''),
        active=request.json.get('active', False)
    )

    if db.product_repository.update(updated_product):
        return jsonify(success="Product update successfully.", updated_product=updated_product), 200

    return jsonify(error="Product update error"), 500


@app.route('/product/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_product():
    if db.product_repository.delete_by_id(int(request.json.get('id'))):
        return jsonify(success="Product delete successfully."), 200

    return jsonify(error="Product delete error"), 500


@app.route('/product/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_products():
    limit = 100
    offset = request.json.get('offset', 0)
    products = [p for p in db.product_repository.select_all_paged(limit=limit, offset=offset)]
    if len(products) == 100:
        return jsonify(products=products, next_page_offset=offset + limit, has_next=True), 200
    else:
        return jsonify(products=products, has_next=False), 200


# endregion

# region /product per kg

@app.route('/product_per_kg/create', methods=['POST'])
@product.require_weight
@product.optional_category
@product.optional_description
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def create_per_kg_product():
    new_product = ProductPerKg(
        weight=request.json.get('weight'),
        price_per_kg=39.90,
        category=request.json.get('category', ''),
        description=request.json.get('description', ''),
    )

    if db.product_per_kg_repository.insert(new_product):
        return jsonify(success="Product per kg creation successfully.", new_product_per_kg=new_product), 200

    return jsonify(error="Product per kg creation error"), 500

# endregion

# /kg_price/create POST
# /kg_price/update POST
# /kg_price/delete DELETE
# /kg_price/get    GET
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
        return jsonify(success="kg price creation successfully.", new_product=new_kg_price), 200

    return jsonify(error="kg price creation error"), 500


@app.route('/kg_price/update', methods=['POST'])
@product.require_price
@product.required_category
@product.require_id
@role_required(db, [UserRole.ADMIN])
def update_kg_price():
    new_kg_price = KgPrice(
        id=request.json.get("id"),
        price=request.json.get('price'),
        category=request.json.get('category'),
    )

    if not db.kg_price_repository.exists_by_id(new_kg_price.id):
        return jsonify(error="kg price id does not exist"), 404

    if db.kg_price_repository.update(new_kg_price):
        return jsonify(success="kg price update successfully.", new_product=new_kg_price), 200

    return jsonify(error="kg price update error"), 500


@app.route('/kg_price/delete', methods=['DELETE'])
@product.require_id
@role_required(db, [UserRole.ADMIN])
def delete_kg_price():
    if db.kg_price_repository.delete_by_id(int(request.json.get('id'))):
        return jsonify(success="kg price delete successfully."), 200

    return jsonify(error="kg price delete error"), 500


@app.route('/kg_price/get', methods=['GET'])
@utils.optional_offset
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_kg_price():
    limit = 100
    offset = request.json.get('offset', 0)
    kg_prices = [p for p in db.kg_price_repository.select_all_paged(limit=limit, offset=offset)]
    if len(kg_prices) == 100:
        return jsonify(kg_prices=kg_prices, next_page_offset=offset + limit, has_next=True), 200
    else:
        return jsonify(kg_prices=kg_prices, has_next=False), 200


# endregion

if __name__ == '__main__':
    app.run(debug=True)
