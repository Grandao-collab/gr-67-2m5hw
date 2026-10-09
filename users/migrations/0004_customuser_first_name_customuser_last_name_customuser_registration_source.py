from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_customuser_phone_number_customuser_birthdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='customuser',
            name='registration_source',
            field=models.CharField(choices=[('local', 'local'), ('google', 'google'), ('facebook', 'facebook')], default='local', max_length=20),
        ),
    ]
