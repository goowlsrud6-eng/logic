from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0003_productmaster'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='file_type',
            field=models.CharField(choices=[('stock_sales', '재고/판매 통합'), ('product_master', '상품기본정보/오픈일'), ('inbound_schedule', '입고예정'), ('legacy', '기존 특별재고')], default='stock_sales', max_length=30, verbose_name='파일 종류'),
        ),
        migrations.AddField(
            model_name='productoptionmetric',
            name='supplier_option_name',
            field=models.CharField(blank=True, max_length=120, verbose_name='공급처옵션명'),
        ),
        migrations.AddField(
            model_name='productoptionmetric',
            name='previous_inbound_recent_weeks',
            field=models.FloatField(default=0, verbose_name='지난주 기준 판매가능주'),
        ),
        migrations.AddField(
            model_name='productoptionmetric',
            name='sales_trend',
            field=models.CharField(blank=True, max_length=30, verbose_name='판매 상승/하락 상태'),
        ),
        migrations.AddField(
            model_name='dailyshipment',
            name='supplier_option_name',
            field=models.CharField(blank=True, max_length=120, verbose_name='공급처옵션명'),
        ),
        migrations.AddField(
            model_name='inboundschedule',
            name='supplier_option_name',
            field=models.CharField(blank=True, max_length=120, verbose_name='공급처옵션명'),
        ),
        migrations.AddField(
            model_name='inboundschedule',
            name='status',
            field=models.CharField(choices=[('planned', '예정'), ('completed', '완료'), ('canceled', '취소')], default='planned', max_length=20, verbose_name='상태'),
        ),
        migrations.AddField(
            model_name='inboundschedule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='수정 일시'),
        ),
        migrations.AlterField(
            model_name='productoptionmetric',
            name='product_code',
            field=models.CharField(blank=True, max_length=120, verbose_name='상품코드'),
        ),
        migrations.AlterField(
            model_name='dailyshipment',
            name='product_code',
            field=models.CharField(blank=True, max_length=120, verbose_name='상품코드'),
        ),
        migrations.AlterField(
            model_name='inboundschedule',
            name='product_code',
            field=models.CharField(blank=True, max_length=120, verbose_name='상품코드'),
        ),
    ]
