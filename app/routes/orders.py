from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import SessionLocal
from app.dependencies import get_db, get_current_user, admin_required
from app.email_service import email_service

router=APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[schemas.Order])
def read_orders(skip: int=0, limit: int=100, db: Session=Depends(get_db), current_user: models.User=Depends(admin_required)):
    orders=db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@router.get("/my-orders", response_model=List[schemas.Order])
def read_my_orders(skip: int=0,limit: int=100, db: Session=Depends(get_db), current_user: models.User=Depends(get_current_user)):
    orders=db.query(models.Order).filter(models.Order.user_id == current_user.id).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session=Depends(get_db), current_user: models.User=Depends(get_current_user)):
    order=db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, background_tasks: BackgroundTasks, db: Session=Depends(get_db), current_user: models.User=Depends(get_current_user)):
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only create orders for yourself") 
    total_amount=0.0
    order_items_data=[]
    for item in order.items:
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
        order_items_data.append({"product": product,"quantity": item.quantity, "price_at_time": product.price})
    db_order=models.Order(user_id=order.user_id, total=total_amount, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item_data in order_items_data:
        product=item_data["product"]
        quantity=item_data["quantity"]
        order_item=models.OrderItem(order_id=db_order.id, product_id=product.id, quantity=quantity, price_at_time=item_data["price_at_time"])
        db.add(order_item)
        product.stock -= quantity
    db.commit()
    db.refresh(db_order)
    user=db.query(models.User).filter(models.User.id == order.user_id).first()
    if user:
        order_email_data={"id": db_order.id, "total": db_order.total, "status": db_order.status, "created_at": db_order.created_at.isoformat(), "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in db_order.items]}
        background_tasks.add_task(email_service.send_order_confirmation, user_email=user.email, username=user.username, order_data=order_email_data)
    return db_order

@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, order_update: schemas.OrderUpdate, background_tasks: BackgroundTasks, db: Session=Depends(get_db), current_user: models.User=Depends(admin_required)):
    db_order=db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    old_status=db_order.status
    db_order.status=order_update.status
    db.commit()
    db.refresh(db_order)
    if old_status != order_update.status:
        user=db.query(models.User).filter(models.User.id == db_order.user_id).first()
        if user:
            order_email_data={
                "id": db_order.id,
                "total": db_order.total,
                "status": db_order.status, "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in db_order.items]}
            background_tasks.add_task(email_service.send_status_update, user_email=user.email, username=user.username, order_data=order_email_data, old_status=old_status, new_status=order_update.status)
    return db_order

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session=Depends(get_db),current_user: models.User=Depends(admin_required)):
    order=db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for order_item in order.items:
        product=db.query(models.Product).filter(models.Product.id == order_item.product_id).first()
        if product:
            product.stock += order_item.quantity
    db.delete(order)
    db.commit()
    return {"detail": "Order deleted and stock restored"}

@router.get("/user/{user_id}", response_model=List[schemas.Order])
def get_user_orders(user_id: int, db: Session=Depends(get_db), current_user: models.User=Depends(admin_required)):
    orders=db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return orders