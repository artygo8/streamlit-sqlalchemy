from typing import Optional

import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql.sqltypes import Integer as SqlInteger


def _pretty_class_name(cls: type[DeclarativeBase]) -> str:
    return " ".join(cls.__tablename__.split("_")).title()


class BaseStreamlitSqlAlchemyView:
    engine: Engine

    def __init__(self, sql_cls: type[DeclarativeBase]) -> None:
        self.__ensure_has_id(sql_cls)
        self.sql_cls = sql_cls

    @staticmethod
    def _format_exception(e) -> str:
        return str(e.orig if isinstance(e, IntegrityError) else e)

    @classmethod
    def get_session(cls) -> Session:
        return Session(cls.engine)

    @property
    def pretty_name(self) -> str:
        return _pretty_class_name(self.sql_cls)

    def get_all(self, cls: type[DeclarativeBase]) -> list[DeclarativeBase]:
        query = self.get_session().query(cls)
        return query.all()


    def create_form(self, defaults=None):
        if defaults is None:
            defaults = {}

        st.markdown(f"### New {self.pretty_name}")
        with st.form(f"create_{self.sql_cls.__name__}", clear_on_submit=True):
            kwargs = {}
            for column in self.sql_cls.__table__.columns:
                if column.name == "id":
                    continue
                if column.name in defaults:
                    kwargs.update({column.name: defaults[column.name]})
                    continue

                input_function = self._get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            " ".join(column.name.split("_")).title()
                        )
                    }
                )

            if any(default not in kwargs for default in defaults):
                st.warning(
                    f"Some defaults {defaults} not found in {self.pretty_name} "
                    f"columns {kwargs.keys()}"
                )
            kwargs.update(defaults)

            submitted = st.form_submit_button(f"Create {self.pretty_name}")
            if submitted:
                for field in kwargs:
                    if any(
                        hasattr(kwargs[field], sql_field)
                        for sql_field in ["foreign_keys", "_sa_instance_state"]
                    ):
                        kwargs[field] = kwargs[field].id
                self._obj_create(**kwargs)

    def update_select_form(self):
        selected_obj_to_update = st.selectbox(
            f"Select {self.pretty_name} to Update",
            self.get_all(self.sql_cls),
            index=None,
            format_func=lambda obj: self._obj_repr(obj),
        )
        if selected_obj_to_update is not None:
            self.update_form(selected_obj_to_update)

    def delete_select_form(self):
        selected_obj_to_delete = st.selectbox(
            f"Select {self.pretty_name} to Delete",
            self.get_all(self.sql_cls),
            index=None,
            format_func=lambda obj: self._obj_repr(obj),
        )
        if selected_obj_to_delete:
            with st.form(f"delete_{self.pretty_name}", clear_on_submit=True):
                if st.form_submit_button(f"Delete {self.pretty_name}"):
                    self._session_delete(selected_obj_to_delete)

    def crud_tabs(self):
        create_tab, update_tab, delete_tab = st.tabs(
            [
                f"Create {self.pretty_name}",
                f"Update {self.pretty_name}",
                f"Delete {self.pretty_name}",
            ]
        )
        with create_tab:
            self.create_form()
        with update_tab:
            self.update_select_form()
        with delete_tab:
            self.delete_select_form()

    def delete_button(self, obj: DeclarativeBase):
        st.button(
            f"Delete {self.pretty_name}",
            on_click=lambda: self._session_delete(obj),
            key=f"{self.pretty_name}_{obj.id}",  # type: ignore
        )

    def update_form(self, obj: DeclarativeBase):
        with st.form(f"update_{self.sql_cls.__name__}_{obj.id}"):  # type: ignore
            kwargs = {
                column.name: getattr(obj, column.name)
                for column in obj.__table__.columns
            }
            for column in obj.__table__.columns:
                if column.name == "id" or column.foreign_keys:
                    continue

                input_function = self._get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            (" ".join(column.name.split("_")).title()),
                            value=kwargs[column.name],
                        )
                    }
                )

            if st.form_submit_button(f"Update {self.pretty_name}"):
                for field in kwargs:
                    if hasattr(kwargs[field], "foreign_keys"):
                        kwargs[field] = kwargs[field].id
                self._obj_update(**kwargs)

    def _get_class_by_tablename(self, tablename):
        """
        Inspired by: https://stackoverflow.com/a/23754464/11547305
        Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for c in self.sql_cls.registry._class_registry.values():
            if hasattr(c, "__tablename__") and getattr(c, "__tablename__") == tablename:
                return c

    def _get_first_column_name(self, cls: type[DeclarativeBase]) -> Optional[str]:
        for col in cls.__mapper__._all_column_expressions:
            if col.name != "id":
                return col.name

    def _get_input_function(self, column):
        if column.foreign_keys:
            # create a new set and pop the only element
            foreign_table_name = set(column.foreign_keys).pop().column.table.name
            class_ = self._get_class_by_tablename(foreign_table_name)

            session = self.get_session()
            choices = sorted(session.query(class_).all(), key=self._obj_order_by)

            return lambda *a, **kw: st.selectbox(
                *a, index=None, options=choices, format_func=self._obj_repr, **kw
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

    def _obj_create(self, **kwargs):
        obj = self.sql_cls(**kwargs)
        self._session_add(obj)

    def _obj_update(self, **kwargs):
        obj = self.sql_cls(**kwargs)
        self._session_update(obj)

    def _obj_delete(self, **kwargs):
        obj = self.sql_cls(**kwargs)
        self._session_delete(obj)

    def _obj_repr(self, obj: DeclarativeBase) -> str:
        if hasattr(obj, "__st_repr__"):
            return obj.__st_repr__()  # type: ignore

        first_column_name = self._get_first_column_name(type(obj))
        if first_column_name is not None:
            return str(getattr(obj, first_column_name))

        return str(obj)

    def _obj_order_by(self, obj: DeclarativeBase):
        if hasattr(obj, "__st_order_by__"):
            return obj.__st_order_by__()  # type: ignore

        first_column_name = self._get_first_column_name(type(obj))
        if first_column_name is not None:
            return getattr(obj, first_column_name)

        return obj.id  # type: ignore

    def _session_add(self, obj: DeclarativeBase):
        class_name = _pretty_class_name(type(obj))
        session = self.get_session()
        with session.begin():
            try:
                session.add(obj)
            except Exception as e:
                st.error(
                    f"*Error creating {class_name} {obj}!*\n\n"
                    f"{self._format_exception(e)}"
                )
            else:
                st.success(f"{class_name} Added")

    def _session_delete(self, obj: DeclarativeBase):
        class_name = _pretty_class_name(type(obj))
        session = self.get_session()
        with session.begin():
            try:
                session.delete(obj)
            except Exception as e:
                st.error(
                    f"*Error deleting {class_name} {obj}!*\n\n"
                    f"{self._format_exception(e)}"
                )
            else:
                st.success(f"{class_name} Deleted")

    def _session_update(self, obj: DeclarativeBase):
        session = self.get_session()
        with session.begin():
            try:
                session.query(self.sql_cls).filter_by(id=obj.id).update(  # type: ignore
                    {
                        column.name: getattr(obj, column.name)
                        for column in obj.__table__.columns
                    }
                )
            except Exception as e:
                st.error(
                    f"*Error updating {self.pretty_name} {self._obj_repr(obj)}!*\n\n"
                    f"{self._format_exception(e)}"
                )
            else:
                st.success(f"{self.pretty_name} Updated")

    def __ensure_has_id(self, sql_cls: type[DeclarativeBase]) -> None:
        assert hasattr(sql_cls, "id"), f"{sql_cls} does not have an id column"


def declarative_streamlit_view(engine: Engine) -> type[BaseStreamlitSqlAlchemyView]:
    cls = type(
        "StreamlitSqlAlchemyView",
        (BaseStreamlitSqlAlchemyView,),
        {"engine": engine},
    )
    return cls
