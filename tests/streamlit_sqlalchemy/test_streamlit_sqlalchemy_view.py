import os
from textwrap import dedent
import time
from streamlit.testing.v1 import AppTest
from streamlit_sqlalchemy import declarative_streamlit_view
from tests.objects import Item, OneToMany


def test_create_form_no_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)
            item_view = StreamlitView(Item)
            item_view.create_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.create_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.text_input[0].label == "Name"
    assert at.number_input[0].label == "Count"
    assert at.button[0].label == "Create Item"

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == []
    assert at.button[1].label == "Create One To Many"


def test_create_form_one_item():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="Test", count=1))
            session.commit()

            item_view = StreamlitView(Item)
            item_view.create_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.create_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == ["Test"]
    assert at.button[1].label == "Create One To Many"


def test_create_form_two_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="Test", count=1))
            session.add(Item(name="Test2", count=2))
            session.commit()

            item_view = StreamlitView(Item)
            item_view.create_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.create_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == ["Test", "Test2"]
    assert at.button[1].label == "Create One To Many"


def test_update_select_form_no_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            item_view = StreamlitView(Item)
            item_view.update_select_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.update_select_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == []
    assert len(at.button) == 0

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_update_select_form_one_item():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="Test", count=1))
            session.commit()

            item_view = StreamlitView(Item)
            item_view.update_select_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.update_select_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == ["Test"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_update_select_form_several_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="A", count=1))
            session.add(Item(name="B", count=3))
            session.add(Item(name="C", count=2))
            session.add(OneToMany(first_field="FF", test_item_id=None))
            session.commit()

            item_view = StreamlitView(Item)
            item_view.update_select_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.update_select_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == ["A", "B", "C"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == ["FF"]
    assert len(at.button) == 0


def test_delete_form_no_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            item_view = StreamlitView(Item)
            item_view.delete_select_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.delete_select_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Delete"
    assert at.selectbox[0].options == []
    assert len(at.button) == 0

    # second form
    assert at.selectbox[1].label == "Select One To Many to Delete"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_delete_form_several_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="A", count=1))
            session.add(Item(name="B", count=3))
            session.add(Item(name="C", count=2))
            session.add(OneToMany(first_field="FF", test_item_id=None))
            session.commit()

            item_view = StreamlitView(Item)
            item_view.delete_select_form()

            one_to_many_view = StreamlitView(OneToMany)
            one_to_many_view.delete_select_form()

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Delete"
    assert at.selectbox[0].options == ["A", "B", "C"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Delete"
    assert at.selectbox[1].options == ["FF"]
    assert len(at.button) == 0


def test_delete_button_several_items():
    def fct():
        from tests.objects import Item, OneToMany, engine_ctx
        from streamlit_sqlalchemy import declarative_streamlit_view

        with engine_ctx() as engine:
            StreamlitView = declarative_streamlit_view(engine)

            session = StreamlitView.get_session()
            session.add(Item(name="A", count=1))
            session.add(Item(name="B", count=3))
            session.add(Item(name="C", count=2))
            session.add(OneToMany(first_field="FF", test_item_id=None))
            session.commit()

            item_view = StreamlitView(Item)

            session = item_view.get_session()
            for item in session.query(Item).all():
                item_view.delete_button(item)

            one_to_many_view = StreamlitView(OneToMany)

            for one_to_many in session.query(OneToMany).all():
                one_to_many_view.delete_button(one_to_many)

    at = AppTest.from_function(fct, default_timeout=10).run(timeout=10)

    # first form
    assert at.button[0].label == "Delete Item"
    assert at.button[1].label == "Delete Item"
    assert at.button[2].label == "Delete Item"
    assert at.button[3].label == "Delete One To Many"
    assert len(at.button) == 4
