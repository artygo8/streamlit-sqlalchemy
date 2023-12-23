from pathlib import Path

import streamlit as st
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship

from streamlit_sqlalchemy import declarative_streamlit_view

Base = declarative_base()


class CarBrand(Base):
    __tablename__ = "car_brand"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class CarModel(Base):
    __tablename__ = "car_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    brand_id = Column(Integer, ForeignKey("car_brand.id"))

    brand = relationship("CarBrand", backref="cars")

    def __st_order_by__(self):
        return self.name

class Car(Base):
    __tablename__ = "car"

    id = Column(Integer, primary_key=True)
    serial = Column(String)
    model_id = Column(Integer, ForeignKey("car_model.id"))

    model = relationship("CarModel", backref="cars")

    def __repr__(self):
        return f"<Car {self.model.name} {self.serial}>"
    
    def __st_repr__(self):
       return f"{self.model.name} - {self.serial}"

    def __st_order_by__(self):
        return self.serial


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    car_id = Column(Integer, ForeignKey("car.id"))

    car = relationship("Car", backref="users")

    def __st_order_by__(self):
        return self.fullname


def main():
    car_brand_view = StreamlitView(CarBrand)
    car_model_view = StreamlitView(CarModel)
    car_view = StreamlitView(Car)
    user_view = StreamlitView(User)

    car_brand_view.crud_tabs()
    car_model_view.crud_tabs()
    car_view.crud_tabs()
    user_view.crud_tabs()

    for user in user_view.get_session().query(User).all():
        st.write(
            user.fullname,
            user.car.model.brand.name,
            user.car.model.name,
            user.car.serial,
        )
        user_view.delete_button(user)


if __name__ == "__main__":
    should_init = not Path("db.sqlite3").exists()
    engine = create_engine("sqlite:///db.sqlite3")
    if should_init:
        Base.metadata.create_all(engine)

    StreamlitView = declarative_streamlit_view(engine)
    main()
