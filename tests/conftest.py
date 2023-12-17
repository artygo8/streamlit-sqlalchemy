import os
import pytest

from sqlalchemy import create_engine

from streamlit_sqlalchemy import StreamlitAlchemyMixin
from tests.objects import Base


@pytest.fixture
def database():
    db_engine = create_engine("sqlite:///test.sqlite")
    Base.metadata.create_all(db_engine)
    StreamlitAlchemyMixin.sam_initialize(Base, db_engine)
    yield db_engine
    os.remove("test.sqlite")
