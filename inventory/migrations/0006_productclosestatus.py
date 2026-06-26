# Generated manually for product close status tracking.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_inboundschedule_order_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCloseStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255, unique=True, verbose_name='상품명')),
                ('is_closed', models.BooleanField(default=False, verbose_name='마감 여부')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'ordering': ['product_name'],
            },
        ),
    ]
