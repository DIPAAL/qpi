"""Connect to the database and declare a sessionmaker."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from helper_functions import get_config

config = get_config()

SQLALCHEMY_DATABASE_URL = \
    f"postgresql://{config['Database']['user']}@{config['Database']['host']}/{config['Database']['database']}"

if os.getenv("IS_TESTING", False):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{config['Database']['database']}.sqlite"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
