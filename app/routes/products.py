from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import app.crud as crud, app.schemas as schemas
from app.database import SessionLocal
from app.dependencies import get_db, get_current_user, admin_required
from app import models

router=APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.Product])
def read_products(skip: int=Query(0, description="Number of items to skip"), limit: int=Query(100, description="Number of items to return", le=100), search: str=Query(None, description="Search products by name"), min_price: float=Query(None, description="Minimum price filter"), max_price: float=Query(None, description="Maximum price filter"), in_stock: bool=Query(None, description="Filter by stock availability"), db: Session=Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit, search=search, min_price=min_price, max_price=max_price, in_stock=in_stock)

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session=Depends(get_db)):
    product=crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session=Depends(get_db), current_user: models.User=Depends(admin_required)):
    return crud.create_product(db, product)

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, updated: schemas.ProductCreate, db: Session=Depends(get_db),current_user: models.User=Depends(admin_required)):
    product=crud.update_product(db, product_id, updated)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session=Depends(get_db), current_user: models.User=Depends(admin_required)):
    success=crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}

@router.get("/search/{search_term}", response_model=List[schemas.Product])
def search_products(search_term: str, skip: int=Query(0, description="Number of items to skip"), limit: int=Query(100, description="Number of items to return", le=100), db: Session=Depends(get_db)):
    return crud.search_products(db, search_term, skip=skip, limit=limit)

@router.get("/filter/price", response_model=List[schemas.Product])
def filter_products_by_price(min_price: float=Query(None, description="Minimum price"), max_price: float=Query(None, description="Maximum price"), skip: int=Query(0, description="Number of items to skip"), limit: int=Query(100, description="Number of items to return", le=100), db: Session=Depends(get_db)):
    return crud.filter_products_by_price(db, min_price=min_price, max_price=max_price, skip=skip, limit=limit)

@router.get("/filter/stock", response_model=List[schemas.Product])
def filter_products_by_stock(in_stock: bool=Query(True, description="True for in-stock, False for out-of-stock"),skip: int=Query(0, description="Number of items to skip"),limit: int=Query(100, description="Number of items to return", le=100), db: Session=Depends(get_db)):
    return crud.get_products_in_stock(db, in_stock=in_stock, skip=skip, limit=limit)