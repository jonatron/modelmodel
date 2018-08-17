# Generated by Django 2.1 on 2018-08-16 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MakeField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('field_type', models.CharField(choices=[('TextField', 'TextField'), ('IntegerField', 'IntegerField')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MakeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Model Name')),
            ],
        ),
        migrations.AddField(
            model_name='makefield',
            name='make_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.MakeModel'),
        ),
    ]