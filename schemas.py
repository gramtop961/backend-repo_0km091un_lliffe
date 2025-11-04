"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Bits & Bites: Order-related schemas
class OrderItem(BaseModel):
    name: str
    price: int = Field(..., ge=0)
    qty: int = Field(..., ge=1)

class Order(BaseModel):
    customer_name: str
    customer_mobile: str = Field(..., description="10-digit mobile number")
    items: List[OrderItem]
    subtotal: int = Field(..., ge=0)
    discount: int = Field(0, ge=0)
    total: int = Field(..., ge=0)
    payment_method: Literal["cod", "upi"]
    coupon_code: Optional[str] = None

    @field_validator("customer_mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        digits = ''.join([ch for ch in v if ch.isdigit()])
        if len(digits) != 10:
            raise ValueError("Mobile must be 10 digits")
        return digits

# Note: Each class name maps to a collection of the same lowercase name.
# For example, Order -> "order" collection.
