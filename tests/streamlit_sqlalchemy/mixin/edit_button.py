from tests.objects import Item, OneToMany

for item in Item.st_list_all():
    item.st_edit_button("Add 1", {"count": item.count + 1})
