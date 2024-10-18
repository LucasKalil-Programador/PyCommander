from datetime import datetime, timedelta

from flask import jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token

from database import *
from utils import generate_bcrypt_hash, verify_bcrypt_password, role_required
from validators import user

# /auth/login    POST
# /auth/refresh  POST
# /auth/register DELETE Admin

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
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

            expires_at = datetime.now() + timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS")))
            jwt_item = JWTItem(jti=refresh_token, user_id=temp_user.id, expires_at=expires_at)

            db.jwt_list_repository.delete_by_user_id(temp_user.id)
            db.jwt_list_repository.insert(jwt_item)

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify(msg='Wrong username or password'), 401


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    token = request.headers['Authorization'].replace("Bearer ", "")
    if not db.jwt_list_repository.exists_by_jti(token):
        return jsonify(error="Invalid or expired token. Please log in again."), 401

    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@auth_blueprint.route('/register', methods=['POST'])
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
