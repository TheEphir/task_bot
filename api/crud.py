from datetime import date
from sqlalchemy.orm import Session

from . import models, schemas
from . import exchanges

def create_expanse(db: Session, expanse: schemas.ExpenseBase):
    usd_amount = expanse.uah_amount / exchanges.get_NBU_usd_exchange_rate() 
    db_item = models.Expenses(**expanse.model_dump(), usd_amount = usd_amount)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_expanse_by_id(db: Session, expanse_id: int):
    return db.query(models.Expenses).filter(models.Expenses.id == expanse_id).first()


def get_expanse_by_date(db: Session, expanse_date: date, limit: int = 100):
    return db.query(models.Expenses).filter(models.Expenses.date == expanse_date).limit(limit).all()


def delete_expanse(db: Session, expanse_id: int):
    item = db.get(models.Expenses, expanse_id)
    db.delete(item)
    db.commit()
    return f'{item.description} was DELETED'