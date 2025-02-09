from pydantic import BaseModel


class SimpleResultMessage(BaseModel):
    message: str
