import os
import tempfile

import pytest
import streamlit as st
from sqlalchemy import create_engine

from streamlit_sqlalchemy import StreamlitAlchemyMixin
from tests.objects import Base


@pytest.fixture
def database():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.sqlite")
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    connection = st.connection("test", type="sql", url=db_url)
    StreamlitAlchemyMixin.st_initialize(connection)

    yield connection

    # Cleanup
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except (OSError, FileNotFoundError):
        pass
