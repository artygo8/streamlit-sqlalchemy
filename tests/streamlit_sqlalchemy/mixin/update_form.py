from tests.objects import OneToMany, Item

item = next(i for i in Item.st_list_all())
item.st_update_form()

for o2m in OneToMany.st_list_all():
    o2m.st_update_form()
