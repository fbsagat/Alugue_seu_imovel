# Generated by Django 4.1.7 on 2023-03-17 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_remove_tarefa_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='anotacoe',
            name='tarefa',
            field=models.BooleanField(default=False),
        ),
    ]