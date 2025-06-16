from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='reviews')
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    product = relationship('Product', back_populates='reviews')
    comment = Column(String, nullable=True)
    comment_date = Column(DateTime, server_default=func.now())
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)
