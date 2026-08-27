import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='UserProfile',
                    fields=[
                        ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ('plan_type', models.CharField(choices=[('free', 'Free'), ('pro', 'Pro')], default='free', max_length=10)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('company_name', models.CharField(blank=True, max_length=150)),
                        ('industry_sector', models.CharField(blank=True, max_length=100)),
                        ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'analysis_userprofile',
                    },
                ),
            ],
        ),
    ]