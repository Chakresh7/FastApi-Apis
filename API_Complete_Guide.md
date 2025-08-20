# 🚀 Complete REST API Guide with FastAPI

## Table of Contents
- [🎯 Introduction](#-introduction)
- [🔧 HTTP Methods Deep Dive](#-http-methods-deep-dive)
- [🏗️ Route Design Principles](#️-route-design-principles)
- [📊 HTTP Status Codes](#-http-status-codes)
- [📋 Data Models & Validation](#-data-models--validation)
- [📚 API Documentation](#-api-documentation)
- [⭐ Best Practices](#-best-practices)
- [🌍 Real-World Examples](#-real-world-examples)
- [🔄 Common Patterns](#-common-patterns)
- [💡 Advanced Concepts](#-advanced-concepts)
- [🎓 Summary](#-summary)

---

## 🎯 Introduction

**REST (Representational State Transfer)** is an architectural style for designing web APIs that uses standard HTTP methods to perform operations on resources.

### Core REST Principles
- **📍 Resource-based**: Everything is a resource with a unique URL
- **🔄 Stateless**: Each request contains all needed information
- **🎯 Standard Methods**: Use HTTP verbs (GET, POST, PUT, DELETE)
- **📝 JSON Format**: Standard data exchange format
- **🔗 HATEOAS**: Hypermedia as the Engine of Application State

### Why REST APIs Matter
- **🌐 Universal**: Works across all platforms and languages
- **📱 Scalable**: Easy to scale and maintain
- **🔧 Simple**: Easy to understand and implement
- **📖 Self-documenting**: URLs describe the resources

---

## 🔧 HTTP Methods Deep Dive

### 📥 GET - Retrieve Data

**Purpose**: Fetch data without modifying anything

```python
from fastapi import FastAPI, HTTPException
from typing import List, Optional

app = FastAPI(title="Complete API Guide", version="2.0.0")

# Sample database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"}
}

@app.get("/users", tags=["Users"])
def get_all_users(
    role: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Get all users with optional filtering and pagination
    
    - **role**: Filter by user role (admin/user)
    - **limit**: Number of users to return (default: 10)
    - **offset**: Number of users to skip (default: 0)
    """
    users = list(users_db.values())
    
    # Filter by role if provided
    if role:
        users = [u for u in users if u.get('role') == role]
    
    # Pagination
    paginated_users = users[offset:offset + limit]
    
    return {
        "users": paginated_users,
        "total": len(users),
        "limit": limit,
        "offset": offset
    }

@app.get("/users/{user_id}", tags=["Users"])
def get_user_by_id(user_id: int):
    """Get a specific user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404, 
            detail=f"User with ID {user_id} not found"
        )
    return {"user": users_db[user_id]}
```

**GET Characteristics:**
- ✅ **Safe**: Doesn't modify server state
- ✅ **Idempotent**: Same result every time
- ✅ **Cacheable**: Results can be cached
- 📊 **Status Code**: 200 OK, 404 Not Found

### 📤 POST - Create New Resource

**Purpose**: Create new resources on the server

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: str

@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(user: UserCreate):
    """
    Create a new user
    
    - **name**: User's full name
    - **email**: Valid email address
    - **role**: User role (admin/user, defaults to user)
    """
    # Generate new ID
    new_id = max(users_db.keys()) + 1 if users_db else 1
    
    # Create user data
    user_data = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": datetime.now().isoformat()
    }
    
    # Store in database
    users_db[new_id] = user_data
    
    return user_data

# Bulk creation example
@app.post("/users/bulk", tags=["Users"])
def create_users_bulk(users: List[UserCreate]):
    """Create multiple users at once"""
    created_users = []
    
    for user in users:
        new_id = max(users_db.keys()) + 1 if users_db else 1
        user_data = {
            "id": new_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": datetime.now().isoformat()
        }
        users_db[new_id] = user_data
        created_users.append(user_data)
    
    return {
        "message": f"Created {len(created_users)} users",
        "users": created_users
    }
```

**POST Characteristics:**
- ❌ **Not Safe**: Modifies server state
- ❌ **Not Idempotent**: Creates new resource each time
- 📊 **Status Code**: 201 Created, 400 Bad Request

### 🔄 PUT - Update/Replace Resource

**Purpose**: Update entire resource or create if doesn't exist

```python
@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user: UserCreate):
    """
    Update entire user resource (replace all fields)
    
    If user doesn't exist, creates a new one (true REST behavior)
    """
    old_user = users_db.get(user_id)
    
    # Create new user data
    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": old_user.get("created_at") if old_user else datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    users_db[user_id] = user_data
    
    if old_user:
        return {
            "message": "User updated successfully",
            "user": user_data,
            "previous_data": old_user
        }
    else:
        return {
            "message": "User created successfully",
            "user": user_data
        }
```

**PUT Characteristics:**
- ❌ **Not Safe**: Modifies server state
- ✅ **Idempotent**: Same result when repeated
- 🔄 **Replaces**: Entire resource is replaced
- 📊 **Status Code**: 200 OK, 201 Created, 404 Not Found

### 🩹 PATCH - Partial Update

**Purpose**: Update only specific fields of a resource

```python
from typing import Optional

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

@app.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def partial_update_user(user_id: int, user_updates: UserUpdate):
    """
    Partially update user (only provided fields)
    
    - Only updates fields that are provided
    - Leaves other fields unchanged
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_user = users_db[user_id].copy()
    update_data = user_updates.model_dump(exclude_unset=True)
    
    # Update only provided fields
    for field, value in update_data.items():
        current_user[field] = value
    
    current_user["updated_at"] = datetime.now().isoformat()
    users_db[user_id] = current_user
    
    return {
        "message": "User partially updated",
        "user": current_user,
        "updated_fields": list(update_data.keys())
    }
```

**PATCH Characteristics:**
- ❌ **Not Safe**: Modifies server state
- ⚠️ **May not be Idempotent**: Depends on implementation
- 🎯 **Selective**: Updates only specified fields
- 📊 **Status Code**: 200 OK, 404 Not Found

### 🗑️ DELETE - Remove Resource

**Purpose**: Remove resources from the server

```python
@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int):
    """Delete a user by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = users_db.pop(user_id)
    
    return {
        "message": "User deleted successfully",
        "deleted_user": deleted_user
    }

# Soft delete example
@app.delete("/users/{user_id}/soft", tags=["Users"])
def soft_delete_user(user_id: int):
    """Soft delete - mark as deleted but keep data"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id]["deleted_at"] = datetime.now().isoformat()
    users_db[user_id]["is_deleted"] = True
    
    return {"message": "User soft deleted", "user": users_db[user_id]}

# Bulk delete example
@app.delete("/users/bulk", tags=["Users"])
def delete_users_bulk(user_ids: List[int]):
    """Delete multiple users"""
    deleted_users = []
    not_found_ids = []
    
    for user_id in user_ids:
        if user_id in users_db:
            deleted_users.append(users_db.pop(user_id))
        else:
            not_found_ids.append(user_id)
    
    return {
        "deleted_count": len(deleted_users),
        "deleted_users": deleted_users,
        "not_found_ids": not_found_ids
    }
```

**DELETE Characteristics:**
- ❌ **Not Safe**: Modifies server state
- ✅ **Idempotent**: Same result when repeated
- 🗑️ **Removes**: Resource is deleted
- 📊 **Status Code**: 200 OK, 204 No Content, 404 Not Found

---

## 🏗️ Route Design Principles

### 1. 📝 Use Nouns, Not Verbs

#### ✅ **Excellent Route Design**
```python
# Resource-based URLs (nouns only)
GET    /users                    # Get all users
GET    /users/123                # Get user 123
POST   /users                    # Create new user
PUT    /users/123                # Update user 123
PATCH  /users/123                # Partially update user 123
DELETE /users/123                # Delete user 123

# Nested resources
GET    /users/123/orders         # Get orders for user 123
POST   /users/123/orders         # Create order for user 123
GET    /users/123/orders/456     # Get specific order
```

#### ❌ **Poor Route Design**
```python
# Verb-based URLs (avoid these)
GET    /getUsers                 # Don't use verbs
POST   /createUser               # Action in URL
PUT    /updateUser/123           # Mixed conventions
DELETE /deleteUser/123           # Redundant action
GET    /user/123/getOrders       # Too many verbs
```

### 2. 🔗 Resource Hierarchy

```python
# E-commerce example with proper hierarchy
@app.get("/categories", tags=["Categories"])
def get_categories(): pass

@app.get("/categories/{category_id}/products", tags=["Products"])
def get_products_in_category(category_id: int): pass

@app.get("/products/{product_id}", tags=["Products"])  
def get_product(product_id: int): pass

@app.get("/products/{product_id}/reviews", tags=["Reviews"])
def get_product_reviews(product_id: int): pass

@app.get("/users/{user_id}/cart", tags=["Cart"])
def get_user_cart(user_id: int): pass

@app.post("/users/{user_id}/cart/items", tags=["Cart"])
def add_to_cart(user_id: int, item: CartItem): pass
```

### 3. 🔍 Query Parameters for Filtering

```python
@app.get("/products", tags=["Products"])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "name",
    order: str = "asc",
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None
):
    """
    Advanced product filtering and search
    
    Query examples:
    - /products?category=electronics&min_price=100&max_price=500
    - /products?search=laptop&sort_by=price&order=desc
    - /products?page=2&limit=10
    """
    # Implementation with all filters
    pass
```

### 4. 🏷️ Consistent Naming

```python
# ✅ Consistent plural nouns
/users          # Not /user
/products       # Not /product  
/orders         # Not /order
/categories     # Not /category

# ✅ Consistent casing (kebab-case for URLs)
/product-categories     # Not /productCategories or /product_categories
/user-preferences       # Not /userPreferences
/order-history         # Not /orderHistory
```

---

## 📊 HTTP Status Codes

### 2️⃣xx Success Codes

```python
from fastapi import status

@app.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    """200 OK - Request successful"""
    return users_db

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """201 Created - Resource created successfully"""
    # Creation logic
    return new_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """204 No Content - Successful deletion, no content to return"""
    # Deletion logic
    return None  # FastAPI will return empty response
```

### 4️⃣xx Client Error Codes

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Proper error handling with appropriate status codes"""
    
    # 400 Bad Request - Invalid input
    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="User ID must be a positive integer"
        )
    
    # 404 Not Found - Resource doesn't exist
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    
    return users_db[user_id]

@app.post("/users")
def create_user(user: UserCreate):
    """422 Unprocessable Entity - Validation errors"""
    # FastAPI automatically returns 422 for Pydantic validation errors
    
    # Custom business logic validation
    if user.email in [u.get('email') for u in users_db.values()]:
        raise HTTPException(
            status_code=422,
            detail="Email already exists"
        )
    
    # Creation logic
    pass
```

### 5️⃣xx Server Error Codes

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Handle server errors gracefully"""
    try:
        # Some operation that might fail
        result = complex_database_operation(user_id)
        return result
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

## 📋 Data Models & Validation

### 🎯 Advanced Pydantic Models

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., ge=13, le=120, description="User age (13-120)")
    role: UserRole = Field(UserRole.USER, description="User role")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True  # For SQLAlchemy models

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    role: Optional[UserRole] = None

# Nested models for complex data
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')
    country: str = "US"

class UserProfile(UserResponse):
    addresses: List[Address] = []
    preferences: dict = {}
    last_login: Optional[datetime] = None
```

### 🔄 Model Usage Examples

```python
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    """Create user with comprehensive validation"""
    # Hash password (in real app)
    hashed_password = hash_password(user.password)
    
    user_data = {
        "id": generate_id(),
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "role": user.role,
        "password_hash": hashed_password,
        "created_at": datetime.now(),
        "is_active": True
    }
    
    users_db[user_data["id"]] = user_data
    return user_data

@app.get("/users/{user_id}/profile", response_model=UserProfile)
def get_user_profile(user_id: int):
    """Get complete user profile with nested data"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    # Add addresses and preferences from other tables
    user["addresses"] = get_user_addresses(user_id)
    user["preferences"] = get_user_preferences(user_id)
    
    return user
```

---

## 📚 API Documentation

### 🎨 Enhanced FastAPI Documentation

```python
from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Complete User Management API",
    description="""
    ## User Management System
    
    This API provides comprehensive user management functionality including:
    
    * **Users**: Create, read, update, and delete users
    * **Authentication**: Login and token management
    * **Profiles**: Manage user profiles and preferences
    * **Admin**: Administrative functions
    
    ### Authentication
    Most endpoints require authentication. Use the `/auth/login` endpoint to get a token.
    
    ### Rate Limiting
    API calls are limited to 1000 requests per hour per user.
    """,
    version="2.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="User Management API",
        version="2.0.0",
        description="Complete user management system",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Detailed endpoint documentation
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    tags=["Users"],
    summary="Create a new user",
    description="Create a new user account with validation",
    response_description="The created user information",
    responses={
        201: {"description": "User created successfully"},
        422: {"description": "Validation error"},
        409: {"description": "Email already exists"}
    }
)
def create_user(user: UserCreate):
    """
    Create a new user with the following information:
    
    - **name**: User's full name (2-100 characters)
    - **email**: Valid email address (must be unique)
    - **age**: User's age (13-120 years old)
    - **role**: User role (admin/user/moderator)
    - **password**: Secure password (min 8 chars, must include upper, lower, digit)
    
    Returns the created user information (excluding password).
    """
    pass
```

---

## ⭐ Best Practices

### 1. 🔐 Security Best Practices

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return get_user(user_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Protected endpoint
@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user's information"""
    return current_user

# Admin-only endpoint
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.delete("/users/{user_id}")
def delete_user_admin(
    user_id: int,
    admin_user: dict = Depends(require_admin)
):
    """Admin-only: Delete any user"""
    pass
```

### 2. 📄 Pagination & Filtering

```python
from typing import Optional

class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ):
        self.page = max(1, page)
        self.limit = min(100, max(1, limit))  # Max 100 items per page
        self.sort_by = sort_by
        self.order = order
        self.offset = (self.page - 1) * self.limit

def get_pagination_params(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc"
) -> PaginationParams:
    return PaginationParams(page, limit, sort_by, order)

@app.get("/users")
def get_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
):
    """Get users with advanced filtering and pagination"""
    
    # Start with all users
    users = list(users_db.values())
    
    # Apply filters
    if search:
        users = [u for u in users if search.lower() in u.get('name', '').lower()]
    
    if role:
        users = [u for u in users if u.get('role') == role]
    
    if is_active is not None:
        users = [u for u in users if u.get('is_active') == is_active]
    
    # Sort
    reverse = pagination.order == "desc"
    users.sort(key=lambda x: x.get(pagination.sort_by, ''), reverse=reverse)
    
    # Paginate
    total = len(users)
    paginated_users = users[pagination.offset:pagination.offset + pagination.limit]
    
    return {
        "users": paginated_users,
        "pagination": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total": total,
            "pages": (total + pagination.limit - 1) // pagination.limit,
            "has_next": pagination.offset + pagination.limit < total,
            "has_prev": pagination.page > 1
        }
    }
```

### 3. 🚨 Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

# Custom exception classes
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")

class DuplicateEmailError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists")

# Global exception handlers
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "User not found",
            "user_id": exc.user_id,
            "message": str(exc)
        }
    )

@app.exception_handler(DuplicateEmailError)
async def duplicate_email_handler(request: Request, exc: DuplicateEmailError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Duplicate email",
            "email": exc.email,
            "message": str(exc)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "body": exc.body
        }
    )

# Usage in endpoints
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users_db:
        raise UserNotFoundError(user_id)
    return users_db[user_id]
```

---

## 🌍 Real-World Examples

### 🛒 E-commerce API Complete Example

```python
from enum import Enum
from decimal import Decimal
from typing import List, Optional

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"

# Models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    category: ProductCategory
    stock_quantity: int
    is_active: bool = True

class CartItem(BaseModel):
    product_id: int
    quantity: int = 1

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: Decimal  # Price at time of order

class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

# Sample data
products_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "category": "electronics", "stock": 10},
    2: {"id": 2, "name": "T-Shirt", "price": 29.99, "category": "clothing", "stock": 50},
}

carts_db = {}  # user_id -> list of cart items
orders_db = {}  # order_id -> order data

# Products API
@app.get("/products", tags=["Products"])
def get_products(
    category: Optional[ProductCategory] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get products with filtering"""
    products = list(products_db.values())
    
    # Apply filters
    if category:
        products = [p for p in products if p["category"] == category]
    if min_price:
        products = [p for p in products if p["price"] >= min_price]
    if max_price:
        products = [p for p in products if p["price"] <= max_price]
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    
    # Pagination
    offset = (page - 1) * limit
    paginated = products[offset:offset + limit]
    
    return {
        "products": paginated,
        "total": len(products),
        "page": page,
        "limit": limit
    }

@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    """Get product details"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

# Shopping Cart API
@app.get("/users/{user_id}/cart", tags=["Cart"])
def get_user_cart(user_id: int):
    """Get user's shopping cart"""
    cart_items = carts_db.get(user_id, [])
    
    # Enrich with product details
    enriched_cart = []
    total_amount = 0
    
    for item in cart_items:
        product = products_db.get(item["product_id"])
        if product:
            item_total = product["price"] * item["quantity"]
            enriched_cart.append({
                "product": product,
                "quantity": item["quantity"],
                "item_total": item_total
            })
            total_amount += item_total
    
    return {
        "user_id": user_id,
        "items": enriched_cart,
        "total_items": sum(item["quantity"] for item in cart_items),
        "total_amount": total_amount
    }

@app.post("/users/{user_id}/cart/items", tags=["Cart"])
def add_to_cart(user_id: int, cart_item: CartItem):
    """Add item to cart"""
    # Validate product exists
    if cart_item.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock
    product = products_db[cart_item.product_id]
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Initialize cart if doesn't exist
    if user_id not in carts_db:
        carts_db[user_id] = []
    
    # Check if item already in cart
    existing_item = next(
        (item for item in carts_db[user_id] if item["product_id"] == cart_item.product_id),
        None
    )
    
    if existing_item:
        existing_item["quantity"] += cart_item.quantity
    else:
        carts_db[user_id].append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        })
    
    return {"message": "Item added to cart", "cart": carts_db[user_id]}

@app.put("/users/{user_id}/cart/items/{product_id}", tags=["Cart"])
def update_cart_item(user_id: int, product_id: int, quantity: int):
    """Update cart item quantity"""
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = next(
        (item for item in carts_db[user_id] if item["product_id"] == product_id),
        None
    )
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    if quantity <= 0:
        carts_db[user_id].remove(cart_item)
        return {"message": "Item removed from cart"}
    else:
        cart_item["quantity"] = quantity
        return {"message": "Cart item updated", "item": cart_item}

@app.delete("/users/{user_id}/cart/items/{product_id}", tags=["Cart"])
def remove_from_cart(user_id: int, product_id: int):
    """Remove item from cart"""
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = next(
        (item for item in carts_db[user_id] if item["product_id"] == product_id),
        None
    )
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    carts_db[user_id].remove(cart_item)
    return {"message": "Item removed from cart"}

# Orders API
@app.post("/orders", tags=["Orders"])
def create_order(user_id: int):
    """Create order from user's cart"""
    if user_id not in carts_db or not carts_db[user_id]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart_items = carts_db[user_id]
    order_items = []
    total_amount = 0
    
    # Process each cart item
    for cart_item in cart_items:
        product = products_db.get(cart_item["product_id"])
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock"] < cart_item["quantity"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for {product['name']}"
            )
        
        # Create order item
        item_total = product["price"] * cart_item["quantity"]
        order_items.append({
            "product_id": cart_item["product_id"],
            "quantity": cart_item["quantity"],
            "price": product["price"]
        })
        total_amount += item_total
        
        # Update stock
        products_db[cart_item["product_id"]]["stock"] -= cart_item["quantity"]
    
    # Create order
    order_id = len(orders_db) + 1
    order = {
        "id": order_id,
        "user_id": user_id,
        "items": order_items,
        "total_amount": total_amount,
        "status": OrderStatus.PENDING,
        "created_at": datetime.now().isoformat()
    }
    
    orders_db[order_id] = order
    
    # Clear cart
    carts_db[user_id] = []
    
    return {"message": "Order created successfully", "order": order}

@app.get("/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int):
    """Get order details"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Enrich with product details
    enriched_items = []
    for item in order["items"]:
        product = products_db.get(item["product_id"])
        if product:
            enriched_items.append({
                "product": product,
                "quantity": item["quantity"],
                "price": item["price"],
                "total": item["price"] * item["quantity"]
            })
    
    return {
        **order,
        "items": enriched_items
    }

@app.patch("/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, status: OrderStatus):
    """Update order status"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    old_status = order["status"]
    order["status"] = status
    order["updated_at"] = datetime.now().isoformat()
    
    return {
        "message": f"Order status updated from {old_status} to {status}",
        "order": order
    }

@app.get("/users/{user_id}/orders", tags=["Orders"])
def get_user_orders(user_id: int):
    """Get all orders for a user"""
    user_orders = [order for order in orders_db.values() if order["user_id"] == user_id]
    return {
        "user_id": user_id,
        "orders": user_orders,
        "total_orders": len(user_orders)
    }
```

### 📚 Blog API Complete Example

```python
from typing import List, Optional
from datetime import datetime

# Models
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Post(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    tags: List[str] = []
    status: PostStatus = PostStatus.DRAFT

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    excerpt: Optional[str]
    tags: List[str]
    status: PostStatus
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    view_count: int = 0

class Comment(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    content: str
    author_id: int
    author_name: str
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime]

# Sample data
posts_db = {}
comments_db = {}

# Posts API
@app.get("/posts", tags=["Posts"])
def get_posts(
    status: Optional[PostStatus] = None,
    author_id: Optional[int] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Get posts with advanced filtering"""
    posts = list(posts_db.values())
    
    # Filter by status (default to published for public access)
    if status:
        posts = [p for p in posts if p["status"] == status]
    else:
        posts = [p for p in posts if p["status"] == PostStatus.PUBLISHED]
    
    # Filter by author
    if author_id:
        posts = [p for p in posts if p["author_id"] == author_id]
    
    # Filter by tags
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        posts = [p for p in posts if any(tag in p.get("tags", []) for tag in tag_list)]
    
    # Search in title and content
    if search:
        search_lower = search.lower()
        posts = [
            p for p in posts 
            if search_lower in p["title"].lower() or search_lower in p["content"].lower()
        ]
    
    # Sort
    reverse = order == "desc"
    posts.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
    
    # Pagination
    offset = (page - 1) * limit
    paginated = posts[offset:offset + limit]
    
    return {
        "posts": paginated,
        "total": len(posts),
        "page": page,
        "limit": limit,
        "pages": (len(posts) + limit - 1) // limit
    }

@app.get("/posts/{post_id}", tags=["Posts"])
def get_post(post_id: int):
    """Get single post and increment view count"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts_db[post_id]
    
    # Increment view count
    post["view_count"] = post.get("view_count", 0) + 1
    
    return post

@app.post("/posts", tags=["Posts"])
def create_post(post: Post, current_user: dict = Depends(get_current_user)):
    """Create new blog post"""
    post_id = len(posts_db) + 1
    
    post_data = {
        "id": post_id,
        "title": post.title,
        "content": post.content,
        "excerpt": post.excerpt or post.content[:200] + "...",
        "tags": post.tags,
        "status": post.status,
        "author_id": current_user["id"],
        "author_name": current_user["name"],
        "created_at": datetime.now(),
        "view_count": 0
    }
    
    if post.status == PostStatus.PUBLISHED:
        post_data["published_at"] = datetime.now()
    
    posts_db[post_id] = post_data
    return post_data

@app.put("/posts/{post_id}", tags=["Posts"])
def update_post(
    post_id: int, 
    post: Post, 
    current_user: dict = Depends(get_current_user)
):
    """Update blog post (author only)"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_post = posts_db[post_id]
    
    # Check if user is author or admin
    if existing_post["author_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    # Update post
    existing_post.update({
        "title": post.title,
        "content": post.content,
        "excerpt": post.excerpt or post.content[:200] + "...",
        "tags": post.tags,
        "status": post.status,
        "updated_at": datetime.now()
    })
    
    # Set published_at if status changed to published
    if post.status == PostStatus.PUBLISHED and not existing_post.get("published_at"):
        existing_post["published_at"] = datetime.now()
    
    return existing_post

@app.delete("/posts/{post_id}", tags=["Posts"])
def delete_post(
    post_id: int, 
    current_user: dict = Depends(get_current_user)
):
    """Delete blog post (author or admin only)"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts_db[post_id]
    
    # Check permissions
    if post["author_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    deleted_post = posts_db.pop(post_id)
    
    # Also delete associated comments
    post_comments = [c_id for c_id, c in comments_db.items() if c["post_id"] == post_id]
    for comment_id in post_comments:
        del comments_db[comment_id]
    
    return {
        "message": "Post deleted successfully",
        "deleted_post": deleted_post,
        "deleted_comments": len(post_comments)
    }

# Comments API
@app.get("/posts/{post_id}/comments", tags=["Comments"])
def get_post_comments(post_id: int, page: int = 1, limit: int = 20):
    """Get comments for a post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_comments = [c for c in comments_db.values() if c["post_id"] == post_id]
    post_comments.sort(key=lambda x: x["created_at"])
    
    # Pagination
    offset = (page - 1) * limit
    paginated = post_comments[offset:offset + limit]
    
    return {
        "comments": paginated,
        "total": len(post_comments),
        "page": page,
        "limit": limit
    }

@app.post("/posts/{post_id}/comments", tags=["Comments"])
def create_comment(
    post_id: int, 
    comment: Comment, 
    current_user: dict = Depends(get_current_user)
):
    """Add comment to post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_id = len(comments_db) + 1
    
    comment_data = {
        "id": comment_id,
        "content": comment.content,
        "author_id": current_user["id"],
        "author_name": current_user["name"],
        "post_id": post_id,
        "created_at": datetime.now()
    }
    
    comments_db[comment_id] = comment_data
    return comment_data

@app.put("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
def update_comment(
    post_id: int,
    comment_id: int,
    comment: Comment,
    current_user: dict = Depends(get_current_user)
):
    """Update comment (author only)"""
    if comment_id not in comments_db:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    existing_comment = comments_db[comment_id]
    
    # Check if comment belongs to the post
    if existing_comment["post_id"] != post_id:
        raise HTTPException(status_code=404, detail="Comment not found for this post")
    
    # Check if user is comment author
    if existing_comment["author_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    existing_comment.update({
        "content": comment.content,
        "updated_at": datetime.now()
    })
    
    return existing_comment

@app.delete("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete comment (author or admin only)"""
    if comment_id not in comments_db:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment = comments_db[comment_id]
    
    # Check if comment belongs to the post
    if comment["post_id"] != post_id:
        raise HTTPException(status_code=404, detail="Comment not found for this post")
    
    # Check permissions
    if comment["author_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    deleted_comment = comments_db.pop(comment_id)
    return {"message": "Comment deleted successfully", "deleted_comment": deleted_comment}

# Tags API
@app.get("/tags", tags=["Tags"])
def get_popular_tags(limit: int = 20):
    """Get most popular tags"""
    tag_counts = {}
    
    for post in posts_db.values():
        if post["status"] == PostStatus.PUBLISHED:
            for tag in post.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort by count and limit
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        "tags": [{"name": tag, "count": count} for tag, count in popular_tags],
        "total_unique_tags": len(tag_counts)
    }

@app.get("/tags/{tag_name}/posts", tags=["Tags"])
def get_posts_by_tag(tag_name: str, page: int = 1, limit: int = 10):
    """Get posts with specific tag"""
    tagged_posts = [
        p for p in posts_db.values() 
        if p["status"] == PostStatus.PUBLISHED and tag_name in p.get("tags", [])
    ]
    
    # Sort by creation date (newest first)
    tagged_posts.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Pagination
    offset = (page - 1) * limit
    paginated = tagged_posts[offset:offset + limit]
    
    return {
        "tag": tag_name,
        "posts": paginated,
        "total": len(tagged_posts),
        "page": page,
        "limit": limit
    }
```

---

## 🔄 Common Patterns

### 1. 🔍 Search & Filtering

```python
@app.get("/search")
def global_search(
    q: str,  # Search query
    type: Optional[str] = None,  # users, posts, products
    page: int = 1,
    limit: int = 10
):
    """Global search across all resources"""
    results = {"users": [], "posts": [], "products": []}
    
    if not type or type == "users":
        # Search users
        matching_users = [
            u for u in users_db.values()
            if q.lower() in u["name"].lower() or q.lower() in u["email"].lower()
        ]
        results["users"] = matching_users[:limit]
    
    if not type or type == "posts":
        # Search posts
        matching_posts = [
            p for p in posts_db.values()
            if q.lower() in p["title"].lower() or q.lower() in p["content"].lower()
        ]
        results["posts"] = matching_posts[:limit]
    
    if not type or type == "products":
        # Search products
        matching_products = [
            p for p in products_db.values()
            if q.lower() in p["name"].lower() or q.lower() in p["description"].lower()
        ]
        results["products"] = matching_products[:limit]
    
    return {
        "query": q,
        "results": results,
        "total_results": sum(len(v) for v in results.values())
    }
```

### 2. 📊 Analytics & Reporting

```python
@app.get("/analytics/dashboard", tags=["Analytics"])
def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    """Get dashboard analytics (admin only)"""
    
    # User statistics
    total_users = len(users_db)
    active_users = len([u for u in users_db.values() if u.get("is_active", True)])
    
    # Post statistics
    total_posts = len(posts_db)
    published_posts = len([p for p in posts_db.values() if p["status"] == "published"])
    draft_posts = len([p for p in posts_db.values() if p["status"] == "draft"])
    
    # Order statistics (if e-commerce)
    total_orders = len(orders_db) if 'orders_db' in globals() else 0
    pending_orders = len([o for o in orders_db.values() if o["status"] == "pending"]) if 'orders_db' in globals() else 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "posts": {
            "total": total_posts,
            "published": published_posts,
            "drafts": draft_posts
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders
        },
        "generated_at": datetime.now().isoformat()
    }

@app.get("/analytics/users/activity", tags=["Analytics"])
def get_user_activity(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get user activity analytics"""
    # In a real app, this would query activity logs
    return {
        "daily_active_users": 150,
        "weekly_active_users": 500,
        "monthly_active_users": 1200,
        "new_registrations_this_week": 25,
        "top_active_users": [
            {"user_id": 1, "name": "Alice", "activity_score": 95},
            {"user_id": 2, "name": "Bob", "activity_score": 87},
        ]
    }
```

### 3. 🔄 Batch Operations

```python
class BatchUserUpdate(BaseModel):
    user_ids: List[int]
    updates: UserUpdate

@app.patch("/users/batch", tags=["Users"])
def batch_update_users(
    batch_update: BatchUserUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update multiple users at once (admin only)"""
    updated_users = []
    failed_updates = []
    
    for user_id in batch_update.user_ids:
        try:
            if user_id in users_db:
                # Apply updates
                user = users_db[user_id]
                update_data = batch_update.updates.model_dump(exclude_unset=True)
                
                for field, value in update_data.items():
                    user[field] = value
                
                user["updated_at"] = datetime.now().isoformat()
                updated_users.append(user)
            else:
                failed_updates.append({"user_id": user_id, "error": "User not found"})
        
        except Exception as e:
            failed_updates.append({"user_id": user_id, "error": str(e)})
    
    return {
        "updated_count": len(updated_users),
        "failed_count": len(failed_updates),
        "updated_users": updated_users,
        "failed_updates": failed_updates
    }

@app.post("/users/export", tags=["Users"])
def export_users(
    format: str = "csv",  # csv, json, xlsx
    filters: Optional[dict] = None,
    current_user: dict = Depends(require_admin)
):
    """Export users data (admin only)"""
    users = list(users_db.values())
    
    # Apply filters if provided
    if filters:
        if filters.get("role"):
            users = [u for u in users if u.get("role") == filters["role"]]
        if filters.get("is_active") is not None:
            users = [u for u in users if u.get("is_active") == filters["is_active"]]
    
    # In a real app, generate and return file
    export_id = str(uuid.uuid4())
    
    return {
        "export_id": export_id,
        "format": format,
        "total_records": len(users),
        "status": "processing",
        "download_url": f"/exports/{export_id}/download",
        "estimated_completion": datetime.now().isoformat()
    }
```

---

## 💡 Advanced Concepts

### 1. 🔐 Authentication & Authorization

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(login_data: LoginRequest):
    """Authenticate user and return JWT token"""
    # Find user by email
    user = None
    for u in users_db.values():
        if u.get("email") == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/logout", tags=["Authentication"])
def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (in a real app, you'd blacklist the token)"""
    return {"message": "Successfully logged out"}

@app.post("/auth/refresh", tags=["Authentication"])
def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user["id"]), "email": current_user["email"], "role": current_user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
```

### 2. 🔄 Rate Limiting

```python
from collections import defaultdict
from time import time

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    def decorator(func):
        def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time()
            window_start = current_time - (window_minutes * 60)
            
            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip] 
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(request_counts[client_ip]) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window_minutes} minutes"
                )
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.get("/api/limited-endpoint")
@rate_limit(max_requests=10, window_minutes=1)
def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

### 3. 📝 API Versioning

```python
from fastapi import APIRouter

# Version 1 API
v1_router = APIRouter(prefix="/api/v1", tags=["API v1"])

@v1_router.get("/users")
def get_users_v1():
    """Version 1 of users endpoint"""
    return {"users": list(users_db.values()), "version": "1.0"}

# Version 2 API with enhanced features
v2_router = APIRouter(prefix="/api/v2", tags=["API v2"])

@v2_router.get("/users")
def get_users_v2(
    include_inactive: bool = False,
    page: int = 1,
    limit: int = 20
):
    """Version 2 of users endpoint with pagination and inactive users"""
    users = list(users_db.values())
    
    if not include_inactive:
        users = [u for u in users if u.get("is_active", True)]
    
    # Pagination
    offset = (page - 1) * limit
    paginated_users = users[offset:offset + limit]
    
    return {
        "users": paginated_users,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(users),
            "pages": (len(users) + limit - 1) // limit
        },
        "version": "2.0"
    }

# Include routers
app.include_router(v1_router)
app.include_router(v2_router)

# Default to latest version
@app.get("/api/users")
def get_users_latest():
    """Redirect to latest API version"""
    return get_users_v2()
```

### 4. 🔍 Health Checks & Monitoring

```python
@app.get("/health", tags=["System"])
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": "24h 15m 30s"  # In real app, calculate actual uptime
    }

@app.get("/health/detailed", tags=["System"])
def detailed_health_check():
    """Detailed health check with system information"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": {
            "status": "connected",
            "users_count": len(users_db),
            "posts_count": len(posts_db) if 'posts_db' in globals() else 0
        },
        "memory_usage": "45%",  # In real app, get actual memory usage
        "cpu_usage": "12%",     # In real app, get actual CPU usage
        "disk_usage": "67%"     # In real app, get actual disk usage
    }

@app.get("/metrics", tags=["System"])
def get_metrics():
    """API metrics for monitoring"""
    return {
        "requests_total": 15420,
        "requests_per_minute": 45,
        "average_response_time": "120ms",
        "error_rate": "0.5%",
        "active_connections": 23,
        "endpoints": {
            "/users": {"requests": 5420, "avg_time": "89ms"},
            "/posts": {"requests": 3210, "avg_time": "156ms"},
            "/orders": {"requests": 2100, "avg_time": "234ms"}
        }
    }
```

---

## 🎓 Summary

### ✅ **Key Principles Learned**

1. **🎯 REST Architecture**
   - Use standard HTTP methods correctly
   - Design resource-based URLs with nouns
   - Return appropriate status codes
   - Be consistent in naming and structure

2. **📊 HTTP Methods Usage**
   - **GET**: Retrieve data (safe, idempotent)
   - **POST**: Create new resources (not idempotent)
   - **PUT**: Update/replace entire resource (idempotent)
   - **PATCH**: Partial updates (may not be idempotent)
   - **DELETE**: Remove resources (idempotent)

3. **🏗️ Route Design**
   - Use plural nouns: `/users`, `/posts`, `/orders`
   - Hierarchy for relationships: `/users/123/orders`
   - Query parameters for filtering: `?status=active&page=1`
   - Consistent naming conventions

4. **📋 Data Validation**
   - Use Pydantic models for request/response validation
   - Separate models for create, update, and response
   - Include field validation and custom validators
   - Handle validation errors gracefully

5. **🔐 Security & Best Practices**
   - Implement proper authentication and authorization
   - Use HTTPS in production
   - Validate all inputs
   - Handle errors gracefully with meaningful messages
   - Implement rate limiting
   - Use environment variables for secrets

### 🌟 **Real-World Applications**

- **E-commerce**: Products, cart management, orders
- **Blog**: Posts, comments, user management
- **Social Media**: Users, posts, likes, follows
- **SaaS**: Users, subscriptions, billing
- **IoT**: Devices, sensors, data collection

### 🚀 **Next Steps**

1. **Database Integration**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Caching**: Implement Redis for performance
3. **Testing**: Write comprehensive unit and integration tests
4. **Deployment**: Deploy with Docker and CI/CD pipelines
5. **Monitoring**: Add logging, metrics, and alerting
6. **Documentation**: Maintain up-to-date API documentation

### 💡 **Remember**

- **APIs are contracts** - Design them carefully and maintain backward compatibility
- **Consistency is key** - Follow the same patterns throughout your API
- **Documentation matters** - Good docs make your API easy to use
- **Security first** - Always validate inputs and protect sensitive data
- **Performance counts** - Use pagination, caching, and efficient queries
- **Monitor everything** - Track usage, errors, and performance metrics

---

## 🎯 **Final Checklist for Great APIs**

### ✅ **Design**
- [ ] RESTful resource-based URLs
- [ ] Consistent naming conventions
- [ ] Proper HTTP method usage
- [ ] Logical resource hierarchy
- [ ] Query parameters for filtering

### ✅ **Implementation**
- [ ] Input validation with Pydantic
- [ ] Proper error handling
- [ ] Appropriate status codes
- [ ] Response models defined
- [ ] Authentication/authorization

### ✅ **Documentation**
- [ ] Interactive API docs (Swagger/ReDoc)
- [ ] Clear endpoint descriptions
- [ ] Request/response examples
- [ ] Error response documentation
- [ ] Authentication instructions

### ✅ **Production Ready**
- [ ] Database integration
- [ ] Caching strategy
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] Health check endpoints
- [ ] Environment configuration
- [ ] Security headers
- [ ] CORS configuration

---

*Happy API Building! 🚀 Remember: Great APIs are built iteratively. Start simple, get feedback, and improve continuously.*
