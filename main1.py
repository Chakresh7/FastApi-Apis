from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI(title="User Management API", version="1.0.0")

# Pydantic Models
class User(BaseModel):
    name: str
    email: str
    phone: str
    gender: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    gender: str

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    gender: str

# In-memory storage (replace with database in production)
users_db: List[UserResponse] = []

@app.get("/", tags=["Root"])
def home():
    """Welcome endpoint"""
    return {"message": "User Management API", "version": "1.0.0"}

@app.post("/users", response_model=UserResponse, tags=["Users"])
def create_user(user: UserCreate):
    """Create a new user"""
    # Generate unique ID for the user
    user_id = str(uuid.uuid4())
    
    # Create user response object
    new_user = UserResponse(
        id=user_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        gender=user.gender
    )
    
    # Add to storage
    users_db.append(new_user)
    
    return new_user

@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_all_users():
    """Get all users"""
    return users_db

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user_by_id(user_id: str):
    """Get a specific user by ID"""
    for user in users_db:
        if user.id == user_id:
            return user
    
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/count", tags=["Users"])
def get_users_count():
    """Get total number of users"""
    return {"total_users": len(users_db)}