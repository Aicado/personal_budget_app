import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
import io
import time

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_analyze_endpoint():
    # Use unique data to avoid duplicate detection if the DB isn't cleared
    unique_id = str(time.time())
    csv_content = f"Date,Payee,Category,Outflow,Inflow\n2024-01-01,Starbucks-{unique_id},Food | Coffee,5.50,0.00"
    files = {'file': ('test.csv', csv_content, 'text/csv')}

    response = client.post("/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.csv"
    assert "monthly_trends" in data
    # It might be duplicate if tests run multiple times, but here we expect inserted with unique data
    assert data["database"]["status"] == "inserted"

def test_database_stats_endpoint():
    response = client.get("/database/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data

def test_accounts_status_endpoint():
    response = client.get("/accounts/status")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
