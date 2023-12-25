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

## Example

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

# Initialize the engine
engine = create_engine("sqlite:///example.db")
ExampleModel.st_initialize(engine)

# Create CRUD tabs
ExampleModel.st_crud_tabs()
```

## Documentation

The project documentation is currently under development. Meanwhile, you can explore the provided [example](./examples/example.py).

## Contributing

We welcome contributions! See our [contribution guidelines](./CONTRIBUTING) for more details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
