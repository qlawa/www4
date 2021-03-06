# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-25 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apka', '0004_auto_20170419_1039'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StatystykaObw',
            new_name='Statystyka',
        ),
        migrations.RenameModel(
            old_name='WynikObw',
            new_name='Wynik',
        ),
        migrations.AlterUniqueTogether(
            name='statystykaokr',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='statystykaokr',
            name='okreg',
        ),
        migrations.AlterUniqueTogether(
            name='wynikokr',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='wynikokr',
            name='kandydat',
        ),
        migrations.RemoveField(
            model_name='wynikokr',
            name='okreg',
        ),
        migrations.RemoveField(
            model_name='wynik',
            name='liczba_glosow',
        ),
        migrations.AddField(
            model_name='wynik',
            name='liczba',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='StatystykaOkr',
        ),
        migrations.DeleteModel(
            name='WynikOkr',
        ),
    ]
