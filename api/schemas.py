# kinda validation for input data
from datetime import date
from pydantic import BaseModel


class ExpenseBase(BaseModel):
    description : str
    uah_amount: float
    date : date


class Expense(ExpenseBase):
    id: int
    usd_amount: float
    class Config:
        orm_mode = True
        