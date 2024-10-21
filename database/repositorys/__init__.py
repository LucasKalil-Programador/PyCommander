"""
Module for importing repository classes for a restaurant management system.

This module imports various repository classes that handle database operations
related to restaurant management, including user management, order processing,
product management, and JWT token handling. The repositories facilitate
interactions with the database for CRUD operations.

Imports:
    - KgPriceRepository: Manages price per kilogram for products.
    - UserRepository: Manages user-related data and operations.
    - RestaurantOrderRepository: Handles operations related to restaurant orders.
    - ProductRepository: Manages product-related data and operations.
    - ProductPerKgRepository: Handles products sold by weight (per kg).
    - OrderItemRepository: Manages individual items within restaurant orders.
    - OrderStatusHistoryRepository: Tracks changes in the status of orders.
    - JWTListRepository: Manages JWT tokens for authentication and authorization.
"""
from database.repositorys.KgPriceRepository import KgPriceRepository
from database.repositorys.UserRepository import UserRepository
from database.repositorys.RestaurantOrderRepository import RestaurantOrderRepository
from database.repositorys.ProductRepository import ProductRepository
from database.repositorys.ProductPerKgRepository import ProductPerKgRepository
from database.repositorys.OrderItemRepository import OrderItemRepository
from database.repositorys.OrderStatusHistoryRepository import OrderStatusHistoryRepository
from database.repositorys.JWTListRepository import JWTListRepository
