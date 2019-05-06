# Generated by Django 2.2 on 2019-05-06 00:33

import concurrency.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', concurrency.fields.AutoIncVersionField(default=0, help_text='record revision number', verbose_name='entity version')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('users', models.ManyToManyField(related_name='accounts', related_query_name='account', to=settings.AUTH_USER_MODEL, verbose_name='users')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.SlugField(max_length=64, unique=True, verbose_name='name')),
                ('provider', models.CharField(choices=[('discord', 'Discord')], max_length=64, verbose_name='providers')),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
                ('client_id', models.CharField(max_length=191, verbose_name='client id')),
                ('client_secret', models.CharField(max_length=191, verbose_name='client secret')),
                ('scope_override', models.TextField(blank=True, default='', verbose_name='scope override')),
            ],
        ),
        migrations.CreateModel(
            name='DiscordAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='guildmaster.Account')),
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=32, verbose_name='username')),
                ('discriminator', models.CharField(max_length=4, verbose_name='discriminator')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('mfa_enabled', models.BooleanField(default=False, verbose_name='MFA enabled')),
                ('avatar', models.CharField(blank=True, default='', max_length=64, verbose_name='avatar')),
            ],
            options={
                'ordering': ('username', 'discriminator'),
            },
            bases=('guildmaster.account',),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('token_type', models.CharField(default='bearer', max_length=64, verbose_name='token type')),
                ('access_token', models.TextField(verbose_name='access token')),
                ('refresh_token', models.TextField(blank=True, default='', verbose_name='refresh token')),
                ('expires_in', models.PositiveIntegerField(blank=True, null=True, verbose_name='expires in')),
                ('scope', models.TextField(blank=True, default='', verbose_name='scope')),
                ('redirect_uri', models.URLField(blank=True, default='', verbose_name='redirect URI')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guildmaster.Client', verbose_name='client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='users')),
            ],
        ),
    ]
