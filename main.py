from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from Routes import *
from database import *
from utils.security_utils import generate_bcrypt_hash


def add_default_user_if_no_users():
    """
        Creates a default user in the database if no users exist.

        If the user repository is empty, a default user is created with:
        - Name: "default"
        - Username: value of the environment variable `DEFAULT_USER`
        - Password: hashed value of the environment variable `DEFAULT_PASSWORD`
        - Email: "default@hotmail.com"
        - Role: `UserRole.ADMIN`
        - Active: `True`

        The default user is then inserted into the user repository. A message is printed
        to inform that the default user has been created, and another user should be made.

        Returns:
            None: This function does not return a value.

        Notes:
            - Ensure `DEFAULT_USER` and `DEFAULT_PASSWORD` environment variables are set.
            - Using a default user may pose security risks in production environments.
    """
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
    """
    Initializes and configures a Flask application with JWT authentication for handling various API endpoints.

    Returns:
        Flask: The configured Flask application object.
    """
    new_app = Flask(__name__)

    # Configuration settings for JWT
    new_app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    new_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES")))
    new_app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS")))
    jwt = JWTManager(new_app)

    # Register blueprints for different API endpoints
    new_app.register_blueprint(product_blueprint, url_prefix="/product")
    new_app.register_blueprint(kg_price_blueprint, url_prefix="/kg_price")
    new_app.register_blueprint(order_blueprint, url_prefix="/order")
    new_app.register_blueprint(product_per_kg_blueprint, url_prefix="/per_kg_product")
    new_app.register_blueprint(auth_blueprint, url_prefix="/auth")
    new_app.register_blueprint(statistics_blueprint, url_prefix="/statistics")

    return new_app


app = get_app()


def main():
    """
    Main function to run the Flask application, ensuring that default users are added if no users exist.

    This script initializes and runs a Flask app with debugging enabled, as well as checks for and adds default users if there are none in the database.
    """
    app.run(debug=True)
    add_default_user_if_no_users()


if __name__ == '__main__':
    main()
