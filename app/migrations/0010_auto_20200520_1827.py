# Generated by Django 3.0.3 on 2020-05-20 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200520_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('OW', 'Outwear'), ('Sw', 'Sport wear'), ('S', 'Shirt')], max_length=200),
        ),
    ]
