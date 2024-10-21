from datetime import datetime, timedelta

from flask import jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token

from database import *
from utils import generate_bcrypt_hash, verify_bcrypt_password, role_required, HttpStatus
from validators import user

statistics_blueprint = Blueprint('statistics', __name__)

# SELECT Payment_Method, SUM(Total_Amount) AS Total_Sum FROM RestaurantOrder WHERE Paid = 1 GROUP BY Payment_Method;