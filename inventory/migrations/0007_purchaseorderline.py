from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_productclosestatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=120, verbose_name='전표번호/발주번호')),
                ('order_label', models.CharField(blank=True, max_length=50, verbose_name='발주 표시명')),
                ('product_code', models.CharField(blank=True, max_length=120, verbose_name='상품코드')),
                ('supplier_option_name', models.CharField(blank=True, max_length=120, verbose_name='공급처옵션명')),
                ('product_name', models.CharField(max_length=255, verbose_name='상품명')),
                ('option_name', models.CharField(blank=True, max_length=255, verbose_name='옵션명')),
                ('quantity', models.FloatField(default=0, verbose_name='발주수량')),
                ('memo', models.CharField(blank=True, max_length=255, verbose_name='입고예정 메모')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_order_lines', to='inventory.uploadedfile')),
            ],
            options={
                'ordering': ['order_number', 'product_name', 'option_name'],
            },
        ),
    ]
