from tests.objects import Item, OneToMany

for item in Item.st_list_all():
    item.st_delete_button()

for one_to_many in OneToMany.st_list_all():
    one_to_many.st_delete_button(label="Delete OTM")
