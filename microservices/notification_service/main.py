from fastapi import FastAPI
import httpx
from typing import List, Dict

app = FastAPI(title="Notification & Reminder Service")

BUDGET_SERVICE_URL = "http://127.0.0.1:8002"

@app.get("/notifications/check-budgets/{year}/{month}")
async def check_budgets(year: int, month: int):
    alerts = []
    
    async with httpx.AsyncClient() as client:
        try:
            # Get all budgets
            resp = await client.get(f"{BUDGET_SERVICE_URL}/budgets/{year}/{month}")
            if resp.status_code == 200:
                budgets = resp.json()
                
                for b in budgets:
                    cat = b["category"]
                    # Fetch status for each category
                    status_resp = await client.get(f"{BUDGET_SERVICE_URL}/budgets/{year}/{month}/{cat}/status")
                    if status_resp.status_code == 200:
                        status = status_resp.json()
                        pct = status["percent_used"]
                        
                        if pct >= 100:
                            alerts.append({
                                "category": cat,
                                "level": "CRITICAL",
                                "message": f"Budget EXCEEDED for {cat}. Spent ${status['spent']:.2f} of ${status['budget_limit']:.2f}"
                            })
                        elif pct >= 80:
                            alerts.append({
                                "category": cat,
                                "level": "WARNING",
                                "message": f"Approaching budget limit for {cat}. Currently at {pct:.1f}%"
                            })
        except Exception as e:
            return {"error": "Failed to communicate with Budget service", "details": str(e)}
            
    if not alerts:
        return {"status": "ok", "message": "All budgets are within safe limits."}
        
    return {"status": "alerts_generated", "alerts": alerts}
