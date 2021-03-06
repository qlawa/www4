# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-14 10:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gmina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazwa', models.CharField(max_length=64)),
                ('numer', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Kandydat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imie', models.CharField(max_length=64)),
                ('nazwisko', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Obwod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numer', models.IntegerField(unique=True)),
                ('nazwa', models.CharField(max_length=128)),
                ('gmina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apka.Gmina')),
            ],
        ),
        migrations.CreateModel(
            name='Okreg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numer', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wojewodztwo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numer', models.IntegerField(unique=True)),
                ('nazwa', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Wynik',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liczba_glosow', models.IntegerField()),
                ('kandydat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apka.Kandydat')),
                ('obwod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apka.Obwod')),
            ],
        ),
        migrations.AddField(
            model_name='okreg',
            name='wojewodztwo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apka.Wojewodztwo'),
        ),
        migrations.AlterUniqueTogether(
            name='kandydat',
            unique_together=set([('imie', 'nazwisko')]),
        ),
        migrations.AddField(
            model_name='gmina',
            name='okreg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apka.Okreg'),
        ),
    ]
