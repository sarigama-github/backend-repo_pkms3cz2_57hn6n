"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Class name lowercased is used as the collection name.

This app models a simple startup expenditure manager with categories,
expenses, and optional monthly budgets.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# ---------- Core Collections ----------

class Category(BaseModel):
    """
    Categories for expenses
    Collection: "category"
    """
    name: str = Field(..., description="Category name, e.g., Marketing, Cloud, Salaries")
    color: Optional[str] = Field(None, description="Hex color for visualizations (e.g., #22c55e)")


class Expense(BaseModel):
    """
    Individual expense items
    Collection: "expense"
    """
    title: str = Field(..., description="Short label for the expense")
    amount: float = Field(..., ge=0, description="Amount spent")
    category_id: Optional[str] = Field(None, description="Reference to a Category document _id as string")
    date: datetime = Field(default_factory=datetime.utcnow, description="Expense date")
    vendor: Optional[str] = Field(None, description="Vendor or payee")
    payment_method: Optional[str] = Field(None, description="Card, Wire, ACH, etc.")
    notes: Optional[str] = Field(None, description="Any additional context")


class Budget(BaseModel):
    """
    Monthly budget per category or overall
    Collection: "budget"
    """
    category_id: Optional[str] = Field(None, description="If set, budget applies to that category; otherwise overall")
    period: Literal["month"] = Field("month", description="Currently only monthly budgets supported")
    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    year: int = Field(..., ge=2000, le=2100, description="Calendar year")
    limit: float = Field(..., ge=0, description="Spending cap for the period")


# Example schemas kept for reference (not used by the app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
