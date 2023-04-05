"""Connect to the data warehouse connection and declare a sessionmaker."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from helper_functions import get_config

config = get_config()
user = config['Database']['user']
password = config['Database']['password']
server = config['Database']['host']
database = config['Database']['database']


if os.getenv("IS_TESTING", False):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{database}.sqlite"
else:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
