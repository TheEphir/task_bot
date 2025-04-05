from datetime import date
from sqlalchemy.orm import Session

from . import models, schemas
from . import exchanges

def create_expense(db: Session, expense: schemas.ExpenseBase) -> schemas.ExpenseBase:
    usd_amount = round(expense.uah_amount / exchanges.get_NBU_usd_exchange_rate(),2)
    db_item = models.Expenses(**expense.model_dump(), usd_amount = usd_amount)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_expenses_all(db: Session) -> list[models.Expenses]:
    return db.query(models.Expenses).all()


def get_expense_by_id(db: Session, expense_id: int) -> models.Expenses:
    return db.query(models.Expenses).filter(models.Expenses.id == expense_id).first()


def get_expense_by_date(db: Session, expense_date: date, limit: int = 100) -> list[models.Expenses]:
    return db.query(models.Expenses).filter(models.Expenses.date == expense_date).limit(limit).all()


def get_expenses_by_date_range(db: Session, start_date: date, end_date: date, limit: int=100) -> list[models.Expenses]:
    return db.query(models.Expenses).filter(models.Expenses.date >= start_date).filter(models.Expenses.date <= end_date).order_by(models.Expenses.date).order_by(models.Expenses.id).limit(limit).all()
    

def delete_expense(db: Session, expense_id: int):
    item = db.get(models.Expenses, expense_id)
    db.delete(item)
    db.commit()
    return f"{item.description} was DELETED"