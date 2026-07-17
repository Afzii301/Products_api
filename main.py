from fastapi import FastAPI, Depends, HTTPException, status
from schemas import product_Create, product_Response, userCreate, userResponse, store_Create,CustomProductResponse,purchaseCreate
from model import User, Product, Store,Purchase
from sqlalchemy.orm import Session
from Database import get_db, engine, Base
from typing import List
from config import hash_password, verify_password, create_access_token, get_user

Base.metadata.create_all(bind=engine)
 
app = FastAPI(
    title="E-Commerce Store API",
    description="""
# 🛍️ E-Commerce Store API

A complete RESTful API for an online shopping platform built with FastAPI.

## Customer Features
- 👤 User Registration & Login
- 🔐 JWT Authentication
- 📦 Browse Products
- 🔍 Search & Filter Products
- 🛒 Add, Update & Remove Cart Items
- ❤️ Wishlist Management
- 📋 Place Orders
- 💳 Secure Checkout
- 📦 Track Order Status

## Admin Features
- 👨‍💼 Admin Authentication
- 📦 Product Management (Create, Update, Delete)
- 🗂️ Category Management
- 📊 Inventory & Stock Management
- 📋 Order Management
- 👥 Customer Management
- 📈 Sales Dashboard

## API Highlights
- ⚡ High Performance with FastAPI
- 📖 Interactive Swagger Documentation
- ✅ Request Validation with Pydantic
- 🔒 Secure REST API
- 🗄️ Database Integration
- 🚀 Scalable and Easy to Maintain

This API is designed for modern e-commerce applications, providing a secure, fast, and reliable backend for online stores.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

def verify_admin(current_user: User = Depends(get_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only admin operation that perform")
    return current_user
  

@app.post("/register", status_code=201, response_model=userResponse)
def create_user(user: userCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if existing_user:
         raise HTTPException(status_code=400, detail="Same Phone number already exist plz change phone number")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password), 
        phone_number=user.phone_number,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login_user/")
def login(name: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == name).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="UNAUTHORIZE password")
    token = {"sub": db_user.name}
    access_token = create_access_token(data=token)
    return {
        "message": "Login successful", 
        "access_token": access_token,
        "Token_Type ": "bearer"
    }


@app.post("/stores", status_code=201)
def create_store(store_data: store_Create, db: Session = Depends(get_db), current_admin: User = Depends(verify_admin)):
    existing_store = db.query(Store).filter(Store.name == store_data.name).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="Store name already exists")
        
    new_store = Store(
        name=store_data.name,
        description=store_data.description,
        user_id=current_admin.id
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@app.post("/stores/{store_id}/products", response_model=CustomProductResponse, status_code=201)
def create_product(store_id: int, produc: product_Create, db: Session = Depends(get_db), current_admin: User = Depends(verify_admin)
):
    store_obj = db.query(Store).filter(Store.id == store_id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Store not found")
        
    if store_obj.user_id != current_admin.id:
        raise HTTPException(status_code=403, detail="You can only add products to your own store")

    db_product = Product(
        **produc.model_dump(),
        store_id=store_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return {
        "id": db_product.id,
        "name": db_product.name,
        "price": db_product.price,
        "quantity": db_product.quantity,
        "store_id": store_obj.id,
        "store_name": store_obj.name,               
        "store_description": store_obj.description   
    }


@app.get("/stores/{store_id}/products", response_model=List[product_Response])
def read_store_products(store_id: int, db: Session = Depends(get_db)):
    store_obj = db.query(Store).filter(Store.id == store_id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Store not found")
    return store_obj.products


@app.get("/products/", response_model=List[product_Response])
def get_all_product(db: Session = Depends(get_db)):
    product_obj = db.query(Product).all()
    return product_obj


@app.put("/products/{product_id}", response_model=product_Response)
def update_product(product_id: int, updated_product: product_Create, db: Session = Depends(get_db), current_admin: User = Depends(verify_admin)):
    productt = db.query(Product).filter(Product.id == product_id).first()
    if productt is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if productt.store.user_id != current_admin.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this product")

    productt.name = updated_product.name
    productt.price = updated_product.price
    productt.quantity = updated_product.quantity

    db.commit()
    db.refresh(productt)
    return productt


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_admin: User = Depends(verify_admin)):
    productt = db.query(Product).filter(Product.id == product_id).first()
    if not productt:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if productt.store.user_id != current_admin.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this product")
    
    product_data = {"id": productt.id, "name": productt.name}
    db.delete(productt)
    db.commit()
    
    return {
        "message": "Product deleted successfully",
        "product": product_data
    }
    
@app.post("/purchases", status_code=status.HTTP_201_CREATED, response_model=None)
def purchase_product(load: purchaseCreate,db: Session = Depends(get_db),current_user: User = Depends(get_user)
):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer buy this product"
        )
    product = db.query(Product).filter(Product.id == load.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Product not found"
        )

    if product.quantity < load.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"check it get_endpoint  many item in quantity"
        )
    total_price = product.price * load.quantity

    try:
        product.quantity -= load.quantity

        new_purchase = Purchase(
            customer_id=current_user.id,    
            product_id=product.id,
            quantity=load.quantity,
            price_at_purchase=product.price,
            total_amount=total_price
        )  

        db.add(new_purchase)
        db.commit() 
        db.refresh(new_purchase)
        
        return {
            "id": new_purchase.id,
            "customer_id": current_user.id,
            "customer_name": current_user.name,
            
            "product_id": product.id,
            "product_name": product.name,
            
            "quantity": new_purchase.quantity,   
            "price_at_purchase": new_purchase.price_at_purchase,
            "total_amount": new_purchase.total_amount,
            "purchased_at": new_purchase.purchased_at,
            
            "store_id": product.store.id,
            "store_name": product.store.name,
            "store_description": product.store.description 
        }
    except Exception as e:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Purchase processing mein koi masla aaya hai. Dobara try karein."
        )
        
