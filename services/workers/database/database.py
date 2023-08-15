from sqlalchemy import create_engine
from sqlalchemy.orm import MappedAsDataclass, sessionmaker, DeclarativeBase
from contextlib import contextmanager

class Base(MappedAsDataclass, DeclarativeBase):
    pass

SQL_ALCHEMY_DATABASE_URI = 'sqlite:///./example.db'
engine = create_engine(SQL_ALCHEMY_DATABASE_URI)

Session = sessionmaker(bind=engine)

@contextmanager
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
        
def create_all():
    Base.metadata.create_all(bind=engine)
