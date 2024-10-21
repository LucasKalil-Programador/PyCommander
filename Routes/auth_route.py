from datetime import datetime, timedelta

from flask import jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token

from database import *
from utils import generate_bcrypt_hash, verify_bcrypt_password, role_required, HttpStatus
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
@user.require_username
@user.require_name
@user.require_email
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


@auth_blueprint.route('/edit', methods=['POST'])
@user.require_username
@user.optional_new_username
@user.optional_name
@user.optional_email
@user.optional_password
@user.optional_active
@user.optional_user_role
@role_required(db, [UserRole.ADMIN])
def edit_user():
    this_user = db.user_repository.select_by_username(request.json.get('username'))

    password = request.json.get('password', None)
    password_hash = this_user.password_hash
    if password is not None:
        password_hash = generate_bcrypt_hash(password)

    new_user = User(
        id=this_user.id,
        name=request.json.get('name', this_user.name),
        email=request.json.get('email', this_user.email),
        username=request.json.get('new_username', this_user.username),
        password_hash=password_hash,
        active=request.json.get('active', this_user.active),
        role=UserRole(request.json.get('user_role', this_user.role))
    )

    # if new_user equals old_user
    if this_user == new_user:
        return jsonify(error="Update not have any changes."), HttpStatus.CONFLICT.value

    # if email exist
    if this_user.email != new_user.email and db.user_repository.email_exists(new_user.email):
        return jsonify(error="Email already exists."), 409

    # try insert
    if db.user_repository.update(new_user):
        return jsonify(success="User edited successfully."), HttpStatus.OK.value

    if this_user.username != new_user.username or this_user.password_hash != new_user.password_hash:
        db.jwt_list_repository.delete_by_user_id(this_user.id)

    # if insertion fail
    return jsonify(error="User edition failed."), 500


@auth_blueprint.route('/delete', methods=['DELETE'])
@user.require_username
@role_required(db, [UserRole.ADMIN])
def delete_user():
    username = request.json.get('username')
    temp_user = db.user_repository.select_by_username(username)

    if temp_user is None:
        return jsonify(success="User not found."), HttpStatus.NOT_FOUND.value

    if db.user_repository.delete_by_id(temp_user.id):
        return jsonify(success="User delete successfully."), HttpStatus.OK.value

    return jsonify(error="User delete error"), HttpStatus.INTERNAL_SERVER_ERROR.value


@auth_blueprint.route('/get', methods=['GET'])
@role_required(db, [UserRole.ADMIN])
def get_users():
    users = [{"name": u.name, "username": u.username, "email": u.email, "role": u.role.value, "active": u.active} for u in db.user_repository.select_all()]
    return jsonify(success="Success retrieve all users", users=users), HttpStatus.OK.value
