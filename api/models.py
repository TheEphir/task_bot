# A psql table markup

from sqlalchemy import Column, Integer,Float, String, Date

from .database import Base

class Expenses(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    description = Column(String, index=True)
    uah_amount = Column(Float)
    usd_amount = Column(Float)
    date = Column(Date)
    