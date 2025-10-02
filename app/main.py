from fastapi import FastAPI
from app.models import Base
from app.database import engine
from app.routes import auth, products, orders, cart, admin

app=FastAPI(title="Order Management System")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}
