# Generated by Django 3.2.14 on 2022-11-23 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0009_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(
                choices=[
                    ('Received',
                     'Order Received'),
                    ('Processing',
                     'Order Processing'),
                    ('Dispatched',
                     'Order Dispatched'),
                    ('On Hold',
                     'On Hold'),
                    ('Extra to be paid',
                     'Extra to be Paid'),
                    ('Pending Partial Refund',
                     'Pending Partial Refund'),
                    ('Cancelled Pending Refund',
                     'Cancelled Pending Refund'),
                    ('Cancelled',
                     'Cancelled')],
                default='Received',
                max_length=50),
        ),
    ]
