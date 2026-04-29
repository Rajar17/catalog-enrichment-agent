"""
Tenarai Catalog Enrichment — FastAPI Backend
Exposes a /enrich endpoint for single and batch product enrichment.

Run: uvicorn api:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agents.enrichment_agent import enrich_product, enrich_catalog

app = FastAPI(
    title="Tenarai Catalog Enrichment API",
    description="AI-powered product catalog enrichment for HP laptops",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductInput(BaseModel):
    name: str
    model_number: str
    raw_specs: Optional[str] = ""


class BatchInput(BaseModel):
    products: list[ProductInput]


@app.get("/")
def root():
    return {"service": "Tenarai Catalog Enrichment API", "status": "running"}


@app.post("/enrich")
def enrich_single(product: ProductInput):
    """Enrich a single HP laptop product."""
    try:
        result = enrich_product(product.model_dump())
        if result["status"] != "success":
            raise HTTPException(status_code=422, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enrich/batch")
def enrich_batch(batch: BatchInput):
    """Enrich multiple products in sequence."""
    try:
        products = [p.model_dump() for p in batch.products]
        results = enrich_catalog(products)
        success = sum(1 for r in results if r["status"] == "success")
        return {
            "total": len(results),
            "success": success,
            "failed": len(results) - success,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
