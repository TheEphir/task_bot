import requests
from bot import utils
from datetime import date
API_URL = "http://localhost:80"

removed_expense = requests.delete(f"{API_URL}/expense/", params={"expense_id": 1}).json()



print(f"expenses{date.today()}.xml")