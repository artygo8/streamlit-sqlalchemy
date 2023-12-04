from pathlib import Path

import streamlit as st
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


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
    CarBrand.sam_crud_tabs()
    CarModel.sam_crud_tabs()
    Car.sam_crud_tabs()
    User.sam_crud_tabs()

    for user in User.sam_get_all():
        st.write(
            user.fullname,
            user.car.model.brand.name,
            user.car.model.name,
            user.car.serial,
        )
        user.sam_delete_button()


if __name__ == "__main__":
    should_init = not Path("db.sqlite3").exists()
    engine = create_engine("sqlite:///db.sqlite3")
    if should_init:
        Base.metadata.create_all(engine)

    StreamlitAlchemyMixin.sam_initialize(Base, engine)
    main()
