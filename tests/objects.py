from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


class Item(Base, StreamlitAlchemyMixin):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count = Column(Integer)


class OneToMany(Base, StreamlitAlchemyMixin):
    __tablename__ = "one_to_many"

    id = Column(Integer, primary_key=True)
    first_field = Column(String)
    test_item_id = Column(Integer, ForeignKey("item.id"))

    test_item = relationship("Item", backref="one_to_many")
