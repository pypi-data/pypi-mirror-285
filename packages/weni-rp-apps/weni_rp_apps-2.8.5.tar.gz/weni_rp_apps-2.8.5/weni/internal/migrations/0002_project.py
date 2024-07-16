# Generated by Django 3.2.17 on 2023-02-07 18:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("orgs", "0090_auto_20211209_2120"),
        ("internal", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "org_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orgs.org",
                    ),
                ),
                ("project_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
            ],
            options={
                "db_table": "internal_project",
            },
            bases=("orgs.org",),
        ),
    ]
