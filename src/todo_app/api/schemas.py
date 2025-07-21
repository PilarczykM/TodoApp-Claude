from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    category: str = Field(default="General", max_length=50, description="Task category")


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    category: str | None = Field(None, max_length=50, description="Task category")
    completed: bool | None = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Task unique identifier")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Task description")
    category: str = Field(..., description="Task category")
    completed: bool = Field(..., description="Task completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")


class TaskFiltersRequest(BaseModel):
    category: str | None = Field(None, description="Filter by category")
    completed: bool | None = Field(None, description="Filter by completion status")
    search: str | None = Field(None, description="Search in title and description")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of tasks to return")
    offset: int = Field(default=0, ge=0, description="Number of tasks to skip")


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching filters")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Error details")


class MessageResponse(BaseModel):
    message: str = Field(..., description="Success message")
