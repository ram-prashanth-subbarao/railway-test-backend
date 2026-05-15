import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Todo, TodoStatus
from app.schemas import TodoCreate, TodoRead, TodoStatusUpdate, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


async def get_todo_or_404(todo_id: uuid.UUID, db: AsyncSession) -> Todo:
    todo = await db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("", response_model=list[TodoRead])
async def list_todos(
    todo_status: TodoStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> list[Todo]:
    stmt = select(Todo).order_by(Todo.created_at.desc())
    if todo_status is not None:
        stmt = stmt.where(Todo.status == todo_status)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, db: AsyncSession = Depends(get_db)) -> Todo:
    todo = Todo(**payload.model_dump())
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Todo:
    return await get_todo_or_404(todo_id, db)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: uuid.UUID,
    payload: TodoUpdate,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    todo = await get_todo_or_404(todo_id, db)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(todo, field, value)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.patch("/{todo_id}/status", response_model=TodoRead)
async def transition_todo_status(
    todo_id: uuid.UUID,
    payload: TodoStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    todo = await get_todo_or_404(todo_id, db)
    todo.status = payload.status
    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    todo = await get_todo_or_404(todo_id, db)
    await db.delete(todo)
    await db.commit()
