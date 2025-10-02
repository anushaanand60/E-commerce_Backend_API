from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.crud as crud, app.schemas as schemas
from app.database import SessionLocal
from app.dependencies import get_current_user

router=APIRouter(prefix="/cart", tags=["cart"])

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=list[schemas.CartItem])
def read_cart(user_id: int, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own cart")
    return crud.get_cart(db, user_id)

@router.post("/", response_model=schemas.CartItem)
def add_cart_item(item: schemas.CartItemCreate, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != item.user_id:
        raise HTTPException(status_code=403, detail="Can only add to your own cart")
    product=db.query(crud.models.Product).filter(crud.models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail=f"{product.name} is out of stock")
    if product.stock < item.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {product.stock} {product.name} available. Requested: {item.quantity}"
        )
    existing_item=db.query(crud.models.CartItem).filter(crud.models.CartItem.user_id == item.user_id, crud.models.CartItem.product_id == item.product_id).first()
    if existing_item:
        new_quantity=existing_item.quantity + item.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot add {item.quantity} more. Only {product.stock - existing_item.quantity} available."
            )
    return crud.add_to_cart_with_stock_check(db, item)

@router.delete("/{user_id}/{product_id}")
def remove_cart_item(user_id: int, product_id: int, db: Session=Depends(get_db),current_user=Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only remove from your own cart")
    
    success=crud.remove_from_cart(db, user_id, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"detail": "Item removed from cart"}

@router.post("/{user_id}/checkout", response_model=schemas.Order)
def checkout(user_id: int, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only checkout your own cart")
    cart_items=db.query(crud.models.CartItem).filter(crud.models.CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    for cart_item in cart_items:
        product=db.query(crud.models.Product).filter(crud.models.Product.id == cart_item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}. Available: {product.stock}, In cart: {cart_item.quantity}"
            )
    order=crud.checkout_cart(db, user_id)
    if not order:
        raise HTTPException(status_code=400, detail="Checkout failed")
    return order