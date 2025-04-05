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


# works
@app.post("/expanse/", response_model=schemas.ExpenseBase)
def create_expanse(expanse: schemas.ExpenseBase, db: Session = Depends(get_db)):
    return crud.create_expanse(db=db, expanse=expanse)
    

# works
@app.delete("/expanse/{expanse_id}")
def delete_expanse(expanse_id: int, db:Session = Depends(get_db)):
    db_item = crud.get_expanse_by_id(db, expanse_id=expanse_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return crud.delete_expanse(db=db, expanse_id=expanse_id) 

# works
@app.get("/expanse/{expanse_id}", response_model=schemas.Expense)
def get_expanse_by_id(expanse_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_expanse_by_id(db, expanse_id=expanse_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_item


@app.get("/expanses/", response_model=list[schemas.Expense])
def get_expanses_by_date(expanse_date: date, db: Session = Depends(get_db), limit:int=100):
    db_items = crud.get_expanse_by_date(db, expanse_date=expanse_date)
    if db_items is None:
        raise HTTPException(status_code=404, detail="Can't find any expanse on this date")
    return db_items


# works
@app.put("/expanse/", response_model=schemas.ExpenseBase)
def change_expanse(expanse_id: int, expanse: schemas.ExpenseBase, db: Session = Depends(get_db)):
    db_item = crud.get_expanse_by_id(db, expanse_id=expanse_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    crud.delete_expanse(db=db, expanse_id=expanse_id)
    return crud.create_expanse(db=db, expanse=expanse)
