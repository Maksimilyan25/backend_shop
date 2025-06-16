from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateReview(BaseModel):
    user_id: int
    product_id: int
    comment : str
    grade: int
    comment_date: datetime = datetime.now()


class DeleteReviewSchema(BaseModel):
    review_id: int