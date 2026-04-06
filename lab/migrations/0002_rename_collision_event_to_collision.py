import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lab", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CollisionEvent",
            new_name="Collision",
        ),
        migrations.RenameField(
            model_name="eventimage",
            old_name="collision_event",
            new_name="collision",
        ),
        migrations.AlterField(
            model_name="collision",
            name="experiment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collisions",
                to="lab.experiment",
            ),
        ),
    ]
