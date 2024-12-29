from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from starlette import status

from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix='/permission', tags=['permission'])

@router.patch('/update_permission')
async def supplier_permission(user_id: int, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    if get_user.get('is_admin'):
        user = await db.scalar(select(User).where(user_id == User.id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        if user.is_supplier:
            await db.execute(update(User).where(user_id == User.id).values(is_supplier=False, is_customer=True))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is no longer supplier'
            }
        else:
            await db.execute(update(User).where(user_id == User.id).values(is_supplier=True, is_customer=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is now supplier'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You dont have admin permission'
        )

@router.delete('/delete_user')
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    if get_user.get('is_admin'):
        user = await db.scalar(select(User).where(user_id == User.id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User is not found'
            )

        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You cant delete admin user'
            )

        if user.is_active:
            await db.execute(update(User).where(user_id == User.id).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is deleted'
            }
        else:
            await db.execute(update(User).where(user_id == User.id).values(is_active=True))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is activated'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You dont have admin permission'
        )