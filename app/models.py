from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base=declarative_base()

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password=Column(String, nullable=False)
    role=Column(String, default="customer")
    
    orders=relationship("Order", back_populates="user")
    cart_items=relationship("CartItem", back_populates="user")

class Product(Base):
    __tablename__="products"
    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, index=True)
    price=Column(Float)
    stock=Column(Integer)

class Order(Base):
    __tablename__="orders"
    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey("users.id"))
    total=Column(Float)
    status=Column(String, default="pending")
    created_at=Column(DateTime, default=datetime.utcnow)
    updated_at=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user=relationship("User", back_populates="orders")
    items=relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__="order_items"
    id=Column(Integer, primary_key=True, index=True)
    order_id=Column(Integer, ForeignKey("orders.id"))
    product_id=Column(Integer, ForeignKey("products.id"))
    quantity=Column(Integer, nullable=False)
    price_at_time=Column(Float)

    order=relationship("Order", back_populates="items")
    product=relationship("Product")

class CartItem(Base):
    __tablename__="cart_items"
    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey("users.id"))
    product_id=Column(Integer, ForeignKey("products.id"))
    quantity=Column(Integer, default=1)

    user=relationship("User", back_populates="cart_items")
    product=relationship("Product")