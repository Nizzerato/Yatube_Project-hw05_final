# Generated by Django 2.2.16 on 2021-11-12 18:48

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=sorl.thumbnail.fields.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
