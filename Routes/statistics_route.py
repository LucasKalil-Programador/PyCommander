"""
This module defines a set of endpoints for retrieving statistical data related to restaurant orders
and product stock in a Flask application. The statistics can be fetched over various timeframes,
allowing authorized users to monitor performance and stock levels effectively.

Endpoints:
- GET /order/day: Retrieve order statistics for the last day (Admin, Cashier, Waiter, Cook access required).
- GET /order/week: Retrieve order statistics for the last week (Admin, Cashier, Waiter, Cook access required).
- GET /order/month: Retrieve order statistics for the last month (Admin, Cashier, Waiter, Cook access required).
- GET /order/year: Retrieve order statistics for the last year (Admin, Cashier, Waiter, Cook access required).
- GET /order/lifetime: Retrieve order statistics since the establishment of the restaurant (Admin, Cashier, Waiter, Cook access required).
- GET /product/stock: Retrieve the current stock summary of products (Admin, Cashier, Waiter, Cook access required).

Dependencies:
- Flask: For routing and handling HTTP requests.
- Database module: For accessing order and product data through the repository.
- Utilities: For role-based access control and HTTP status handling.

Usage:
1. Initialize the Blueprint in your Flask app to handle statistics-related routes.
2. Use the `role_required` decorator to enforce user access restrictions for each endpoint.
3. Implement the `get_order_status` function to centralize the retrieval of order statistics and payment summaries.
4. Ensure the corresponding methods for fetching payment summaries and order statistics are correctly implemented in the database module.

Notes:
- The date calculations utilize Python's `datetime` module to determine the timeframes for statistics.
- If no data is found for the requested statistics, appropriate error messages are returned with the relevant HTTP status codes.
"""
from datetime import datetime, timedelta

from flask import jsonify, Blueprint

from database import *
from utils import role_required, HttpStatus

statistics_blueprint = Blueprint('statistics', __name__)


def get_order_status(before, after):
    payment_summary = db.restaurant_order_repository.get_payment_summary(before, after)
    order_stats = db.restaurant_order_repository.get_order_stats(before, after)

    if payment_summary is None and order_stats is None:
        return jsonify(error="No have any stats."), HttpStatus.NOT_FOUND.value

    return jsonify(success="Success retried stats", payment_summary=payment_summary, order_stats=order_stats)


@statistics_blueprint.route('/order/day', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_status_day():
    now = datetime.now()
    before_now = now - timedelta(days=1)
    return get_order_status(before_now, now)


@statistics_blueprint.route('/order/week', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_status_week():
    now = datetime.now()
    before_now = now - timedelta(days=7)
    return get_order_status(before_now, now)


@statistics_blueprint.route('/order/month', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_status_month():
    now = datetime.now()
    before_now = now - timedelta(days=30)
    return get_order_status(before_now, now)


@statistics_blueprint.route('/order/year', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_status_year():
    now = datetime.now()
    before_now = now - timedelta(days=365)
    return get_order_status(before_now, now)


@statistics_blueprint.route('/order/lifetime', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_order_status_lifetime():
    now = datetime.now()
    before_now = datetime(1900, 1, 1)
    return get_order_status(before_now, now)


@statistics_blueprint.route('/product/stock', methods=['Get'])
@role_required(db, [UserRole.ADMIN, UserRole.CASHIER, UserRole.WAITER, UserRole.COOK])
def get_stock():
    stock = db.product_repository.get_product_summary()
    if stock is None:
        return jsonify(error="Error on get product stock."), HttpStatus.INTERNAL_SERVER_ERROR.value

    return jsonify(success="Success retried stock stats", stock_summary=stock)
