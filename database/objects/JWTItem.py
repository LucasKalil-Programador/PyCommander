from dataclasses import dataclass
from datetime import datetime


@dataclass
class JWTItem:
    jti: str
    user_id: int
    expires_at: datetime
