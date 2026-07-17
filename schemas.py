from pydantic import BaseModel, EmailStr,Field
class userdata(BaseModel):
    name: str
    role: str
    
    class Config:
        from_attributes = True

class userCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str
    bio: str | None = None
    role: str

class userResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str  
    bio: str | None = None
    role: str

    class Config:
        from_attributes = True

class store_Create(BaseModel):
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
        
class store_response(store_Create):
    id:int
    user_id:int

class product_Create(BaseModel):
    name: str
    price: float
    quantity: int
    
class product_Response(product_Create):
    id: int
    store_id:int
    
    
class CustomProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    store_id: int
    store_name: str
    store_description: str | None = None
    
class purchaseCreate(BaseModel):
    product_id:int
    quantity:int=Field(default=1,ge=1)
    


    class Config:
        from_attribute=True