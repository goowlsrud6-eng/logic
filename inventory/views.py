import io

import pandas as pd
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import UploadInventoryFileForm
from .models import DailyShipment, InboundSchedule, ProductOptionMetric, UploadedFile
from .services import parse_basic_inventory_workbook, parse_product_master_workbook, parse_special_stock_workbook, safe_weeks, sha256_file


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
        'shipments': DailyShipment.objects.order_by('-delivery_date', 'product_name')[:20],
        'inbound_schedules': InboundSchedule.objects.filter(is_completed=False).order_by('inbound_date', 'product_name')[:20],
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
        reference_date=form.cleaned_data['reference_date'],
    )
    try:
        if form.cleaned_data['upload_mode'] == 'legacy':
            count = parse_special_stock_workbook(record)
        elif form.cleaned_data['upload_mode'] == 'product_master':
            count = parse_product_master_workbook(record)
        else:
            count = parse_basic_inventory_workbook(record)
        messages.success(request, f'업로드 완료: {count}개 옵션 데이터를 처리했습니다.')
    except Exception as exc:
        record.status = UploadedFile.Status.FAILED
        record.message = str(exc)
        record.save(update_fields=['status', 'message'])
        messages.error(request, f'처리 실패: {exc}')
    return redirect('dashboard')



def excel_response(df, filename, sheet_name):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def download_current_stock_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '가용재고', '접수', '송장', '배송', '송장+배송']
    sample = pd.DataFrame([
        ['P001', 'SUP-001', '촤르르반팔', '블랙/M', 30, 2, 1, 5, 6],
        ['P002', 'SUP-002', '냉감이불', '화이트/Q', 80, 0, 0, 3, 3],
    ], columns=columns)
    return excel_response(sample, 'current_stock_template.xlsx', '현재고')


def download_recent_sales_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '수량']
    sample = pd.DataFrame([
        ['P001', 'SUP-001', '촤르르반팔', '블랙/M', 10],
        ['P002', 'SUP-002', '냉감이불', '화이트/Q', 20],
    ], columns=columns)
    return excel_response(sample, 'recent_week_sales_template.xlsx', '최근한주판매수량')


def download_total_sales_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '수량']
    sample = pd.DataFrame([
        ['P001', 'SUP-001', '촤르르반팔', '블랙/M', 100],
        ['P002', 'SUP-002', '냉감이불', '화이트/Q', 300],
    ], columns=columns)
    return excel_response(sample, 'total_sales_template.xlsx', '총판매수량')


def download_product_master_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '오픈일']
    sample = pd.DataFrame([
        ['P001', 'SUP-001', '촤르르반팔', '블랙/M', '2026-06-01'],
        ['P002', 'SUP-002', '냉감이불', '화이트/Q', '2026-05-01'],
    ], columns=columns)
    return excel_response(sample, 'product_master_open_date_template.xlsx', '상품기본정보')


def download_basic_template(request):
    columns = [
        '상품코드', '상품명', '옵션명', '현재고', '최근한주수량', '총판매수량',
        '오픈일', '판매일수', '입고예정일', '입고예정수량', '배송수량', '접수수량'
    ]
    sample = pd.DataFrame([
        ['P001', '촤르르반팔', '블랙/M', 30, 10, 100, '2026-06-01', 30, '2026-06-19', 50, 0, 0],
        ['P002', '냉감이불', '화이트/Q', 80, 20, 300, '2026-05-01', 45, '', 0, 0, 0],
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
