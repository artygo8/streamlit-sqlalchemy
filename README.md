# streamlit-sqlalchemy

Some templating for streamlit and sqlalchemy

[streamlit-sql-crud](./image.png)

## Usage

```bash
python3 -m pip install streamlit-sqlalchemy
python3 -m streamlit run example.py
```

Add the mixin to your SQLAlchemy defined classes and you will have access to basic streamlit components.

```python
from pathlib import Path

import streamlit as st
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()


class Awesome(Base, StreamlitAlchemyMixin):
    __tablename__ = "car_brand"

    id = Column(Integer, primary_key=True)
    name = Column(String)

# The usual SQLAlchemy stuff
should_init = not Path("db.sqlite3").exists()
engine = create_engine("sqlite:///db.sqlite3")
if should_init:
    Base.metadata.create_all(engine)

# Must be called before any other method
StreamlitAlchemyMixin.sam_initialize(Base, engine)

Awesome.sam_create_form()
Awesome.sam_update_form()
Awesome.sam_delete_form()
Awesome.sam_crud_tabs()

for awesome in Awesome.sam_get_all():
    st.write(awesome.name)
    awesome.delete_button()
```

## Contribute

You are welcome to contribute!
