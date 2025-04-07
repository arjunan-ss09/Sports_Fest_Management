from django.db import migrations, models
import django.db.models.deletion

def copy_college_data(apps, schema_editor):
    Team = apps.get_model('management', 'Team')
    College = apps.get_model('management', 'College')
    # For each team, copy the old text value from the "college" column.
    for team in Team.objects.all():
        # The old value is still in the underlying dict; it should be the raw text.
        old_college_value = team.__dict__.get('college')
        if old_college_value:
            # Get or create a College object with that name.
            college_obj, created = College.objects.get_or_create(name=old_college_value)
            team.new_college = college_obj
            team.save()

class Migration(migrations.Migration):

    dependencies = [
        # Replace '000X_previous_migration' with the actual latest migration file name
        ('management', '0003_alter_team_college'),
    ]

    operations = [
        # 1. Add a new temporary field "new_college" as a ForeignKey to College (nullable)
        migrations.AddField(
            model_name='team',
            name='new_college',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='management.College'),
        ),
        # 2. Copy data from the old "college" (text field) to "new_college"
        migrations.RunPython(copy_college_data, reverse_code=migrations.RunPython.noop),
        # 3. Remove the old "college" field
        migrations.RemoveField(
            model_name='team',
            name='college',
        ),
        # 4. Rename "new_college" to "college"
        migrations.RenameField(
            model_name='team',
            old_name='new_college',
            new_name='college',
        ),
        # 5. (Optional) Enforce non-nullability on "college"
        migrations.AlterField(
            model_name='team',
            name='college',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.College'),
        ),
    ]
