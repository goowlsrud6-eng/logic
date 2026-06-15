# Generated manually for the initial Django scaffold.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_name', models.CharField(max_length=255, verbose_name='원본 파일명')),
                ('file', models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='보관 파일')),
                ('file_hash', models.CharField(blank=True, max_length=64, verbose_name='파일 해시')),
                ('week_label', models.CharField(blank=True, help_text='예: 0615-0619', max_length=20, verbose_name='기준 주차')),
                ('status', models.CharField(choices=[('pending', '처리 대기'), ('completed', '처리 완료'), ('failed', '처리 실패')], default='pending', max_length=20, verbose_name='처리 상태')),
                ('message', models.TextField(blank=True, verbose_name='처리 메시지')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='업로드 일시')),
            ],
        ),
        migrations.CreateModel(
            name='ProductOptionMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_sheet', models.CharField(blank=True, max_length=120, verbose_name='원본 시트명')),
                ('week_label', models.CharField(blank=True, max_length=20, verbose_name='기준 주차')),
                ('product_code', models.CharField(blank=True, max_length=120, verbose_name='상품코드/공급처옵션')),
                ('product_name', models.CharField(max_length=255, verbose_name='상품명')),
                ('option_name', models.CharField(blank=True, max_length=255, verbose_name='옵션명')),
                ('available_stock', models.FloatField(default=0, verbose_name='가용재고')),
                ('inbound_qty', models.FloatField(default=0, verbose_name='입고예정수량')),
                ('stock_after_inbound', models.FloatField(default=0, verbose_name='입고후재고')),
                ('delivery_qty', models.FloatField(default=0, verbose_name='배송수량')),
                ('pending_qty', models.FloatField(default=0, verbose_name='미출고/접수수량')),
                ('recent_week_sales', models.FloatField(default=0, verbose_name='최근한주 판매수량')),
                ('total_sales', models.FloatField(default=0, verbose_name='총판매수량')),
                ('sales_days', models.FloatField(default=0, verbose_name='판매일수')),
                ('current_recent_weeks', models.FloatField(default=0, verbose_name='현재고 기준 최근한주 판매가능주')),
                ('inbound_recent_weeks', models.FloatField(default=0, verbose_name='입고포함 최근한주 판매가능주')),
                ('current_total_weeks', models.FloatField(default=0, verbose_name='현재고 기준 총판매 판매가능주')),
                ('inbound_total_weeks', models.FloatField(default=0, verbose_name='입고포함 총판매 판매가능주')),
                ('status', models.CharField(blank=True, max_length=30, verbose_name='재고 상태')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='inventory.uploadedfile')),
            ],
            options={'ordering': ['product_name', 'option_name']},
        ),
    ]
