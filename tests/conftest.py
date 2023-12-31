import os

import pytest
import streamlit as st
from sqlalchemy import create_engine

from streamlit_sqlalchemy import StreamlitAlchemyMixin
from tests.objects import Base


@pytest.fixture
def database():
    connection = st.connection("test.sqlite", type="sql", url="sqlite:///test.sqlite")
    Base.metadata.create_all(connection.engine)
    StreamlitAlchemyMixin.st_initialize(connection)
    yield connection
    os.remove("test.sqlite")
