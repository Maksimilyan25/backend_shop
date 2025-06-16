from fastapi import FastAPI
from app.routers import category, products, auth, permissions, reviews


app = FastAPI()


@app.get('/')
async def welcome() -> dict:
    return {'message': 'приложение'}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(reviews.router)