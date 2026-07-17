from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from Database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    role = Column(String, default="customer", nullable=False)
    
    stores = relationship("Store", back_populates="owner", cascade="all, delete-orphan")
    purchases=relationship("Purchase",back_populates="customer",cascade="all,delete-orphan")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    
    # Store ko User ke sath connect karne ke liye
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="stores")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")


class Product(Base):  
    __tablename__ = "products"
    id = Column(Integer, index=True, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    # Relationship
    store = relationship("Store", back_populates="products")
    purchases=relationship("Purchase",back_populates="product")
    
    
class Purchase(Base):
    __tablename__="purchases"
    id=Column(Integer,index=True,primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False) 
    price_at_purchase = Column(Float, nullable=False) 
    total_amount = Column(Float, nullable=False) 
    purchased_at = Column(DateTime, default=datetime.utcnow)
    
    
    
    customer = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")