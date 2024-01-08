from pathlib import Path

import streamlit as st
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


# Create your SQLAlchemy model
class YourModel(Base, StreamlitAlchemyMixin):
    __tablename__ = "your_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean, default=True)
    count = Column(Integer)
    text = Column(Text)
    created_at = Column(DateTime)


def app():
    YourModel.st_crud_tabs()

    st.markdown("---")

    with CONNECTION.session as session:
        for item in session.query(YourModel).all():
            st.subheader(item.name)
            item.st_edit_button("Edit", {"name": "New Name"})
            item.st_delete_button()


def main():
    if not Path("example.db").exists():
        Base.metadata.create_all(CONNECTION.engine)

    # initialize the StreamlitAlchemyMixin
    StreamlitAlchemyMixin.st_initialize(connection=CONNECTION)

    # the actual app
    app()


if __name__ == "__main__":
    # initialize the database connection
    # (see https://docs.streamlit.io/library/api-reference/connections/st.connection)
    CONNECTION = st.connection("example2_db", type="sql")

    if not Path("example2.db").exists():
        Base.metadata.create_all(CONNECTION.engine)

    StreamlitAlchemyMixin.st_initialize(connection=CONNECTION)
    main()
