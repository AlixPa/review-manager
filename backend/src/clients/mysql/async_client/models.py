from pydantic import BaseModel


class CondReturn(BaseModel):
    condition: str
    args: dict[str, object]
