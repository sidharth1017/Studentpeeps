# Generated by Django 3.2.7 on 2021-09-16 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_signup_yourdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registers',
            name='profile_image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='pics'),
        ),
    ]