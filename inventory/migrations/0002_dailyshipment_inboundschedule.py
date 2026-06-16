# Generated manually for historical delivery and inbound schedule tracking.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='reference_date',
            field=models.DateField(blank=True, null=True, verbose_name='작성/기준일'),
        ),
        migrations.AddField(
            model_name='productoptionmetric',
            name='inbound_date',
            field=models.DateField(blank=True, null=True, verbose_name='입고예정일'),
        ),
        migrations.CreateModel(
            name='DailyShipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateField(verbose_name='배송 기준일')),
                ('product_code', models.CharField(blank=True, max_length=120, verbose_name='상품코드/공급처옵션')),
                ('product_name', models.CharField(max_length=255, verbose_name='상품명')),
                ('option_name', models.CharField(blank=True, max_length=255, verbose_name='옵션명')),
                ('quantity', models.FloatField(default=0, verbose_name='배송수량')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록 일시')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to='inventory.uploadedfile')),
            ],
            options={'ordering': ['-delivery_date', 'product_name', 'option_name']},
        ),
        migrations.CreateModel(
            name='InboundSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inbound_date', models.DateField(blank=True, null=True, verbose_name='입고예정일')),
                ('product_code', models.CharField(blank=True, max_length=120, verbose_name='상품코드/공급처옵션')),
                ('product_name', models.CharField(max_length=255, verbose_name='상품명')),
                ('option_name', models.CharField(blank=True, max_length=255, verbose_name='옵션명')),
                ('quantity', models.FloatField(default=0, verbose_name='입고예정수량')),
                ('memo', models.CharField(blank=True, max_length=255, verbose_name='메모')),
                ('is_completed', models.BooleanField(default=False, verbose_name='입고완료 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록 일시')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_schedules', to='inventory.uploadedfile')),
            ],
            options={'ordering': ['inbound_date', 'product_name', 'option_name']},
        ),
    ]
