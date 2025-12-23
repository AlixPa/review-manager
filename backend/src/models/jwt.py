from datetime import datetime

from pydantic import BaseModel


class JwtPlayload(BaseModel):
    user_id: int
    exp: datetime
