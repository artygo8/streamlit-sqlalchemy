import enum
import streamlit as st
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


class UserType(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    PUBLIC = "public"

    def __str__(self):
        return self.name.lower().capitalize()


class User(Base, StreamlitAlchemyMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_type = Column(Enum(UserType))


class Task(Base, StreamlitAlchemyMixin):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    done = Column(Boolean, default=False)
    due_date = Column(DateTime)

    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", backref="tasks")

    __st_input_meta__ = {
        "description": lambda *a, **kw: st.text_area(*a, **kw, height=100),
    }
