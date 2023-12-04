import sqlalchemy
import streamlit as st
from sqlalchemy.orm import sessionmaker


class StreamlitAlchemyMixin:
    # Must be called before any other method
    @classmethod
    def sam_initialize(cls, base_class, engine):
        cls.base_class = base_class
        cls.engine = engine

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def sam_get_all(cls):
        query = cls.sam_get_session().query(cls)
        return cls._sam_order_query(query).all()

    @classmethod
    def sam_get_session(cls):
        return sessionmaker(bind=cls.engine)()

    @classmethod
    def sam_create(cls, *args, **kwargs):
        obj = cls(**kwargs)
        session = cls.sam_get_session()
        try:
            session.add(obj)
            session.commit()
            st.success(f"{cls.__name__} Added")
        except sqlalchemy.exc.IntegrityError as e:
            session.rollback()
            st.error(e)
            st.error(f"{cls.__name__} {obj.name} already exists")
        except Exception as e:
            session.rollback()
            st.error(e)

    @classmethod
    def sam_create_form(cls):
        st.markdown(f"### New {cls.__name__}")
        with st.form(f"create_{cls.__name__}", clear_on_submit=True):
            kwargs = {}
            for column in cls.__table__.columns:
                if column.name == "id":
                    continue

                input_function = cls._sam_get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            " ".join(column.name.split("_")).title()
                        )
                    }
                )

            submitted = st.form_submit_button(f"Create {cls.__name__}")
            if submitted:
                for field in kwargs:
                    if field.endswith("_id"):
                        kwargs[field] = kwargs[field].id
                cls.sam_create(**kwargs)

    @classmethod
    def sam_update_select_form(cls):
        selected_obj_to_update = st.selectbox(
            f"Select {cls.__name__} to Update",
            cls.sam_get_all(),
            index=None,
            format_func=lambda obj: obj._sam_repr(),
        )
        if selected_obj_to_update:
            selected_obj_to_update.sam_update_form()

    @classmethod
    def sam_delete_select_form(cls):
        selected_obj_to_delete = st.selectbox(
            f"Select {cls.__name__} to Delete",
            cls.sam_get_all(),
            index=None,
            format_func=lambda obj: obj._sam_repr(),
        )
        if selected_obj_to_delete:
            with st.form(f"delete_{cls.__name__}", clear_on_submit=True):
                if st.form_submit_button(f"Delete {cls.__name__}"):
                    selected_obj_to_delete._sam_delete()

    @classmethod
    def sam_crud_tabs(cls):
        create_tab, update_tab, delete_tab = st.tabs(
            [
                f"Create {cls.__name__}",
                f"Update {cls.__name__}",
                f"Delete {cls.__name__}",
            ]
        )
        with create_tab:
            cls.sam_create_form()
        with update_tab:
            cls.sam_update_select_form()
        with delete_tab:
            cls.sam_delete_select_form()

    @classmethod
    def _sam_get_class_by_tablename(cls, tablename):
        """
        Inspired by: https://stackoverflow.com/a/23754464/11547305
        Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for c in cls.base_class.registry._class_registry.values():
            if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
                return c

    @classmethod
    def _sam_get_first_column_name(cls):
        for col in cls.__mapper__._all_column_expressions:
            if col.name != "id":
                return col.name

    @classmethod
    def _sam_get_input_function(self, column):
        if column.foreign_keys:
            class_ = self._sam_get_class_by_tablename(
                # create a new set and pop the only element
                set(column.foreign_keys)
                .pop()
                .column.table.name,
            )

            return lambda *a, **kw: st.selectbox(
                *a,
                options=[obj for obj in class_.sam_get_all()],
                index=None,
                format_func=lambda obj: obj._sam_repr(),
                **kw,
            )

        if isinstance(column.type, sqlalchemy.sql.sqltypes.Integer):
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

    def sam_delete_button(self):
        st.button(f"Delete {self.__class__.__name__}", on_click=self._sam_delete)

    def sam_update_form(self):
        cls = self.__class__  # TODO: remove this dependency
        with st.form(f"update_{self.id}"):
            kwargs = {
                column.name: getattr(self, column.name)
                for column in cls.__table__.columns
            }
            for column in cls.__table__.columns:
                if column.name == "id" or column.name.endswith("_id"):
                    continue

                input_function = cls._sam_get_input_function(column)
                kwargs.update(
                    {
                        column.name: input_function(
                            (" ".join(column.name.split("_")).title()),
                            value=kwargs[column.name],
                        )
                    }
                )

            if st.form_submit_button(f"Update {cls.__name__}"):
                for field in kwargs:
                    if field.endswith("_id"):
                        kwargs[field] = kwargs[field].id
                self._sam_update(**kwargs)
                st.rerun()

    def _sam_delete(self):
        cls = self.__class__
        session = self.sam_get_session()
        obj = session.query(cls).get(self.id)
        try:
            session.delete(obj)
            session.commit()
            st.success(f"{cls.__name__} Deleted")
        except Exception as e:
            session.rollback()
            st.error(e)

    def _sam_update(self, **kwargs):
        session = self.sam_get_session()
        session.query(self.__class__).filter_by(id=self.id).update(kwargs)
        try:
            session.commit()
            st.success(f"{self.__class__.__name__} Updated")
        except Exception as e:
            session.rollback()
            st.error(e)

    # TO BE OVERRIDEN

    @classmethod
    def _sam_order_query(cls, query):
        """Return a query object that orders the query by the first column.
        Override this to provide a better default ordering.
        """
        first_column_name = cls._sam_get_first_column_name()
        if first_column_name:
            query = query.order_by(getattr(cls, first_column_name))
        return query

    def _sam_repr(self):
        """Return a string representation of this object.
        By default this is the first column's value. Override this
        to provide a better representation of your object.
        """
        first_column_name = self._sam_get_first_column_name()
        if first_column_name:
            return getattr(self, first_column_name)
        return super().__repr__()
