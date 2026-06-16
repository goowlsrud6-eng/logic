import io
from collections import defaultdict

import pandas as pd
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import MultiUploadInventoryForm
from .models import InboundSchedule, ProductOptionMetric, UploadedFile
from .services import (
    infer_week_label,
    metric_key,
    parse_combined_single_sheet_workbook,
    parse_inbound_schedule_workbook,
    parse_product_master_workbook,
    parse_special_stock_workbook,
    planned_inbound_by_key,
    safe_weeks,
    sha256_file,
)


def latest_stock_file():
    return UploadedFile.objects.filter(
        status=UploadedFile.Status.COMPLETED,
        file_type__in=[UploadedFile.FileType.STOCK_SALES, UploadedFile.FileType.LEGACY],
        metrics__isnull=False,
    ).distinct().order_by('-reference_date', '-created_at').first()


def live_option_rows(metrics):
    inbound_lookup = planned_inbound_by_key()
    rows = []
    for item in metrics:
        key = metric_key(item.product_code, item.supplier_option_name, item.product_name, item.option_name)
        inbound_qty = inbound_lookup.get(key, 0)
        stock_after = item.available_stock + inbound_qty
        inbound_recent = safe_weeks(stock_after, item.recent_week_sales)
        weekly_total_rate = (item.total_sales / item.sales_days * 7) if item.total_sales > 0 and item.sales_days > 0 else 0
        rows.append({
            'id': item.id,
            'product_code': item.product_code,
            'supplier_option_name': item.supplier_option_name,
            'product_name': item.product_name,
            'option_name': item.option_name,
            'available_stock': item.available_stock,
            'inbound_qty': inbound_qty,
            'inbound_date': item.inbound_date,
            'stock_after_inbound': stock_after,
            'delivery_qty': item.delivery_qty,
            'pending_qty': item.pending_qty,
            'recent_week_sales': item.recent_week_sales,
            'total_sales': item.total_sales,
            'sales_days': item.sales_days,
            'current_recent_weeks': safe_weeks(item.available_stock, item.recent_week_sales),
            'inbound_recent_weeks': inbound_recent,
            'current_total_weeks': safe_weeks(item.available_stock, weekly_total_rate),
            'inbound_total_weeks': safe_weeks(stock_after, weekly_total_rate),
            'previous_inbound_recent_weeks': item.previous_inbound_recent_weeks,
            'status': item.status,
            'sales_trend': item.sales_trend,
        })
    return rows


def summarize_products(option_rows):
    grouped = {}
    for item in option_rows:
        row = grouped.setdefault(item['product_name'], {
            'product_name': item['product_name'],
            'option_count': 0,
            'available_stock': 0,
            'inbound_qty': 0,
            'stock_after_inbound': 0,
            'delivery_qty': 0,
            'pending_qty': 0,
            'recent_week_sales': 0,
            'total_sales': 0,
            'sales_days': 0,
            'previous_inbound_recent_weeks': 0,
            'sales_trend': '',
        })
        row['option_count'] += 1
        for field in ['available_stock', 'inbound_qty', 'stock_after_inbound', 'delivery_qty', 'pending_qty', 'recent_week_sales', 'total_sales']:
            row[field] += item[field] or 0
        row['sales_days'] = max(row['sales_days'], item['sales_days'] or 0)
        row['previous_inbound_recent_weeks'] += item['previous_inbound_recent_weeks'] or 0
        if item['sales_trend'] in ['판매 급상승', '판매 급하락']:
            row['sales_trend'] = item['sales_trend']
        elif not row['sales_trend'] and item['sales_trend']:
            row['sales_trend'] = item['sales_trend']

    summary = list(grouped.values())
    for row in summary:
        weekly_total_rate = (row['total_sales'] / row['sales_days'] * 7) if row['total_sales'] > 0 and row['sales_days'] > 0 else 0
        row['current_recent_weeks'] = safe_weeks(row['available_stock'], row['recent_week_sales'])
        row['inbound_recent_weeks'] = safe_weeks(row['stock_after_inbound'], row['recent_week_sales'])
        row['current_total_weeks'] = safe_weeks(row['available_stock'], weekly_total_rate)
        row['inbound_total_weeks'] = safe_weeks(row['stock_after_inbound'], weekly_total_rate)
    return sorted(summary, key=lambda r: r['product_name'])


def dashboard(request):
    latest_file = latest_stock_file()
    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file).order_by('product_name', 'option_name') if latest_file else ProductOptionMetric.objects.none()
    option_rows = live_option_rows(metrics)
    summary = summarize_products(option_rows)
    distribution = {
        '0~4주': sum(1 for row in summary if 0 < row['inbound_recent_weeks'] <= 4),
        '4~8주': sum(1 for row in summary if 4 < row['inbound_recent_weeks'] <= 8),
        '8~12주': sum(1 for row in summary if 8 < row['inbound_recent_weeks'] <= 12),
        '12주 이상': sum(1 for row in summary if row['inbound_recent_weeks'] > 12),
    }
    planned_inbound_products = set(InboundSchedule.objects.filter(status=InboundSchedule.Status.PLANNED).values_list('product_name', flat=True))
    context = {
        'latest_file': latest_file,
        'summary': summary,
        'total_products': len(summary),
        'total_options': len(option_rows),
        'under_4_count': sum(1 for row in summary if 0 < row['inbound_recent_weeks'] <= 4),
        'under_8_count': sum(1 for row in summary if 0 < row['inbound_recent_weeks'] <= 8),
        'surge_count': sum(1 for row in summary if row['sales_trend'] == '판매 급상승'),
        'drop_count': sum(1 for row in summary if row['sales_trend'] == '판매 급하락'),
        'no_inbound_count': sum(1 for row in summary if row['product_name'] not in planned_inbound_products),
        'risk_count': sum(1 for row in summary if 0 < row['inbound_recent_weeks'] <= 4),
        'distribution': distribution,
        'top_surges': [row for row in summary if row['sales_trend'] in ['판매 급상승', '판매 상승']][:10],
        'top_drops': [row for row in summary if row['sales_trend'] in ['판매 급하락', '판매 하락']][:10],
        'upload_form': MultiUploadInventoryForm(),
        'uploads': UploadedFile.objects.order_by('-created_at')[:10],
    }
    return render(request, 'inventory/dashboard.html', context)


def create_upload_record(uploaded, file_type, reference_date=None):
    return UploadedFile.objects.create(
        original_name=uploaded.name,
        file=uploaded,
        file_hash=sha256_file(uploaded),
        file_type=file_type,
        reference_date=reference_date,
        week_label=infer_week_label('', uploaded.name, reference_date),
    )


def upload_inventory(request):
    if request.method != 'POST':
        return redirect('dashboard')
    form = MultiUploadInventoryForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, '업로드할 파일을 하나 이상 선택해주세요.')
        return redirect('dashboard')

    reference_date = form.cleaned_data['reference_date'] or timezone.localdate()
    tasks = [
        ('product_master_file', UploadedFile.FileType.PRODUCT_MASTER, parse_product_master_workbook, '상품기본정보/오픈일'),
        ('inbound_schedule_file', UploadedFile.FileType.INBOUND_SCHEDULE, parse_inbound_schedule_workbook, '입고예정'),
        ('stock_sales_file', UploadedFile.FileType.STOCK_SALES, parse_combined_single_sheet_workbook, '재고/판매 통합'),
    ]
    success = []
    for field_name, file_type, parser, label in tasks:
        uploaded = form.cleaned_data.get(field_name)
        if not uploaded:
            continue
        record = create_upload_record(uploaded, file_type, reference_date)
        try:
            count = parser(record)
            success.append(f'{label} {count}건')
        except Exception as exc:
            record.status = UploadedFile.Status.FAILED
            record.message = str(exc)
            record.save(update_fields=['status', 'message'])
            messages.error(request, f'{label} 처리 실패: {exc}')
    if success:
        messages.success(request, ' / '.join(success) + ' 처리 완료')
    return redirect('dashboard')


def product_detail(request, product_name):
    latest_file = latest_stock_file()
    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file, product_name=product_name).order_by('option_name') if latest_file else ProductOptionMetric.objects.none()
    option_rows = live_option_rows(metrics)
    return render(request, 'inventory/product_detail.html', {
        'product_name': product_name,
        'metrics': option_rows,
    })


def inbound_schedule(request):
    today = timezone.localdate()
    inbound_schedules = InboundSchedule.objects.order_by('inbound_date', 'product_name', 'option_name')
    return render(request, 'inventory/inbound_schedule.html', {
        'inbound_schedules': inbound_schedules,
        'today': today,
    })


def excel_response(df, filename, sheet_name):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def download_current_stock_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '가용재고', '접수', '송장', '배송', '송장+배송']
    sample = pd.DataFrame([['P001', 'SUP-001', '촤르르반팔', '블랙/M', 30, 2, 1, 5, 6]], columns=columns)
    return excel_response(sample, 'current_stock_template.xlsx', '현재고')


def download_recent_sales_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '수량']
    sample = pd.DataFrame([['P001', 'SUP-001', '촤르르반팔', '블랙/M', 10]], columns=columns)
    return excel_response(sample, 'recent_week_sales_template.xlsx', '최근한주판매수량')


def download_total_sales_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '수량']
    sample = pd.DataFrame([['P001', 'SUP-001', '촤르르반팔', '블랙/M', 100]], columns=columns)
    return excel_response(sample, 'total_sales_template.xlsx', '총판매수량')


def download_product_master_template(request):
    columns = ['상품코드', '공급처옵션명', '상품명', '옵션', '오픈일']
    sample = pd.DataFrame([['P001', 'SUP-001', '촤르르반팔', '블랙/M', '2026-06-01']], columns=columns)
    return excel_response(sample, 'product_master_open_date_template.xlsx', '상품기본정보')


def download_inbound_schedule_template(request):
    columns = ['공급처옵션명', '상품명', '옵션', '수량', '일정', '상태', '비고']
    sample = pd.DataFrame([
        ['SUP-001', '촤르르반팔', '블랙/M', 40, '2026-06-19', '예정', '1차 입고'],
        ['SUP-003', '모자', '베이지/F', 100, '', '예정', '발주완료, 일정 미정'],
    ], columns=columns)
    return excel_response(sample, 'inbound_schedule_template.xlsx', '입고예정수량')


def download_basic_template(request):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('재고_판매_통합')
        writer.sheets['재고_판매_통합'] = worksheet
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9EAF7', 'border': 1})
        section_format = workbook.add_format({'bold': True, 'bg_color': '#FCE4D6'})
        sections = [
            (0, '1. 현재고양식', ['상품코드', '공급처옵션명', '상품명', '옵션', '가용재고', '접수', '송장', '배송', '송장+배송'], [['P001', 'SUP-001', '촤르르반팔', '블랙/M', 30, 2, 1, 5, 6]]),
            (10, '2. 최근한주판매수량 양식', ['상품코드', '공급처옵션명', '상품명', '옵션', '수량'], [['P001', 'SUP-001', '촤르르반팔', '블랙/M', 10]]),
            (16, '3. 총판매수량 양식', ['상품코드', '공급처옵션명', '상품명', '옵션', '수량'], [['P001', 'SUP-001', '촤르르반팔', '블랙/M', 100]]),
        ]
        for start_col, title, headers, rows in sections:
            worksheet.write(0, start_col, title, section_format)
            for col_offset, header in enumerate(headers):
                worksheet.write(1, start_col + col_offset, header, header_format)
            for row_offset, row in enumerate(rows, start=2):
                for col_offset, value in enumerate(row):
                    worksheet.write(row_offset, start_col + col_offset, value)
            worksheet.set_column(start_col, start_col + len(headers) - 1, 14)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="stock_sales_combined_template.xlsx"'
    return response
