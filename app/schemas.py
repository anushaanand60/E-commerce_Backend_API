from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING="pending"
    CONFIRMED="confirmed"
    SHIPPED="shipped"
    DELIVERED="delivered"
    CANCELLED="cancelled"

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    secret_key: str

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    
    class Config:
        from_attributes=True

class ProductBase(BaseModel):
    name: str
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes=True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    price_at_time: float

    class Config:
        from_attributes=True

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class Order(BaseModel):
    id: int
    user_id: int
    total: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem]=[]

    class Config:
        from_attributes=True

class OrderUpdate(BaseModel):
    status: OrderStatus

class CartItemBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int

    class Config:
        from_attributes=True

class Token(BaseModel):
    access_token: str
    token_type: str="bearer"