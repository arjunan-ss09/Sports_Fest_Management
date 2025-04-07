from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # Replace '000X_previous_migration' with your latest migration filename (without .py)
        ('management', '0004_convert_team_college'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Disable foreign key constraints for the update
                PRAGMA foreign_keys = OFF;
                -- Update the college_id column in management_team:
                UPDATE management_team
                SET college_id = (
                    SELECT management_college.id
                    FROM management_college
                    WHERE management_college.name = management_team.college_id
                )
                WHERE EXISTS (
                    SELECT 1
                    FROM management_college
                    WHERE management_college.name = management_team.college_id
                );
                PRAGMA foreign_keys = ON;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
