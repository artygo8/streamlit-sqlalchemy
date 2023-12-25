import os
import time
from sqlalchemy import create_engine
from streamlit.testing.v1 import AppTest
from streamlit_sqlalchemy import StreamlitAlchemyMixin
from tests.objects import Item, OneToMany


def test_create_form_no_items(database):
    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/create_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.text_input[0].label == "Name"
    assert at.number_input[0].label == "Count"
    assert at.button[0].label == "Create Item"

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == []
    assert at.button[1].label == "Create One To Many"


def test_create_form_one_item(database):
    # create item
    Item._st_create(name="Test", count=1)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/create_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == ["Test"]
    assert at.button[1].label == "Create One To Many"


def test_create_form_two_items(database):
    # create item
    Item._st_create(name="Test", count=1)
    Item._st_create(name="Test2", count=2)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/create_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # second form
    assert at.text_input[1].label == "First Field"
    assert at.selectbox[0].label == "Test Item Id"
    assert at.selectbox[0].options == ["Test", "Test2"]
    assert at.button[1].label == "Create One To Many"


def test_update_select_form_no_items(database):
    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/update_select_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == []
    assert len(at.button) == 0

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_update_select_form_one_item(database):
    # create item
    Item._st_create(name="Test", count=1)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/update_select_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == ["Test"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_update_select_form_several_items(database):
    # create item
    Item._st_create(name="A", count=1)
    Item._st_create(name="C", count=2)
    Item._st_create(name="B", count=3)

    OneToMany._st_create(first_field="FF", test_item_id=None)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/update_select_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Update"
    assert at.selectbox[0].options == ["A", "B", "C"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Update"
    assert at.selectbox[1].options == ["FF"]
    assert len(at.button) == 0


def test_delete_form_no_items(database):
    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/delete_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Delete"
    assert at.selectbox[0].options == []
    assert len(at.button) == 0

    # second form
    assert at.selectbox[1].label == "Select One To Many to Delete"
    assert at.selectbox[1].options == []
    assert len(at.button) == 0


def test_delete_form_several_items(database):
    # create item
    Item._st_create(name="A", count=1)
    Item._st_create(name="C", count=2)
    Item._st_create(name="B", count=3)

    OneToMany._st_create(first_field="FF", test_item_id=None)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/delete_form.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.selectbox[0].label == "Select Item to Delete"
    assert at.selectbox[0].options == ["A", "B", "C"]

    # second form
    assert at.selectbox[1].label == "Select One To Many to Delete"
    assert at.selectbox[1].options == ["FF"]
    assert len(at.button) == 0


def test_delete_button_several_items(database):
    # create item
    Item._st_create(name="A", count=1)
    Item._st_create(name="C", count=2)
    Item._st_create(name="B", count=3)

    OneToMany._st_create(first_field="FF", test_item_id=None)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/delete_button.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.button[0].label == "Delete Item"
    assert at.button[1].label == "Delete Item"
    assert at.button[2].label == "Delete Item"
    assert at.button[3].label == "Delete One To Many"
    assert len(at.button) == 4
