from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from Routes import *
from database import *
from utils.security_utils import generate_bcrypt_hash


def add_default_user_if_no_users():
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


def get_app():
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES")))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS")))
    jwt = JWTManager(app)

    app.register_blueprint(product_blueprint,        url_prefix="/product")
    app.register_blueprint(kg_price_blueprint,       url_prefix="/kg_price")
    app.register_blueprint(order_blueprint,          url_prefix="/order")
    app.register_blueprint(product_per_kg_blueprint, url_prefix="/per_kg_product")
    app.register_blueprint(auth_blueprint,           url_prefix="/auth")
    app.register_blueprint(statistics_blueprint,     url_prefix="/statistics")
    return app


if __name__ == '__main__':
    get_app().run(debug=True)
    add_default_user_if_no_users()
