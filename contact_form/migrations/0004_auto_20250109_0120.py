# Generated by Django 3.2.14 on 2025-01-08 20:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact_form', '0003_alter_customermessages_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customermessages',
            old_name='message',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='customermessages',
            old_name='subject',
            new_name='phone_number',
        ),
    ]
