from datetime import date
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST expense into psql
@app.post("/expense/", response_model=schemas.ExpenseBase)
def create_expense(expense: schemas.ExpenseBase, db: Session = Depends(get_db)):
    return crud.create_expense(db=db, expense=expense)
    

# DEL expense by id
@app.delete("/expense/{expense_id}")
def delete_expense(expense_id: int, db:Session = Depends(get_db)):
    db_item = crud.get_expense_by_id(db, expense_id=expense_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return crud.delete_expense(db=db, expense_id=expense_id) 


# GET expense by id
@app.get("/expense/{expense_id}", response_model=schemas.Expense)
def get_expense_by_id(expense_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_expense_by_id(db, expense_id=expense_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expenses not found")
    return db_item


# GET expenses all
@app.get("/expenses", response_model=list[schemas.Expense])
def get_all_exenses(db: Session = Depends(get_db)):
    db_items = crud.get_expenses_all(db)
    if db_items is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_items
    

# GET expenses by date
@app.get("/expenses/date/", response_model=list[schemas.Expense])
def get_expenses_by_date(expense_date: date, db: Session = Depends(get_db), limit:int=100):
    db_items = crud.get_expense_by_date(db, expense_date=expense_date, limit=limit)
    if db_items is None:
        raise HTTPException(status_code=404, detail="Can't find any expense on this date")
    return db_items


# GET expenses by date range
@app.get("/expenses/daterange/", response_model=list[schemas.Expense])
def get_expenses_by_date_range(start_date: date, end_date: date, db: Session = Depends(get_db), limit:int=100):
    db_items = crud.get_expenses_by_date_range(db=db, start_date=start_date, end_date=end_date, limit=limit)
    if db_items is None:
        raise HTTPException(status_code=404, detail="Can't find any expense in this date range")
    return db_items


# PUT expense in psql
@app.put("/expense/", response_model=schemas.ExpenseBase)
def change_expense(expense_id: int, expense: schemas.ExpenseBase, db: Session = Depends(get_db)):
    db_item = crud.get_expense_by_id(db, expense_id=expense_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    crud.delete_expense(db=db, expense_id=expense_id)
    return crud.create_expense(db=db, expense=expense)

