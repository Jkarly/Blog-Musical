# Generated by Django 5.1 on 2024-08-29 02:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_artista_link_facebook_artista_link_instagram_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorito',
            unique_together={('usuario', 'cancion')},
        ),
        migrations.AlterField(
            model_name='favorito',
            name='cancion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.cancion'),
        ),
        migrations.RemoveField(
            model_name='favorito',
            name='fecha_agregado',
        ),
    ]
