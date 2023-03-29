"""Data warehouse connection"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from helper_functions import get_config

config = get_config()
user = config['Database']['user']
password = config['Database']['password']
server = config['Database']['host']
database = config['Database']['database']

DW_URL = f"postgresql://{user}:{password}@{server}/{database}"

engine = create_engine(DW_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
