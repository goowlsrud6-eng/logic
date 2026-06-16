# Generated manually for product open-date master data.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0002_dailyshipment_inboundschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(blank=True, max_length=120, verbose_name='상품코드')),
                ('supplier_option_name', models.CharField(blank=True, max_length=120, verbose_name='공급처옵션명')),
                ('product_name', models.CharField(max_length=255, verbose_name='상품명')),
                ('option_name', models.CharField(blank=True, max_length=255, verbose_name='옵션명')),
                ('open_date', models.DateField(blank=True, null=True, verbose_name='오픈일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={'ordering': ['product_name', 'option_name']},
        ),
    ]
