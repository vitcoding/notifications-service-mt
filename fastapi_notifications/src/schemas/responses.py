from pydantic import BaseModel


class SimpleResultResponse(BaseModel):
    message: str
