import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def read_env() -> dict:
    return {
        "PS_USER": os.environ["PS_USER"],
        "PS_PASS": os.environ["PS_PASS"],
        "PS_SERVER": os.environ["PS_SERVER"],
        "PS_DB": os.environ["PS_DB"],
    }    


creds = read_env()

SQLALCHEMY_DATABASE_URL = f"postgresql://{creds["PS_USER"]}:{creds['PS_PASS']}@{creds['PS_SERVER']}/{creds['PS_DB']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()