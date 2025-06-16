from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models.reviews import Review
from app.models.products import Product
from app.schemas import CreateReview


router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    reviews_all = reviews.all()
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Отзывы не найдены')
    return reviews_all

@router.get('/{product_slug}')
async def products_reviews(
    db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(
        Product.slug == product_slug, Product.is_active == True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_review: CreateReview,
    get_user: Annotated[dict, Depends(get_current_user)]):
        if get_user.get('is_admin') or get_user.get('is_customer') or get_user.get('is_supplier'):
            product = await db.scalar(select(Product).where(
                Product.id == create_review.product_id))
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
            
            await db.execute(insert(Review).values(
                user_id=create_review.user_id,
                product_id=create_review.product_id,
                comment=create_review.comment,
                grade=create_review.grade
            ))
            await db.commit()
            return {'status_code': status.HTTP_200_OK,
                    'detail': 'Отзыв создан'}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='У вас нет доступа')


@router.delete('/{product_slug}')
async def delete_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        product = await db.scalar(select(Product).where(
            Product.slug == product_slug, Product.is_active == True))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
        reviews = await db.execute(select(Review).where(
            Review.product_id == product.id, Review.is_active == True))
        result = await db.execute(reviews)
        reviews_all = result.scalars().all()

        if not reviews_all:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Активные отзывы не найдены')
        deactivate_stmt = (
            update(Review)
            .values(is_active=False)
            .where(Review.product_id == product.id, Review.is_active == True)
        )
        await db.execute(deactivate_stmt)
        await db.commit()

        return {'message': 'Отзыв(-ы) успешно удалены'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='У вас нет доступа')    
