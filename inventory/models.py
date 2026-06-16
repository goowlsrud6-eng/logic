from django.db import models


class UploadedFile(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '처리 대기'
        COMPLETED = 'completed', '처리 완료'
        FAILED = 'failed', '처리 실패'

    original_name = models.CharField('원본 파일명', max_length=255)
    file = models.FileField('보관 파일', upload_to='uploads/%Y/%m/%d/')
    file_hash = models.CharField('파일 해시', max_length=64, blank=True)
    week_label = models.CharField('기준 주차', max_length=20, blank=True, help_text='예: 0615-0619')
    reference_date = models.DateField('작성/기준일', null=True, blank=True)
    status = models.CharField('처리 상태', max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField('처리 메시지', blank=True)
    created_at = models.DateTimeField('업로드 일시', auto_now_add=True)

    def __str__(self):
        return f'{self.original_name} ({self.week_label or "주차 미지정"})'


class ProductOptionMetric(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='metrics')
    source_sheet = models.CharField('원본 시트명', max_length=120, blank=True)
    week_label = models.CharField('기준 주차', max_length=20, blank=True)
    product_code = models.CharField('상품코드/공급처옵션', max_length=120, blank=True)
    product_name = models.CharField('상품명', max_length=255)
    option_name = models.CharField('옵션명', max_length=255, blank=True)
    available_stock = models.FloatField('가용재고', default=0)
    inbound_qty = models.FloatField('입고예정수량', default=0)
    inbound_date = models.DateField('입고예정일', null=True, blank=True)
    stock_after_inbound = models.FloatField('입고후재고', default=0)
    delivery_qty = models.FloatField('배송수량', default=0)
    pending_qty = models.FloatField('미출고/접수수량', default=0)
    recent_week_sales = models.FloatField('최근한주 판매수량', default=0)
    total_sales = models.FloatField('총판매수량', default=0)
    sales_days = models.FloatField('판매일수', default=0)
    current_recent_weeks = models.FloatField('현재고 기준 최근한주 판매가능주', default=0)
    inbound_recent_weeks = models.FloatField('입고포함 최근한주 판매가능주', default=0)
    current_total_weeks = models.FloatField('현재고 기준 총판매 판매가능주', default=0)
    inbound_total_weeks = models.FloatField('입고포함 총판매 판매가능주', default=0)
    status = models.CharField('재고 상태', max_length=30, blank=True)

    class Meta:
        ordering = ['product_name', 'option_name']

    def __str__(self):
        return f'{self.product_name} / {self.option_name}'


class DailyShipment(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='shipments')
    delivery_date = models.DateField('배송 기준일')
    product_code = models.CharField('상품코드/공급처옵션', max_length=120, blank=True)
    product_name = models.CharField('상품명', max_length=255)
    option_name = models.CharField('옵션명', max_length=255, blank=True)
    quantity = models.FloatField('배송수량', default=0)
    created_at = models.DateTimeField('등록 일시', auto_now_add=True)

    class Meta:
        ordering = ['-delivery_date', 'product_name', 'option_name']

    def __str__(self):
        return f'{self.delivery_date} {self.product_name} {self.quantity}'


class InboundSchedule(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='inbound_schedules')
    inbound_date = models.DateField('입고예정일', null=True, blank=True)
    product_code = models.CharField('상품코드/공급처옵션', max_length=120, blank=True)
    product_name = models.CharField('상품명', max_length=255)
    option_name = models.CharField('옵션명', max_length=255, blank=True)
    quantity = models.FloatField('입고예정수량', default=0)
    memo = models.CharField('메모', max_length=255, blank=True)
    is_completed = models.BooleanField('입고완료 여부', default=False)
    created_at = models.DateTimeField('등록 일시', auto_now_add=True)

    class Meta:
        ordering = ['inbound_date', 'product_name', 'option_name']

    def __str__(self):
        return f'{self.inbound_date or "날짜 미정"} {self.product_name} {self.quantity}'
