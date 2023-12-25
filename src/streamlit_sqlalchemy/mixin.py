import logging
from typing import TYPE_CHECKING, Any, Optional

import streamlit as st
from sqlalchemy import Column, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql.sqltypes import Integer as SqlInteger


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(module)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DeclarativeBaseWithId(DeclarativeBase):
    id: Column


def _st_pretty_class_name(cls: type[DeclarativeBase]) -> str:
    return " ".join(cls.__tablename__.split("_")).title()


def _st_get_first_column_name(cls: type[DeclarativeBase]) -> Optional[str]:
    for col in cls.__mapper__._all_column_expressions:
        if col.name != "id":
            return col.name


def _st_repr(obj: DeclarativeBase) -> str:
    if hasattr(obj, "__st_repr__"):
        return getattr(obj, "__st_repr__")()

    first_column_name = _st_get_first_column_name(type(obj))
    if first_column_name is not None:
        return getattr(obj, first_column_name)

    return repr(obj)


def _st_order_by(cls: type[DeclarativeBaseWithId]) -> Optional[Column]:
    if hasattr(cls, "__st_order_by__"):
        return getattr(cls, "__st_order_by__")()

    first_column_name = _st_get_first_column_name(cls)
    if first_column_name is not None:
        return getattr(cls, first_column_name)

    return cls.id


if TYPE_CHECKING:
    """
    When type checking, we want to inherit from DeclarativeBaseWithId
    to get the id attribute, and because we know that the class will
    be a subclass of DeclarativeBase.
    """
    mixin_parent = DeclarativeBaseWithId
else:
    mixin_parent = object


class StreamlitAlchemyMixin(mixin_parent):
    """
    A mixin for Streamlit integration with SQLAlchemy models.
    """

    engine: Engine

    @classmethod
    def st_initialize(cls, engine: Engine):
        """
        Must be called before any other method to initialize the engine.
        """
        cls.engine = engine

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        """
        Overrides the default behavior to ensure 'st_'-prefixed attributes
        are only accessed after the 'st_initialize' method is called.
        """
        if item.startswith("st_"):
            self.__ensure_initialized()
            return getattr(self, item)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )

    @classmethod
    def st_pretty_class(cls):
        """
        Returns a pretty class name for display in the UI.
        """
        return _st_pretty_class_name(cls)

    @classmethod
    def st_get_session(cls) -> Session:
        """
        Returns a SQLAlchemy session.
        """
        return Session(cls.engine)

    @classmethod
    def st_list_all(cls):
        """
        Returns a list of all objects of this class.
        """
        query = cls.st_get_session().query(cls).order_by(_st_order_by(cls))
        return query.all()

    @classmethod
    def st_create_form(cls, defaults=None):
        """
        Renders a form to create a new object of this class.

        :param defaults: A dictionary of default values for the form.

        Example:
        ```
        User.st_create_form(defaults={"fullname": "John Doe"})
        ```
        """
        if defaults is None:
            defaults = {}

        st.markdown(f"### New {cls.st_pretty_class()}")
        with st.form(f"create_{cls.__name__}", clear_on_submit=True):
            kwargs = {}
            for column in cls.__table__.columns:
                if column.name == "id":
                    continue
                if column.name in defaults:
                    kwargs.update({column.name: defaults[column.name]})
                    continue

                input_function = cls._st_get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            " ".join(column.name.split("_")).title()
                        )
                    }
                )

            if any(default not in kwargs for default in defaults):
                logging.warning(
                    f"Some defaults {defaults} not found in {cls.st_pretty_class()} columns {kwargs.keys()}"
                )

            kwargs.update(defaults)

            submitted = st.form_submit_button(f"Create {cls.st_pretty_class()}")
            if submitted:
                for field in kwargs:
                    if any(
                        hasattr(kwargs[field], sql_field)
                        for sql_field in ["foreign_keys", "_sa_instance_state"]
                    ):
                        kwargs[field] = kwargs[field].id
                cls._st_create(**kwargs)

    @classmethod
    def st_update_select_form(cls):
        """
        Renders a form to select an object of this class to update.
        """
        selected_obj_to_update = st.selectbox(
            f"Select {cls.st_pretty_class()} to Update",
            cls.st_list_all(),
            index=None,
            format_func=lambda obj: _st_repr(obj),
        )
        if selected_obj_to_update:
            selected_obj_to_update.st_update_form()

    @classmethod
    def st_delete_select_form(cls):
        """
        Renders a form to select an object of this class to delete.
        """
        selected_obj_to_delete = st.selectbox(
            f"Select {cls.st_pretty_class()} to Delete",
            cls.st_list_all(),
            index=None,
            format_func=lambda obj: _st_repr(obj),
        )
        if selected_obj_to_delete:
            with st.form(f"delete_{cls.__name__}", clear_on_submit=True):
                if st.form_submit_button(f"Delete {cls.st_pretty_class()}"):
                    selected_obj_to_delete._st_session_delete()

    @classmethod
    def st_crud_tabs(cls, defaults=None):
        """
        Renders a tabbed interface for creating, updating, and deleting
        objects of this class.

        :param defaults: A dictionary of default values for the create form.

        Example:
        ```
        User.st_crud_tabs(defaults={"fullname": "John Doe"})
        ```
        """
        create_tab, update_tab, delete_tab = st.tabs(
            [
                f"Create {cls.st_pretty_class()}",
                f"Update {cls.st_pretty_class()}",
                f"Delete {cls.st_pretty_class()}",
            ]
        )
        with create_tab:
            cls.st_create_form(defaults=defaults)
        with update_tab:
            cls.st_update_select_form()
        with delete_tab:
            cls.st_delete_select_form()

    @classmethod
    def _st_get_input_function(cls, column):
        """
        Returns an input function for the given column.
        """
        if column.foreign_keys:
            # create a new set and pop the only element
            foreign_table_name = set(column.foreign_keys).pop().column.table.name

            class_ = cls._st_get_class_by_tablename(foreign_table_name)

            session = cls.st_get_session()
            choices = session.query(class_).all()  # type: ignore

            choices.sort(key=_st_order_by)

            return lambda *a, **kw: st.selectbox(
                *a, index=None, options=choices, format_func=_st_repr, **kw
            )

        if isinstance(column.type, SqlInteger):
            value = 0
            if column.default:
                value = column.default.arg
            if not isinstance(value, int):
                value = 0

            def number_input(*a, **kw):
                if "value" not in kw:
                    kw["value"] = value
                if "step" not in kw:
                    kw["step"] = 1
                return st.number_input(*a, **kw)

            return number_input
        return st.text_input

    @classmethod
    def _st_get_class_by_tablename(cls, tablename):
        """
        Returns the class for the given tablename.

        Inspired by: https://stackoverflow.com/a/23754464/11547305
        Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for c in cls.registry._class_registry.values():
            if hasattr(c, "__tablename__") and getattr(c, "__tablename__") == tablename:
                return c
        raise RuntimeError(f"Class with tablename {tablename} not found")

    @classmethod
    def _st_create(cls, **kwargs):
        """
        Creates a new object of this class.
        """
        obj = cls(**kwargs)
        obj._st_session_add()

    @classmethod
    def _st_update(cls, **kwargs):
        """
        Updates an existing object of this class.
        """
        obj = cls(**kwargs)
        obj._st_session_update()

    def st_edit_button(self, label, kwargs):
        """
        Renders a button to edit this object.

        :param label: The label for the button.
        :param kwargs: The keyword arguments to pass to the update method.

        Example:
        ```
        user.st_edit_button("Deactivate", {"active": False})
        ```
        """
        class_name = self.__class__.__name__
        st.button(
            label,
            on_click=self._st_update,
            kwargs=kwargs,
            key=f"{class_name}_{self.id}",
        )

    def st_delete_button(self):
        """
        Renders a button to delete this object.
        """
        class_name = self.__class__.__name__
        st.button(
            f"Delete {self.st_pretty_class()}",
            on_click=self._st_session_delete,
            key=f"{class_name}_{self.id}",
        )

    def st_update_form(self):
        """
        Renders a form to update this object.
        """
        with st.form(f"update_{self.id}"):
            kwargs = {
                column.name: getattr(self, column.name)
                for column in self.__table__.columns
            }
            for column in self.__table__.columns:
                if column.name == "id" or column.name.endswith("_id"):
                    continue

                input_function = self._st_get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            (" ".join(column.name.split("_")).title()),
                            value=kwargs[column.name],
                        )
                    }
                )

            if st.form_submit_button(f"Update {self.st_pretty_class()}"):
                for field in kwargs:
                    if field.endswith("_id"):
                        kwargs[field] = kwargs[field].id
                self._st_update(**kwargs)

    def _get_first_column_name(self, cls: type[DeclarativeBase]) -> Optional[str]:
        """
        Returns the first column name of the given class.
        """
        for col in cls.__mapper__._all_column_expressions:
            if col.name != "id":
                return col.name

    def _st_session_add(self):
        """
        Adds this object to the session.
        """
        session = self.st_get_session()
        with session.begin():
            try:
                session.add(self)
            except IntegrityError as e:
                logging.exception(
                    f"*Error creating {self.st_pretty_class()} {_st_repr(self)}!*\n\n{e.orig}"
                )
            else:
                logging.info(f"{self.st_pretty_class()} Added")

    def _st_session_delete(self):
        """
        Deletes this object from the session.
        """
        session = self.st_get_session()
        with session.begin():
            try:
                session.delete(self)
            except IntegrityError as e:
                logging.exception(
                    f"*Error deleting {self.st_pretty_class()} {_st_repr(self)}!*\n\n{e.orig}"
                )
            else:
                logging.info(f"{self.st_pretty_class()} Deleted")

    def _st_session_update(self):
        """
        Updates this object in the session.
        """
        session = self.st_get_session()
        with session.begin():
            try:
                session.query(self.__class__).filter_by(id=self.id).update(
                    {
                        column.name: getattr(self, column.name)
                        for column in self.__table__.columns
                    }
                )
            except IntegrityError as e:
                logging.exception(
                    f"*Error updating {self.st_pretty_class()} {_st_repr(self)}!*\n\n{e.orig}"
                )
            else:
                logging.info(f"{self.st_pretty_class()} Updated")

    def __ensure_initialized(self):
        """
        Ensures that the engine is initialized.
        """
        if not hasattr(self, "engine"):
            raise RuntimeError(
                "You must call StreamlitAlchemyMixin.st_initialize(engine) "
                "before using any StreamlitAlchemyMixin methods."
            )
