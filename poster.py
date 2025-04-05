from datetime import date
import requests
import json

API_URL = "http://localhost:80"
for i in range(5):
    item = {
        "description": f"test0{i}",
        "uah_amount": i+1000.3,
        "date": str(date(2025,4,20))
    }
    requests.post(f"{API_URL}/expense/", json=item)

for i in range(5):
    item = {
        "description": f"test1{i}",
        "uah_amount": i+1000,
        "date": str(date(2025,4,22))
    }
    requests.post(f"{API_URL}/expense/", json=item)

for i in range(5):
    item = {
        "description": f"test2{i}",
        "uah_amount": i+1000.4,
        "date": str(date(2025,4,21))
    }
    requests.post(f"{API_URL}/expense/", json=item)

for i in range(5):
    item = {
        "description": f"test3{i}",
        "uah_amount": i+3000,
        "date": str(date(2025,4,23))
    }
    requests.post(f"{API_URL}/expense/", json=item)