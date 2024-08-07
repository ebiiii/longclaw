# Generated by Django 2.2.17 on 2021-04-02 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Submitted'), (2, 'Fulfilled'), (3, 'Cancelled'), (4, 'Refunded'), (5, 'Payment Failed'), (6, 'Payment Succeeded')], default=1),
        ),
    ]