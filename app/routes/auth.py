from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from .. import models, schemas
from ..dependencies import get_db, get_password_hash, verify_password, create_access_token

router=APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session=Depends(get_db)):
    existing_user=db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_pw=get_password_hash(user.password)
    new_user=models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role="customer"
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create user")
    return new_user

@router.post("/register-admin", response_model=schemas.UserResponse)
def register_admin(admin_data: schemas.AdminCreate, db: Session=Depends(get_db)):
    if admin_data.secret_key != "admin123":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid admin secret key"
        )
    existing_user=db.query(models.User).filter((models.User.username == admin_data.username) | (models.User.email == admin_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_pw=get_password_hash(admin_data.password)
    new_user=models.User(username=admin_data.username, email=admin_data.email, hashed_password=hashed_pw, role="admin")
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create admin user")
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session=Depends(get_db)):
    db_user=db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires=timedelta(minutes=30)
    access_token=create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}