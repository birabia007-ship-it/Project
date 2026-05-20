from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import httpx

app = FastAPI(title="Budget Service")

DB_PATH = "budgets.db"
TRANSACTION_SERVICE_URL = "http://127.0.0.1:8001"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(category, month, year)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Budget(BaseModel):
    category: str
    amount: float
    month: int
    year: int

class BudgetOut(Budget):
    id: int

@app.post("/budgets/", response_model=BudgetOut)
def set_budget(budget: Budget):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO budgets (category, amount, month, year)
           VALUES (?, ?, ?, ?)""",
        (budget.category, budget.amount, budget.month, budget.year)
    )
    conn.commit()
    budget_id = cursor.lastrowid
    conn.close()
    return {**budget.model_dump(), "id": budget_id}

@app.get("/budgets/{year}/{month}", response_model=List[BudgetOut])
def get_all_budgets(year: int, month: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE year=? AND month=?", (year, month))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/budgets/{year}/{month}/{category}/status")
async def get_budget_status(year: int, month: int, category: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE year=? AND month=? AND category=?", (year, month, category))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget_limit = row["amount"]
    
    # Communicate with Transaction Service to calculate spent amount
    spent = 0.0
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{TRANSACTION_SERVICE_URL}/transactions/")
            if resp.status_code == 200:
                txns = resp.json()
                prefix = f"{year:04d}-{month:02d}"
                for t in txns:
                    if t["type"] == "expense" and t["category"] == category and t["date"].startswith(prefix):
                        spent += t["amount"]
        except Exception:
            # Handle failure gracefully
            pass

    return {
        "category": category,
        "budget_limit": budget_limit,
        "spent": spent,
        "remaining": budget_limit - spent,
        "percent_used": (spent / budget_limit) * 100 if budget_limit > 0 else 0
    }
