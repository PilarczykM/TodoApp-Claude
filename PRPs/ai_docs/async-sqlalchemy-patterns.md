# SQLAlchemy Async Patterns for TODO App

## Critical Session Management Patterns

### Session Factory Setup
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Create engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set True for debug SQL logging
)

# Session factory with proper config
async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False,  # CRITICAL: Access attrs after commit
    class_=AsyncSession
)

async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Repository Pattern with Async
```python
class AsyncBaseRepository:
    def __init__(self, model: Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> Model:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[Model]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_filter(self, **filters) -> List[Model]:
        stmt = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

## Critical Gotchas

1. **NEVER share AsyncSession across concurrent tasks** - Each task needs its own session
2. **Use expire_on_commit=False** - Required to access model attributes after commit
3. **Explicit relationship loading** - Use `selectinload()` or `joinedload()` to avoid lazy loading issues
4. **Proper session cleanup** - Always use async context managers

## Eager Loading Patterns
```python
# Use selectinload for relationships
stmt = select(Task).options(selectinload(Task.category))
result = await session.execute(stmt)
tasks = result.scalars().all()

# Access relationship safely
for task in tasks:
    print(task.category.name)  # No additional query needed
```