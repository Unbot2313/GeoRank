from django.db import migrations


def fix_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='analysis', model='userprofile').update(app_label='accounts')


def reverse_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='accounts', model='userprofile').update(app_label='analysis')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('analysis', '0006_move_userprofile_to_accounts'),
    ]

    operations = [
        migrations.RunPython(fix_content_type, reverse_content_type),
    ]