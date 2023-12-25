import logging
from pathlib import Path

import streamlit as st
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


class StreamlitHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        st.toast(log_entry)


@st.cache_resource
def configure_logging():
    logging.getLogger().addHandler(StreamlitHandler())
    logging.getLogger().setLevel(logging.INFO)


configure_logging()


class CarBrand(Base, StreamlitAlchemyMixin):
    __tablename__ = "car_brand"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class CarModel(Base, StreamlitAlchemyMixin):
    __tablename__ = "car_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    brand_id = Column(Integer, ForeignKey("car_brand.id"))

    brand = relationship("CarBrand", backref="cars")


class Car(Base, StreamlitAlchemyMixin):
    __tablename__ = "car"

    id = Column(Integer, primary_key=True)
    serial = Column(String)
    model_id = Column(Integer, ForeignKey("car_model.id"))

    model = relationship("CarModel", backref="cars")


class User(Base, StreamlitAlchemyMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    car_id = Column(Integer, ForeignKey("car.id"))

    car = relationship("Car", backref="users")


def main():
    CarBrand.st_crud_tabs()
    CarModel.st_crud_tabs()
    Car.st_crud_tabs()
    User.st_crud_tabs(defaults={"fullname": "John Doe"})

    for user in User.st_list_all():
        st.write(
            user.fullname,
        )
        user.st_delete_button()


if __name__ == "__main__":
    should_init = not Path("db.sqlite3").exists()
    engine = create_engine("sqlite:///db.sqlite3")
    if should_init:
        Base.metadata.create_all(engine)

    StreamlitAlchemyMixin.st_initialize(engine)
    main()
