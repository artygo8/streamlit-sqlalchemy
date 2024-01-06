from streamlit.testing.v1 import AppTest
from tests.objects import Item, OneToMany, SuperItem


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
    assert at.selectbox[0].label == "Test Item"
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
    assert at.selectbox[0].label == "Test Item"
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
    assert at.selectbox[0].label == "Test Item"
    assert at.selectbox[0].options == ["Test", "Test2"]
    assert at.button[1].label == "Create One To Many"


def test_create_form_advanced(database):
    SuperItem._st_create(name="Test", count=1)
    SuperItem._st_create(name="Test2", count=3)
    SuperItem._st_create(name="Test3", count=2)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/create_form_advanced.py",
        default_timeout=10,
    ).run(timeout=10)

    assert len(at.text_input) == 1
    assert at.text_input[0].label == "Name"

    assert len(at.text_area) == 2
    assert at.text_area[0].label == "Another String"
    assert at.text_area[1].label == "Text"

    assert len(at.number_input) == 2
    assert at.number_input[0].label == "Count"
    assert at.number_input[0].step == 1
    assert at.number_input[1].label == "My Float"
    assert at.number_input[1].step == 0.1

    assert len(at.date_input) == 2
    assert at.date_input[0].label == "Due Datetime"
    assert at.date_input[1].label == "Creating Date"

    assert len(at.time_input) == 2
    assert at.time_input[0].label == "Due Datetime"
    assert at.time_input[1].label == "Closing Time"

    assert len(at.selectbox) == 2
    assert at.selectbox[0].label == "My Bool"
    assert at.selectbox[0].options == ["True", "False"]
    assert at.selectbox[1].label == "Super Item"
    assert at.selectbox[1].options == ["Test (1)", "Test3 (2)", "Test2 (3)"]

    assert len(at.checkbox) == 1
    assert at.checkbox[0].label == "My Other Bool"
    assert at.checkbox[0].value is True

    assert at.button[0].label == "Create Advanced Object"


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
    assert at.button[0].label == "Delete"
    assert at.button[1].label == "Delete"
    assert at.button[2].label == "Delete"
    assert at.button[3].label == "Delete OTM"
    assert len(at.button) == 4


def test_edit_button(database):
    # create item
    Item._st_create(name="A", count=1)
    Item._st_create(name="C", count=2)
    Item._st_create(name="B", count=3)

    OneToMany._st_create(first_field="FF", test_item_id=None)

    at = AppTest.from_file(
        "tests/streamlit_sqlalchemy/mixin/edit_button.py",
        default_timeout=10,
    ).run(timeout=10)

    # first form
    assert at.button[0].label == "Add 1"
    assert at.button[1].label == "Add 1"
    assert at.button[2].label == "Add 1"
    assert len(at.button) == 3
