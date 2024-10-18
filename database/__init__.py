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
