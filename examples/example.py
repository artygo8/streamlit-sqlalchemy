import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

from examples.models import Base, Task, User
from streamlit_sqlalchemy import StreamlitAlchemyMixin


@st.cache_resource
def _configure_logging():
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            st.toast(log_entry)

    logger = logging.getLogger()
    if not any(isinstance(h, StreamlitHandler) for h in logger.handlers):
        logger.addHandler(StreamlitHandler())
    logger.setLevel(logging.INFO)


def _display_inline():
    """
    Make the columns inline.
    (https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line)
    """
    st.markdown(
        """
        <style>
            div[data-testid="column"] {
                width: fit-content !important;
                flex: unset;
            }
            div[data-testid="column"] * {
                width: fit-content !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_single_task(task):
    col1, col2, col3 = st.columns([1, 1, 1])
    if task.done:
        col1.write(f" - ~~{task.description}~~")
        with col2:
            task.st_delete_button()
    else:
        if task.due_date:
            date_color = "red" if task.due_date < datetime.now() else "green"
            col1.write(
                f" - {task.description} (:{date_color}[{task.due_date.strftime('%H:%M - %d.%m.%Y')}])"
            )
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

    # initialize the StreamlitAlchemyMixin
    StreamlitAlchemyMixin.st_initialize(connection=CONNECTION)

    # make the columns inline
    _display_inline()

    # use the logs as toasts in the app
    _configure_logging()

    # the actual app
    app()


if __name__ == "__main__":
    # initialize the database connection
    # (see https://docs.streamlit.io/library/api-reference/connections/st.connection)
    CONNECTION = st.connection("example_db", type="sql")
    main()
