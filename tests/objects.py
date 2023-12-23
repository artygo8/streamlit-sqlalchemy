from contextlib import contextmanager
import os

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count = Column(Integer)


class OneToMany(Base):
    __tablename__ = "one_to_many"

    id = Column(Integer, primary_key=True)
    first_field = Column(String)
    test_item_id = Column(Integer, ForeignKey("item.id"))

    test_item = relationship("Item", backref="one_to_many")


@contextmanager
def engine_ctx():
    engine = create_engine("sqlite:///test.sqlite3")
    Base.metadata.create_all(engine)
    yield engine
    os.remove("test.sqlite3")
