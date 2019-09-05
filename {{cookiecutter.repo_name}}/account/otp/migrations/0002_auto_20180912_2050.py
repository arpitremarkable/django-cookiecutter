# Generated by Django 2.1.1 on 2018-09-12 20:50

import account.otp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='otpmodel',
            name='phone_number',
            field=models.CharField(default='', max_length=11),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='otpmodel',
            name='generated_otp',
            field=models.CharField(default=account.otp.models.generate_otp, max_length=6),
        ),
    ]