from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0005_userprofile_company_name_userprofile_industry_sector'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='UserProfile',
                ),
            ],
        ),
    ]