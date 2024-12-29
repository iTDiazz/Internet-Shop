from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from app.models import Product, Category
from app.schemas.products import ProductSchema
from app.backend.db_depends import get_db
from slugify import slugify
from typing import Annotated
from app.routers.auth import get_current_user


router = APIRouter(prefix='/products', tags=['products'])


@router.get('/all_products')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(Product).where(True == Product.is_active, Product.stock > 0))
    products = result.all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )

    return products


@router.post('/create_product')
async def create_products(db: Annotated[AsyncSession, Depends(get_db)], create_product: ProductSchema, get_user: dict = Depends(get_current_user)):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(
            name=create_product.name,
            description=create_product.description,
            price=create_product.price,
            image_url=create_product.image_url,
            stock=create_product.stock,
            category_id=create_product.category_id,
            slug=slugify(create_product.name),
            is_active=create_product.is_active,
            supplier_id=get_user.get('id')
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.get('/category/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(category_slug == Category.slug))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )

    subcategories = await db.scalars(select(Category).where(category.id == Category.parent_id))
    categories_and_subcategories = [category.id] + [subcat.id for subcat in subcategories]

    products_category = await db.scalars(select(Product).where(
        Product.category_id.in_(categories_and_subcategories),
        True == Product.is_active,
        Product.stock > 0
    ))

    return products_category.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(product_slug == Product.slug, True == Product.is_active, Product.stock > 0))

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )

    return product


@router.put('/detail_update/{product_slug}')
async def update_products(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, update_product: ProductSchema, get_user: dict = Depends(get_current_user)):
    product = await db.scalar(select(Product).where(product_slug == Product.slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        if get_user.get('id') == get_user.get('supplier_id') or get_user.get('is_admin'):
            await db.execute(update(Product).where(product_slug == Product.slug).values(
                name=update_product.name,
                description=update_product.description,
                price=update_product.price,
                image_url=update_product.image_url,
                stock=update_product.stock,
                category_id=update_product.category_id
            ))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.delete('/delete_product')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int, get_user: dict = Depends(get_current_user)):
    product = await db.scalar(select(Product).where(product_id == Product.id))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        if get_user.get('id') == get_user.get('supplier_id') or get_user.get('is_admin'):
            await db.execute(delete(Product).where(product_id == Product.id))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )