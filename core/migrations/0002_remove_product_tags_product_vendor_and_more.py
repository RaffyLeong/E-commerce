# Generated by Django 5.0.7 on 2024-09-09 07:47

import core.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.vendor'),
        ),
        migrations.AlterField(
            model_name='cartorder',
            name='product_status',
            field=models.CharField(choices=[('Process', 'Processing'), ('delivered', 'Delivered'), ('Shipped', 'PShipped')], default='processing', max_length=30),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='product.jpg', upload_to=core.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('in_review', 'In_review'), ('disabled', 'Disabled'), ('draft', 'Draft'), ('published', 'Published'), ('rejected', 'Rejected')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(4, '★★★★✩'), (3, '★★★✩✩'), (2, '★★✩✩✩'), (5, '★★★★★'), (1, '★✩✩✩✩')], default=None),
        ),
    ]
