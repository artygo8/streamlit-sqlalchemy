import streamlit as st
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
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


class SuperItem(Base, StreamlitAlchemyMixin):
    __tablename__ = "super_item"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count = Column(Integer)

    __st_repr__ = lambda self: f"{self.name} ({self.count})"
    __st_order_by__ = lambda self: self.count


class AdvancedObject(Base, StreamlitAlchemyMixin):
    __tablename__ = "advanced_object"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    another_string = Column(String)
    yet_another_string = Column(String)
    text = Column(Text)
    count = Column(Integer)
    my_float = Column(Float)
    my_bool = Column(Boolean)
    my_other_bool = Column(Boolean)
    due_datetime = Column(DateTime)
    creating_date = Column(Date)
    closing_time = Column(Time)
    super_item_id = Column(Integer, ForeignKey("super_item.id"))

    item = relationship("SuperItem", backref="advanced_object")

    __st_input_meta__ = {
        "another_string": st.text_area,
        "my_other_bool": lambda *a, **kw: st.checkbox(*a, **kw, value=True),
    }
