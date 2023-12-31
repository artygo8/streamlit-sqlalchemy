from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


class User(Base, StreamlitAlchemyMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Task(Base, StreamlitAlchemyMixin):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", backref="tasks")
