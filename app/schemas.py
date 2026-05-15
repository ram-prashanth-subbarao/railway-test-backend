import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TodoStatus


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TodoStatus = TodoStatus.BACKLOG


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TodoStatus | None = None


class TodoStatusUpdate(BaseModel):
    status: TodoStatus


class TodoRead(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    todo_id: uuid.UUID
    body: str
    created_at: datetime
