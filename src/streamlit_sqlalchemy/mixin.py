import logging
from typing import TYPE_CHECKING, Any, Optional

import streamlit as st
from hashlib import md5
from sqlalchemy import Boolean, Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.sqltypes import Integer as SqlInteger
from streamlit.connections.sql_connection import SQLConnection

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


def _get_unique_hash(**kwargs) -> str:
    return md5((str(kwargs)).encode("utf-8")).hexdigest()


def _get_pretty_column_name(name: str) -> str:
    if name.endswith("_id"):
        name = name[:-3]
    return " ".join(name.split("_")).title()


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

    @classmethod
    def st_initialize(cls, connection: Optional[SQLConnection]):
        """
        Must be called before any other method to initialize the engine.
        """
        if cls._st_is_initialized():
            logging.warning(
                f"StreamlitAlchemyMixin.st_initialize called multiple times for {cls.__name__}"
            )
            return

        cls.__connection = connection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        """
        Overrides the default behavior to ensure 'st_'-prefixed attributes
        are only accessed after the 'st_initialize' method is called.
        """
        if item.startswith("st_"):
            self.__st_ensure_initialized()
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
    def st_get_connection(cls) -> SQLConnection:
        """
        Returns a SQLAlchemy session.
        """
        assert cls.__connection is not None
        return cls.__connection

    @classmethod
    def st_list_all(cls):
        """
        Returns a list of all objects of this class.
        """
        conn = cls.st_get_connection()
        result = None
        with conn.session as session:
            query = session.query(cls).order_by(_st_order_by(cls))
            result = query.all()
        return result

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

        unique_hash = _get_unique_hash(**defaults)
        with st.form(
            f"create_{cls.__name__}_{unique_hash}", clear_on_submit=True, border=False
        ):
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
                            _get_pretty_column_name(column.name),
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
            if selected_obj_to_update.st_update_form():
                st.rerun()

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
            with st.form(f"delete_{cls.__name__}", clear_on_submit=True, border=False):
                if st.form_submit_button(f"Delete {cls.st_pretty_class()}"):
                    selected_obj_to_delete._st_session_delete()
                    st.rerun()

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

            conn = cls.st_get_connection()
            with conn.session as session:
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

        if isinstance(column.type, Boolean):
            value = None
            if column.default:
                value = column.default.arg
            if not isinstance(value, bool):
                value = None

            def boolean_select(*a, **kw):
                options = [True, False]
                selected = kw.pop("value") if "value" in kw else value
                index = options.index(selected) if selected is not None else None
                return st.selectbox(*a, options=[True, False], index=index, **kw)

            return boolean_select

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
    def _st_is_initialized(cls) -> bool:
        """
        Returns whether or not the engine is initialized.
        """
        return hasattr(cls, "__connection")

    @classmethod
    def _st_create(cls, **kwargs) -> None:
        """
        Creates a new object of this class.
        """
        obj = cls(**kwargs)
        conn = cls.st_get_connection()
        with conn.session as session, session.begin():
            try:
                session.add(obj)
            except IntegrityError as e:
                logging.exception(
                    f"*Error creating {cls.st_pretty_class()} {_st_repr(obj)}!*\n\n{e.orig}"
                )
            else:
                logging.info(f"{cls.st_pretty_class()} Added")

    @classmethod
    def _st_update(cls, **kwargs) -> None:
        """
        Updates an existing object of this class.
        """
        obj = cls(**kwargs)
        conn = cls.st_get_connection()
        with conn.session as session, session.begin():
            try:
                session.query(cls).filter_by(id=obj.id).update(
                    {
                        column.name: getattr(obj, column.name)
                        for column in obj.__table__.columns
                    }
                )
            except IntegrityError as e:
                logging.exception(
                    f"*Error updating {cls.st_pretty_class()} {_st_repr(obj)}!*\n\n{e.orig}"
                )
            else:
                logging.info(f"{cls.st_pretty_class()} Updated")

    def st_edit_button(self, label, values: dict[str, Any], **kwargs) -> bool:
        """
        Renders a button to edit this object.

        :param label: The label for the button.
        :param values: The keyword arguments to pass to the update method.
        :param kwargs: Additional keyword arguments to pass to the button.

        Example:
        ```
        user.st_edit_button("Deactivate", {"active": False})
        ```
        """
        unique_hash = _get_unique_hash(label=label, **values, **kwargs)

        def _update(**kw):
            for k, v in kw.items():
                setattr(self, k, v)
            self._st_session_update()

        return st.button(
            label,
            on_click=_update,
            kwargs=values,
            key=f"edit_{self.__class__.__name__}_{self.id}_{unique_hash}",
            **kwargs,
        )

    def st_delete_button(self, label="Delete", **kwargs):
        """
        Renders a button to delete this object.

        :param label: The label for the button.
        :param kwargs: Additional keyword arguments to pass to the button.
        """

        st.button(
            label=label,
            on_click=self._st_session_delete,
            key=f"delete_{self.__class__.__name__}_{self.id}",
            **kwargs,
        )

    def st_update_form(self):
        """
        Renders a form to update this object.
        """

        with st.form(f"update_{self.id}", border=False):
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
                            _get_pretty_column_name(column.name),
                            value=kwargs[column.name],
                        )
                    }
                )

            submitted = st.form_submit_button(f"Update {self.st_pretty_class()}")
            if submitted:
                for field in kwargs:
                    if field.endswith("_id"):
                        kwargs[field] = kwargs[field].id
                self._st_update(**kwargs)
        return submitted

    def _get_first_column_name(self, cls: type[DeclarativeBase]) -> Optional[str]:
        """
        Returns the first column name of the given class.
        """
        for col in cls.__mapper__._all_column_expressions:
            if col.name != "id":
                return col.name

    def _st_session_delete(self):
        """
        Deletes this object from the session.
        """
        conn = self.st_get_connection()
        with conn.session as session, session.begin():
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
        This is not the same as the st_update method, which creates
        a new object and replaces the old one.
        """
        conn = self.st_get_connection()
        with conn.session as session, session.begin():
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

    def __st_ensure_initialized(self):
        """
        Ensures that the engine is initialized.
        """
        if not self._st_is_initialized():
            raise RuntimeError(
                "You must call StreamlitAlchemyMixin.st_initialize(engine) "
                "before using any StreamlitAlchemyMixin methods."
            )
