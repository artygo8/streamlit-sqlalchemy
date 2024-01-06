# Streamlit SQLAlchemy Integration

## Overview

`streamlit_sqlalchemy` is a Python module that provides seamless integration between Streamlit and SQLAlchemy models. It simplifies the process of creating, updating, and deleting database objects through Streamlit's user-friendly interface.

## Features

- **Easy Initialization**: Initialize the SQLAlchemy engine with a simple method call.
- **CRUD Operations**: Create, read, update, and delete operations are streamlined with minimal code.
- **Dynamic Forms**: Automatically generate forms for creating and updating database objects.
- **Tabbed Interface**: Organize CRUD operations in a tabbed interface for better user experience.
- **Foreign Key Support**: Easily handle foreign key relationships in forms.

## Installation

```bash
pip install streamlit_sqlalchemy
```

## Usage

1. **Initialize the Engine:**

   ```python
   from streamlit_sqlalchemy import StreamlitAlchemyMixin

   # Create your SQLAlchemy model
   class YourModel(Base, StreamlitAlchemyMixin):
       __tablename__ = "your_model"

       id = Column(Integer, primary_key=True)
       # Other fields

   # Initialize the engine
   StreamlitAlchemyMixin.st_initialize(engine)
   ```

2. **CRUD Tabs:**

   ```python
   YourModel.st_crud_tabs()
   ```

3. **Customization:**

   Customize the behavior by overriding methods in your model.

   ```python
   class CustomModel(YourModel):
       # Override methods as needed
   ```

## Simple Example

```python
import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from streamlit_sqlalchemy import StreamlitAlchemyMixin

Base = declarative_base()

class ExampleModel(Base, StreamlitAlchemyMixin):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True)
    name = Column(String)

# Initialize the connection
CONNECTION = st.connection("example_db", type="sql")
Base.metadata.create_all(CONNECTION.engine)
StreamlitAlchemyMixin.st_initialize(CONNECTION)

# Create CRUD tabs
ExampleModel.st_crud_tabs()
```

## Comprehensive Example

```python
import logging
from pathlib import Path

import streamlit as st

from examples.models import Base, Task, User
from streamlit_sqlalchemy import StreamlitAlchemyMixin


def show_single_task(task):
    col1, col2, col3 = st.columns([1, 1, 1])
    if task.done:
        col1.write(f" - ~~{task.description}~~")
        with col2:
            task.st_delete_button()
    else:
        if task.due_date:
            date_color = "red" if task.due_date < datetime.now() else "green"
            col1.write(f" - {task.description} (:{date_color}[{task.due_date.strftime('%H:%M - %d.%m.%Y')}])")
        else:
            col1.write(f" - {task.description}")
        with col2:
            task.st_edit_button("Done", {"done": True})
        with col3:
            task.st_delete_button()


def app():
    st.title("Streamlit SQLAlchemy Demo")

    User.st_crud_tabs()

    with CONNECTION.session as session:
        for user in session.query(User).all():
            with st.expander(f"### {user.name}'s tasks:"):
                c = st.container()

                st.write("**Add a new task:**")
                Task.st_create_form(defaults={"user_id": user.id, "done": False})
                with c:
                    if not user.tasks:
                        st.caption("No tasks yet.")

                    for task in user.tasks:
                        show_single_task(task)


def main():
    if not Path("example.db").exists():
        Base.metadata.create_all(CONNECTION.engine)

    StreamlitAlchemyMixin.st_initialize(connection=CONNECTION)

    app()


if __name__ == "__main__":
    # initialize the database connection
    # (see https://docs.streamlit.io/library/api-reference/connections/st.connection)
    CONNECTION = st.connection("example_db", type="sql")
    main()
```

You can explore this provided [example](./examples/example.py), and launch it from the root directory (because it relies on relative imports):

```bash
python -m streamlit run examples/example.py
```

![assets/streamlit-example-2023-12-31-16-12-91.gif](./assets/streamlit-example-2023-12-31-16-12-91.gif)


## Contributing

We welcome contributions! See our [contribution guidelines](./CONTRIBUTING) for more details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
