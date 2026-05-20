# Microservices Stack

This module contains the new backend microservices for the Personal Finance Tracker.

- **Transaction Service** (Port 8001): Handles core CRUD for transactions.
- **Budget Service** (Port 8002): Manages budgets.
- **Report Service** (Port 8003): Generates analytics summaries.
- **Notification Service** (Port 8004): Monitors budgets and generates alerts.

## Requirements
```bash
pip install fastapi uvicorn httpx pydantic sqlite3
```

## Running the services
You can run each service individually:
```bash
uvicorn transaction_service.main:app --port 8001 --reload
uvicorn budget_service.main:app --port 8002 --reload
uvicorn report_service.main:app --port 8003 --reload
uvicorn notification_service.main:app --port 8004 --reload
```
