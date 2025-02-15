from pydantic import BaseModel, Field


class EXCHANGE_NAMES(BaseModel):
    CREATED_TASKS: str = Field(default="topic_created")
    FORMED_TASKS: str = Field("topic_formed")


class QUEUE_NAMES(BaseModel):
    CREATED_TASKS: str = Field(default="created_tasks")
    FORMED_TASKS: str = Field("formed_tasks")


EXCHANGES = EXCHANGE_NAMES()
QUEUES = QUEUE_NAMES()
