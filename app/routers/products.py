from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from slugify import slugify

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas import CreateProduct


router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product).where(
            Product.is_active == True, Product.stock > 0))
    all_products = products.all()
    if not all_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Нет товаров')
    return all_products


@router.post('/', status_code=status.HTTP_200_OK)
async def create_product(
     db: Annotated[AsyncSession, Depends(get_db)],
     create_product: CreateProduct):
    category = await db.scalar(select(Category).where(
        Category.id == create_product.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена')

    await db.execute(insert(Product).values(
        name=create_product.name,
        slug=slugify(create_product.name),
        description=create_product.description,
        price=create_product.price,
        image_url=create_product.image_url,
        stock=create_product.stock,
        category_id=create_product.category,
        rating=0.0))
    await db.commit()

    return {'staus_code': status.HTTP_201_CREATED,
            'detail': 'Продукт создан!'}


@router.get('/{category_slug}')
async def product_by_category(
     db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(
        Category.slug == category_slug))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена')
    subcategories = await db.scalars(
        select(Category).where(Category.parent_id == category.id))
    category_subcategory = [category.id] + [i.id for i in subcategories.all()]
    products_category = await db.scalars(
        select(Product).where(
            Product.category_id.in_(category_subcategory),
            Product.is_active == True, Product.stock > 0))
    return products_category.all()


@router.get('/detail/{product_slug}')
async def product_detail(
     db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    detail_product = await db.scalar(select(Product).where(
        Product.slug == product_slug,
        Product.is_active == True,
        Product.stock > 0))
    if detail_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    return detail_product


@router.put('/{product_slug}')
async def update_product(
     db: Annotated[AsyncSession, Depends(get_db)],
     product_slug: str, update_product: CreateProduct):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    category = await db.scalar(select(Category).where(
        Category.id == update_product.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена!')

    product.name = update_product.name
    product.description = update_product.description
    product.price = update_product.price
    product.image_url = update_product.image_url
    product.slug = slugify(update_product.name)
    product.stock = update_product.stock
    product.category_id = update_product.category
    await db.commit()

    return {'status_code': status.HTTP_200_OK,
            'detail': 'Продукт успешно обновлен!'}


@router.delete('/{product_slug}')
async def delete_product(
     db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(
        Product.slug == product_slug, Product.is_active == True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Продукт не найден')
    product.is_active = False
    await db.commit()

    return {'status_code': status.HTTP_200_OK,
            'detail': 'Продукт удален'}
