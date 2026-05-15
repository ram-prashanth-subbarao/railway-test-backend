import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Comment, Todo
from app.schemas import CommentCreate, CommentRead

router = APIRouter(tags=["comments"])


async def get_todo_or_404(todo_id: uuid.UUID, db: AsyncSession) -> Todo:
    todo = await db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("/todos/{todo_id}/comments", response_model=list[CommentRead])
async def list_comments(
    todo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Comment]:
    await get_todo_or_404(todo_id, db)
    stmt = select(Comment).where(Comment.todo_id == todo_id).order_by(Comment.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/todos/{todo_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    todo_id: uuid.UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
) -> Comment:
    await get_todo_or_404(todo_id, db)
    comment = Comment(todo_id=todo_id, body=payload.body)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    comment = await db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.delete(comment)
    await db.commit()
