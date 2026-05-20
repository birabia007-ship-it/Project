from fastapi import FastAPI
import httpx
from typing import Dict, Any

app = FastAPI(title="Report Service")

TRANSACTION_SERVICE_URL = "http://127.0.0.1:8001"

@app.get("/reports/monthly-summary/{year}/{month}")
async def get_monthly_summary(year: int, month: int) -> Dict[str, Any]:
    total_income = 0.0
    total_expense = 0.0
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{TRANSACTION_SERVICE_URL}/transactions/")
            if resp.status_code == 200:
                txns = resp.json()
                prefix = f"{year:04d}-{month:02d}"
                for t in txns:
                    if t["date"].startswith(prefix):
                        if t["type"] == "income":
                            total_income += t["amount"]
                        elif t["type"] == "expense":
                            total_expense += t["amount"]
        except Exception as e:
            return {"error": "Could not communicate with transaction service"}

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense
    }

@app.get("/reports/category-breakdown/{year}/{month}")
async def get_category_breakdown(year: int, month: int, type: str = "expense"):
    breakdown = {}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{TRANSACTION_SERVICE_URL}/transactions/")
            if resp.status_code == 200:
                txns = resp.json()
                prefix = f"{year:04d}-{month:02d}"
                for t in txns:
                    if t["date"].startswith(prefix) and t["type"] == type:
                        cat = t["category"]
                        breakdown[cat] = breakdown.get(cat, 0.0) + t["amount"]
        except Exception:
            return {"error": "Could not communicate with transaction service"}
            
    # Format for charting
    result = [{"category": k, "total": v} for k, v in breakdown.items()]
    result.sort(key=lambda x: x["total"], reverse=True)
    return result
