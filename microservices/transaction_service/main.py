from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI(title="Transaction Service")

DB_PATH = "transactions.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Init DB
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Transaction(BaseModel):
    type: str
    category: str
    amount: float
    date: str
    description: Optional[str] = ""

class TransactionOut(Transaction):
    id: int

@app.post("/transactions/", response_model=TransactionOut)
def add_transaction(txn: Transaction):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (type, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
        (txn.type, txn.category, txn.amount, txn.date, txn.description)
    )
    conn.commit()
    txn_id = cursor.lastrowid
    conn.close()
    return {**txn.model_dump(), "id": txn_id}

@app.get("/transactions/", response_model=List[TransactionOut])
def get_transactions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/transactions/{txn_id}", response_model=TransactionOut)
def get_transaction(txn_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id=?", (txn_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return dict(row)

@app.delete("/transactions/{txn_id}")
def delete_transaction(txn_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (txn_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    conn.commit()
    conn.close()
    return {"message": "Transaction deleted successfully"}
