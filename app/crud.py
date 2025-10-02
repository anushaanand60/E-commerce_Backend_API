from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import app.models as models, app.schemas as schemas

def get_products(db: Session, skip: int=0, limit: int=100, search: str=None, min_price: float=None, max_price: float=None, in_stock: bool=None):
    query=db.query(models.Product)
    if search:
        query=query.filter(models.Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query=query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query=query.filter(models.Product.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query=query.filter(models.Product.stock > 0)
        else:
            query=query.filter(models.Product.stock == 0)
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product=models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, updated: schemas.ProductCreate):
    db_product=db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None
    for key, value in updated.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product=db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return False
    db.delete(db_product)
    db.commit()
    return True

def get_orders(db: Session, skip: int=0, limit: int=100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_order_with_stock_management(db: Session, order_data: schemas.OrderCreate):
    """
    Create order with automatic stock management and total calculation
    """
    total_amount=0.0
    order_items_data=[]
    for item in order_data.items:
        product=db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {item.quantity}"
            )
        item_total=product.price * item.quantity
        total_amount += item_total
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "price_at_time": product.price
        })
    db_order=models.Order(
        user_id=order_data.user_id,
        total=total_amount,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item_data in order_items_data:
        product=item_data["product"]
        quantity=item_data["quantity"]
        order_item=models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=quantity,
            price_at_time=item_data["price_at_time"]
        )
        db.add(order_item)
        product.stock -= quantity
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order_with_stock_restore(db: Session, order_id: int):
    """
    Delete order and restore stock
    """
    db_order=db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        return False
    for order_item in db_order.items:
        product=db.query(models.Product).filter(models.Product.id == order_item.product_id).first()
        if product:
            product.stock += order_item.quantity
    db.delete(db_order)
    db.commit()
    return True

def get_cart(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def add_to_cart_with_stock_check(db: Session, item: schemas.CartItemCreate):
    """
    Add to cart with stock validation
    """
    product=db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail=f"{product.name} is out of stock")
    db_item=db.query(models.CartItem).filter(models.CartItem.user_id == item.user_id, models.CartItem.product_id == item.product_id).first()
    if db_item:
        new_quantity=db_item.quantity + item.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot add {item.quantity} more. Only {product.stock - db_item.quantity} available."
            )
        db_item.quantity=new_quantity
    else:
        if item.quantity > product.stock:
            raise HTTPException(
                status_code=400, 
                detail=f"Only {product.stock} {product.name} available. Requested: {item.quantity}"
            )
        db_item=models.CartItem(**item.dict())
        db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def remove_from_cart(db: Session, user_id: int, product_id: int):
    db_item=db.query(models.CartItem).filter(models.CartItem.user_id == user_id,models.CartItem.product_id == product_id).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True

def checkout_cart(db: Session, user_id: int):
    cart_items=db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total=0.0
    order_items_data=[]
    for item in cart_items:
        product=db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}. Available: {product.stock}, In cart: {item.quantity}"
            )
        item_total=product.price * item.quantity
        total += item_total
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "price_at_time": product.price,
            "cart_item": item
        })
    new_order=models.Order(user_id=user_id, total=total, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item_data in order_items_data:
        product=item_data["product"]
        quantity=item_data["quantity"]
        cart_item=item_data["cart_item"]
        order_item=models.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price_at_time=item_data["price_at_time"]
        )
        db.add(order_item)
        product.stock -= quantity
        db.delete(cart_item)
    db.commit()
    db.refresh(new_order)
    return new_order

def search_products(db: Session, search_term: str, skip: int=0, limit: int=100):
    """Search products by name"""
    return db.query(models.Product).filter(models.Product.name.ilike(f"%{search_term}%")).offset(skip).limit(limit).all()

def filter_products_by_price(db: Session, min_price: float=None, max_price: float=None, skip: int=0, limit: int=100):
    """Filter products by price range"""
    query=db.query(models.Product)
    if min_price is not None:
        query=query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query=query.filter(models.Product.price <= max_price)
    return query.offset(skip).limit(limit).all()

def get_products_in_stock(db: Session, in_stock: bool=True, skip: int=0, limit: int=100):
    """Get products based on stock availability"""
    query=db.query(models.Product)
    if in_stock:
        query=query.filter(models.Product.stock > 0)
    else:
        query=query.filter(models.Product.stock == 0)
    return query.offset(skip).limit(limit).all()