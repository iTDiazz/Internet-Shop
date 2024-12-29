from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models import Category
from app.schemas.categories import CategorySchema
from slugify import slugify

router = APIRouter(prefix='/category', tags=['category'])

@router.get("/categories", response_model=List[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Category).where(True == Category.is_active))
    categories = result.all()
    return categories


@router.get("/category/{category_id}", response_model=CategorySchema)
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.scalar(select(Category).where(category_id == Category.id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    return category


@router.post('/create_category')
async def create_category(create_category_1: CategorySchema, get_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if get_user.get('is_admin'):
        await db.execute(insert(Category).values(
            name=create_category_1.name,
            parent_id=create_category_1.parent_id,
            slug=slugify(create_category_1.name)
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

@router.put('/update_category')
async def update_category(category_id: int, update_category_1: CategorySchema, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(category_id == Category.id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(update(Category).where(category_id == Category.id).values(
            name=update_category_1.name,
            slug=slugify(update_category_1.name),
            parent_id=update_category_1.parent_id
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Category update is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

@router.delete('/delete_category')
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(category_id == Category.id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(delete(Category).where(category_id == Category.id))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Category delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )