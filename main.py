import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from schemas import Order
from database import create_document, get_documents

app = FastAPI(title="Bits & Bites API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bits & Bites backend is running"}

@app.get("/test")
def test_database():
    """Quick health check for backend and database connectivity"""
    from database import db  # lazy import
    status = {
        "backend": "ok",
        "database": "disconnected",
        "collections": [],
        "env": {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "DATABASE_NAME": bool(os.getenv("DATABASE_NAME")),
        },
    }
    try:
        if db is not None:
            status["database"] = "connected"
            try:
                status["collections"] = db.list_collection_names()[:10]
            except Exception:
                pass
    except Exception as e:
        status["database_error"] = str(e)
    return status

# Utility: convert ObjectId to str for API responses
class MongoJSON(BaseModel):
    @staticmethod
    def normalize(doc: Dict[str, Any]) -> Dict[str, Any]:
        out = {**doc}
        if "_id" in out and isinstance(out["_id"], ObjectId):
            out["id"] = str(out.pop("_id"))
        # Convert datetimes to isoformat strings if present
        for k, v in list(out.items()):
            if hasattr(v, "isoformat"):
                out[k] = v.isoformat()
        return out

@app.post("/orders")
def create_order(order: Order):
    try:
        order_id = create_document("order", order)
        return {"id": order_id, "message": "Order created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
def list_orders(mobile: Optional[str] = Query(None, alias="mobile"), limit: int = Query(25, ge=1, le=100)):
    try:
        filter_dict: Dict[str, Any] = {}
        if mobile:
            # Normalize to digits only (10)
            digits = ''.join([c for c in mobile if c.isdigit()])
            filter_dict["customer_mobile"] = digits
        docs = get_documents("order", filter_dict, limit)
        return [MongoJSON.normalize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
