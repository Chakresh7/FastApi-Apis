from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="User Update API v1", version="1.0.0")

user_db = {
    1: {"name": "John", "email": "john@example.com", "phone": "1234567890", "gender": "male"},
    2: {"name": "Jane", "email": "jane@example.com", "phone": "0987654321", "gender": "female"},
    3: {"name": "Jim", "email": "jim@example.com", "phone": "1111111111", "gender": "male"},
    4: {"name": "Jill", "email": "jill@example.com", "phone": "2222222222", "gender": "female"},
    5: {"name": "Jack", "email": "jack@example.com", "phone": "3333333333", "gender": "male"},
}

class User(BaseModel):
    name: str
    email: str
    phone: str
    gender: str

@app.get("/", tags=["Root"])
def home():
    """Welcome endpoint"""
    return {"message": "User Update API", "total_users": len(user_db)}

@app.get("/users", tags=["Users"])
def get_all_users():
    """Get all users"""
    return {"users": user_db}

@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int):
    """Get a specific user by ID"""
    if user_id in user_db:
        return {"user_id": user_id, "user": user_db[user_id]}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", tags=["Users"])
def update_user(user_id: int, user: User):
    """Update a user by ID"""
    if user_id in user_db:
        # Store old data for comparison
        old_user = user_db[user_id].copy()
        
        # Update with new data
        user_db[user_id] = user.model_dump()
        
        return {
            "message": "User updated successfully",
            "user_id": user_id,
            "old_data": old_user,
            "new_data": user_db[user_id]
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
print(user_db)

@app.delete("/users/v1/delete/{user_id}", tags=["Users"])
def delete_user(user_id: int):
    """Delete a user by ID"""
    if user_id in user_db:
        del user_db[user_id]
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")