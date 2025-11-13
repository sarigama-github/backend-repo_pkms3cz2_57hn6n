import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import db, create_document, get_documents

app = FastAPI(title="Startup Expenditure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Startup Expenditure API is running"}


# ---------- Schemas for request/response ----------
class CategoryIn(BaseModel):
    name: str = Field(...)
    color: Optional[str] = Field(None)


class ExpenseIn(BaseModel):
    title: str
    amount: float = Field(..., ge=0)
    category_id: Optional[str] = None
    date: Optional[datetime] = None
    vendor: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class BudgetIn(BaseModel):
    category_id: Optional[str] = None
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    limit: float = Field(..., ge=0)


# ---------- Helper ----------

def ensure_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available. Set DATABASE_URL and DATABASE_NAME.")


# ---------- Category Endpoints ----------

@app.post("/api/categories")
def create_category(payload: CategoryIn):
    ensure_db()
    _id = create_document("category", payload.model_dump())
    return {"_id": _id, **payload.model_dump()}


@app.get("/api/categories")
def list_categories():
    ensure_db()
    items = get_documents("category")
    # Cast ObjectId to string if present
    for it in items:
        if "_id" in it:
            it["_id"] = str(it["_id"])
    return items


# ---------- Expense Endpoints ----------

@app.post("/api/expenses")
def create_expense(payload: ExpenseIn):
    ensure_db()
    data = payload.model_dump()
    if not data.get("date"):
        data["date"] = datetime.utcnow()
    _id = create_document("expense", data)
    return {"_id": _id, **data}


@app.get("/api/expenses")
def list_expenses(limit: Optional[int] = None):
    ensure_db()
    items = get_documents("expense", limit=limit)
    for it in items:
        if "_id" in it:
            it["_id"] = str(it["_id"])
        # Convert datetime to isoformat for JSON
        if isinstance(it.get("date"), datetime):
            it["date"] = it["date"].isoformat()
    return items


# ---------- Budget Endpoints ----------

@app.post("/api/budgets")
def create_budget(payload: BudgetIn):
    ensure_db()
    _id = create_document("budget", payload.model_dump())
    return {"_id": _id, **payload.model_dump()}


@app.get("/api/budgets")
def list_budgets(month: Optional[int] = None, year: Optional[int] = None, category_id: Optional[str] = None):
    ensure_db()
    filt = {}
    if month is not None:
        filt["month"] = month
    if year is not None:
        filt["year"] = year
    if category_id is not None:
        filt["category_id"] = category_id
    items = get_documents("budget", filter_dict=filt)
    for it in items:
        if "_id" in it:
            it["_id"] = str(it["_id"])
    return items


# ---------- Diagnostics ----------

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
