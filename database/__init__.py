"""
Module for initializing the database connection for a restaurant management system.

This module loads environment variables from a .env file to configure the database
connection and creates an instance of the DB class for interacting with the database.

Dependencies:
    os: Standard library module for interacting with the operating system.
    dotenv: Library for loading environment variables from a .env file.
    database.objects: Imports various data classes and enums used in the application.
    database.repositorys: Imports repository classes for data access.
    database.DB: Imports the DB class for managing database connections and operations.
"""
import os

import dotenv

from database.objects import *
from database.repositorys import *
from database.DB import DB

dotenv.load_dotenv()

db = DB(
    host_ip=os.getenv("db_host_ip"),
    port=int(os.getenv("db_port")),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    db_name=os.getenv("db_name")
)
