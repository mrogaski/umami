# Generated by Django 2.0.3 on 2018-03-12 05:30

import uuid

import concurrency.fields
from django.db import migrations, models

import redirect.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', concurrency.fields.AutoIncVersionField(default=0, help_text='record revision number')),
                ('path', models.CharField(max_length=32, unique=True, validators=[redirect.models.URLPathValidator()])),
                ('location', models.URLField(max_length=2048)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        )
    ]
