from tests.objects import Item, OneToMany

for item in Item.sam_get_all():
    item.sam_delete_button()

for one_to_many in OneToMany.sam_get_all():
    one_to_many.sam_delete_button()
