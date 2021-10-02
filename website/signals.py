from django.db.models.signals import post_delete,post_save,pre_save,pre_init
from django.dispatch import Signal,receiver
from django.db import models

""" Whenever ANY model is deleted, if it has a file field on it, delete the associated file too"""

@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_unused_files(sender, instance, field, instance_file_field)

""" Only delete the file if no other instances of that model are using it"""

def delete_unused_files(model, instance, field, instance_file_field):
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        print("We are about to delete:",instance_file_field)
        instance_file_field.delete(False)


