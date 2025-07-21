# FastAPI Best Practices for TODO App

## Project Structure Pattern
```
src/todo_app/
├── main.py              # App entry point
├── config.py            # Settings management
├── database/
│   ├── connection.py    # Database setup
│   └── models.py        # SQLAlchemy models
├── api/
│   ├── dependencies.py  # FastAPI dependencies
│   └── routes/
│       └── todos.py     # Todo endpoints
├── services/
│   └── todo_service.py  # Business logic
├── schemas/
│   └── todo_schemas.py  # Pydantic models
└── tests/
    ├── conftest.py      # Pytest fixtures
    ├── unit/            # Unit tests
    └── integration/     # API tests
```

## Dependency Injection Pattern
```python
# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database.connection import get_async_session
from .services.todo_service import TodoService

async def get_todo_service(
    session: AsyncSession = Depends(get_async_session)
) -> TodoService:
    return TodoService(session)
```

## Route Handler Pattern
```python
# api/routes/todos.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    try:
        todo = await service.create_todo(todo_data)
        return TodoResponse.model_validate(todo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
```

## Error Handling Pattern
```python
# Custom exceptions
class TodoNotFoundError(Exception):
    pass

# Exception handler
@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Todo not found: {str(exc)}"}
    )
```

## Pydantic Schema Pattern
```python
# Base schema with common fields
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: int = Field(default=1, ge=1, le=5)

# Request schemas
class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    completed: Optional[bool] = None

# Response schema
class TodoResponse(TodoBase):
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

## Critical Configuration
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TODO API",
    description="A TODO application API",
    version="1.0.0"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```