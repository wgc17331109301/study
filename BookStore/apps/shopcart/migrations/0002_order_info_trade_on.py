# Generated by Django 3.2.10 on 2022-04-02 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopcart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_info',
            name='trade_on',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='交易号'),
        ),
    ]
