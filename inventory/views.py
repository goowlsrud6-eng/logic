import io

import pandas as pd
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import UploadInventoryFileForm
from .models import ProductOptionMetric, UploadedFile
from .services import parse_basic_inventory_workbook, parse_special_stock_workbook, safe_weeks, sha256_file


def dashboard(request):
    latest_file = UploadedFile.objects.filter(status=UploadedFile.Status.COMPLETED).order_by('-created_at').first()
    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file) if latest_file else ProductOptionMetric.objects.none()
    summary = list(metrics.values('product_name').annotate(
        option_count=Count('id'),
        available_stock=Sum('available_stock'),
        inbound_qty=Sum('inbound_qty'),
        stock_after_inbound=Sum('stock_after_inbound'),
        recent_week_sales=Sum('recent_week_sales'),
        total_sales=Sum('total_sales'),
        sales_days=Sum('sales_days'),
    ).order_by('product_name'))
    for row in summary:
        row['current_recent_weeks'] = safe_weeks(row['available_stock'] or 0, row['recent_week_sales'] or 0)
        row['inbound_recent_weeks'] = safe_weeks(row['stock_after_inbound'] or 0, row['recent_week_sales'] or 0)
        weekly_total_rate = ((row['total_sales'] or 0) / (row['sales_days'] or 0) * 7) if row.get('sales_days') else 0
        row['current_total_weeks'] = safe_weeks(row['available_stock'] or 0, weekly_total_rate)
        row['inbound_total_weeks'] = safe_weeks(row['stock_after_inbound'] or 0, weekly_total_rate)
    context = {
        'latest_file': latest_file,
        'summary': summary,
        'total_products': len(summary),
        'total_options': metrics.count(),
        'urgent_count': metrics.filter(status='긴급').count(),
        'upload_form': UploadInventoryFileForm(),
        'uploads': UploadedFile.objects.order_by('-created_at')[:10],
    }
    return render(request, 'inventory/dashboard.html', context)


def upload_inventory(request):
    if request.method != 'POST':
        return redirect('dashboard')
    form = UploadInventoryFileForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, '업로드 정보를 확인해주세요.')
        return redirect('dashboard')

    uploaded = request.FILES['file']
    record = UploadedFile.objects.create(
        original_name=uploaded.name,
        file=uploaded,
        file_hash=sha256_file(uploaded),
        week_label=form.cleaned_data['week_label'],
    )
    try:
        if form.cleaned_data['upload_mode'] == 'legacy':
            count = parse_special_stock_workbook(record)
        else:
            count = parse_basic_inventory_workbook(record)
        messages.success(request, f'업로드 완료: {count}개 옵션 데이터를 처리했습니다.')
    except Exception as exc:
        record.status = UploadedFile.Status.FAILED
        record.message = str(exc)
        record.save(update_fields=['status', 'message'])
        messages.error(request, f'처리 실패: {exc}')
    return redirect('dashboard')


def download_basic_template(request):
    columns = [
        '상품코드', '상품명', '옵션명', '현재고', '최근한주수량', '총판매수량',
        '오픈일', '판매일수', '입고예정수량', '배송수량', '접수수량'
    ]
    sample = pd.DataFrame([
        ['P001', '촤르르반팔', '블랙/M', 30, 10, 100, '2026-06-01', 30, 50, 0, 0],
        ['P002', '냉감이불', '화이트/Q', 80, 20, 300, '2026-05-01', 45, 0, 0, 0],
    ], columns=columns)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        sample.to_excel(writer, index=False, sheet_name='기초데이터')
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="basic_inventory_template.xlsx"'
    return response
