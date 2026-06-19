import io
from collections import defaultdict

import pandas as pd
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import InboundScheduleForm, MultiUploadInventoryForm
from .models import InboundSchedule, ProductOptionMetric, UploadedFile
from .services import (
    infer_week_label,
    first_lookup,
    judge_sales_trend,
    normalize_sales_trend,
    metric_key,
    parse_combined_single_sheet_workbook,
    parse_inbound_schedule_workbook,
    parse_product_master_workbook,
    parse_date,
    parse_special_stock_workbook,
    planned_inbound_by_key,
    previous_recent_sales_by_key,
    recent_sales_period_days,
    recent_weekly_rate,
    safe_weeks,
    sales_trend_css_class,
    sha256_file,
)


def latest_stock_file(upload_id=None):
    base_qs = UploadedFile.objects.filter(
        status=UploadedFile.Status.COMPLETED,
        file_type__in=[UploadedFile.FileType.STOCK_SALES, UploadedFile.FileType.LEGACY],
        metrics__isnull=False,
    ).distinct()
    if upload_id:
        selected = base_qs.filter(pk=upload_id).first()
        if selected:
            return selected
    return base_qs.order_by('-reference_date', '-created_at').first()




def remember_product(request, product_name, upload_id=None):
    request.session['last_product_name'] = product_name
    if upload_id:
        request.session['last_upload_id'] = str(upload_id)
    recent = request.session.get('recent_products', [])
    recent = [item for item in recent if item != product_name]
    recent.insert(0, product_name)
    request.session['recent_products'] = recent[:8]
    request.session.modified = True


def product_navigation(product_names, product_name):
    if product_name not in product_names:
        return None, None
    index = product_names.index(product_name)
    previous_name = product_names[index - 1] if index > 0 else None
    next_name = product_names[index + 1] if index < len(product_names) - 1 else None
    return previous_name, next_name

def live_option_rows(metrics, current_file=None):
    inbound_lookup = planned_inbound_by_key()
    previous_sales_lookup = previous_recent_sales_by_key(current_file) if current_file else {}
    rows = []
    for item in metrics:
        inbound_qty = first_lookup(inbound_lookup, item.product_code, item.supplier_option_name, item.product_name, item.option_name, default=0)
        stock_after = item.available_stock + inbound_qty
        recent_period_days = recent_sales_period_days(item.sales_days)
        recent_daily_sales = item.recent_week_sales / recent_period_days if item.recent_week_sales and recent_period_days > 0 else 0
        recent_rate = recent_weekly_rate(item.recent_week_sales, item.sales_days)
        inbound_recent = safe_weeks(stock_after, recent_rate)
        weekly_total_rate = (item.total_sales / item.sales_days * 7) if item.total_sales > 0 and item.sales_days > 0 else 0
        previous_sales = first_lookup(previous_sales_lookup, item.product_code, item.supplier_option_name, item.product_name, item.option_name, default=0)
        previous_weeks = safe_weeks(stock_after, previous_sales)
        sales_trend = normalize_sales_trend(judge_sales_trend(inbound_recent, previous_weeks) or item.sales_trend)
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
            'recent_sales_days': recent_period_days,
            'recent_daily_sales': recent_daily_sales,
            'current_recent_weeks': safe_weeks(item.available_stock, recent_rate),
            'inbound_recent_weeks': inbound_recent,
            'current_total_weeks': safe_weeks(item.available_stock, weekly_total_rate),
            'inbound_total_weeks': safe_weeks(stock_after, weekly_total_rate),
            'previous_week_sales': previous_sales,
            'previous_inbound_recent_weeks': previous_weeks or item.previous_inbound_recent_weeks,
            'status': item.status,
            'sales_trend': sales_trend,
            'sales_trend_class': sales_trend_css_class(sales_trend),
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
            'previous_week_sales': 0,
            'recent_daily_sales': 0,
            'previous_inbound_recent_weeks': 0,
            'sales_trend': '',
            'product_codes': set(),
            'supplier_options': set(),
        })
        row['option_count'] += 1
        if item.get('product_code'):
            row['product_codes'].add(str(item['product_code']))
        if item.get('supplier_option_name'):
            row['supplier_options'].add(str(item['supplier_option_name']))
        for field in ['available_stock', 'inbound_qty', 'stock_after_inbound', 'delivery_qty', 'pending_qty', 'recent_week_sales', 'total_sales', 'previous_week_sales', 'recent_daily_sales']:
            row[field] += item[field] or 0
        row['sales_days'] = max(row['sales_days'], item['sales_days'] or 0)
        row['previous_inbound_recent_weeks'] += item['previous_inbound_recent_weeks'] or 0
        item_trend = normalize_sales_trend(item['sales_trend'])
        if item_trend in ['판매 급등', '판매 급감']:
            row['sales_trend'] = item_trend
        elif not row['sales_trend'] and item_trend:
            row['sales_trend'] = item_trend

    summary = list(grouped.values())
    for row in summary:
        row['total_daily_sales'] = row['total_sales'] / 7 if row['total_sales'] else 0
        row['current_recent_weeks'] = safe_weeks(row['available_stock'], row['recent_daily_sales'] * 7)
        row['inbound_recent_weeks'] = safe_weeks(row['stock_after_inbound'], row['recent_daily_sales'] * 7)
        row['current_total_weeks'] = safe_weeks(row['available_stock'], row['total_daily_sales'] * 7)
        row['inbound_total_weeks'] = safe_weeks(row['stock_after_inbound'], row['total_daily_sales'] * 7)
        row['product_codes_text'] = ', '.join(sorted(row['product_codes']))
        row['supplier_options_text'] = ', '.join(sorted(row['supplier_options']))
        row['sales_trend_class'] = sales_trend_css_class(row['sales_trend'])
        row['search_text'] = f"{row['product_name']} {row['product_codes_text']} {row['supplier_options_text']}".lower()
    return sorted(summary, key=lambda r: r['product_name'])


def card_product_items(summary, card_filter):
    labels = {
        'under4': '4주 이하 품목',
        'under8': '8주 이하 품목',
        'surge': '판매 급등 품목',
        'drop': '판매 급감 품목',
    }
    if card_filter == 'under4':
        rows = [row for row in summary if 0 < row['inbound_recent_weeks'] <= 4]
        rows.sort(key=lambda row: row['inbound_recent_weeks'] or 999999)
    elif card_filter == 'under8':
        rows = [row for row in summary if 0 < row['inbound_recent_weeks'] <= 8]
        rows.sort(key=lambda row: row['inbound_recent_weeks'] or 999999)
    elif card_filter == 'surge':
        rows = [row for row in summary if row['sales_trend'] == '판매 급등']
        rows.sort(key=lambda row: row['inbound_recent_weeks'] or 999999)
    elif card_filter == 'drop':
        rows = [row for row in summary if row['sales_trend'] == '판매 급감']
        rows.sort(key=lambda row: row['inbound_recent_weeks'] or 999999, reverse=True)
    else:
        return '', []
    return labels[card_filter], rows


def dashboard(request):
    latest_file = latest_stock_file(request.GET.get('upload_id'))
    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file).order_by('product_name', 'option_name') if latest_file else ProductOptionMetric.objects.none()
    option_rows = live_option_rows(metrics, latest_file)
    summary = summarize_products(option_rows)
    all_summary = list(summary)
    card_filter = request.GET.get('card', '').strip()
    card_title, card_items = card_product_items(all_summary, card_filter)
    search_query = request.GET.get('q', '').strip()
    trend_filter = normalize_sales_trend(request.GET.get('trend', '').strip())
    inbound_filter = request.GET.get('inbound', '').strip()
    if search_query:
        lowered_query = search_query.lower()
        summary = [row for row in summary if lowered_query in row['search_text']]
    if trend_filter:
        summary = [row for row in summary if row['sales_trend'] == trend_filter]
    if inbound_filter == 'yes':
        summary = [row for row in summary if row['inbound_qty'] > 0]
    elif inbound_filter == 'no':
        summary = [row for row in summary if row['inbound_qty'] <= 0]
    distribution = {
        '0~4주': sum(1 for row in all_summary if 0 < row['inbound_recent_weeks'] <= 4),
        '4~8주': sum(1 for row in all_summary if 4 < row['inbound_recent_weeks'] <= 8),
        '8~12주': sum(1 for row in all_summary if 8 < row['inbound_recent_weeks'] <= 12),
        '12주 이상': sum(1 for row in all_summary if row['inbound_recent_weeks'] > 12),
    }
    planned_inbound_products = set(InboundSchedule.objects.filter(status=InboundSchedule.Status.PLANNED).values_list('product_name', flat=True))
    context = {
        'latest_file': latest_file,
        'summary': summary,
        'card_filter': card_filter,
        'card_title': card_title,
        'card_items': card_items,
        'total_products': len(all_summary),
        'total_options': len(option_rows),
        'under_4_count': sum(1 for row in all_summary if 0 < row['inbound_recent_weeks'] <= 4),
        'under_8_count': sum(1 for row in all_summary if 0 < row['inbound_recent_weeks'] <= 8),
        'surge_count': sum(1 for row in all_summary if row['sales_trend'] == '판매 급등'),
        'drop_count': sum(1 for row in all_summary if row['sales_trend'] == '판매 급감'),
        'no_inbound_count': sum(1 for row in all_summary if row['product_name'] not in planned_inbound_products),
        'risk_count': sum(1 for row in all_summary if 0 < row['inbound_recent_weeks'] <= 4),
        'distribution': distribution,
        'top_surges': [row for row in all_summary if row['sales_trend'] in ['판매 급등', '판매 상승']][:10],
        'top_drops': [row for row in all_summary if row['sales_trend'] in ['판매 급감', '판매 하락']][:10],
        'upload_form': MultiUploadInventoryForm(),
        'search_query': search_query,
        'trend_filter': trend_filter,
        'inbound_filter': inbound_filter,
        'recent_products': request.session.get('recent_products', []),
        'favorite_products': request.session.get('favorite_products', []),
        'last_product_name': request.session.get('last_product_name', ''),
        'last_upload_id': request.session.get('last_upload_id', latest_file.id if latest_file else ''),
        'stock_uploads': UploadedFile.objects.filter(file_type__in=[UploadedFile.FileType.STOCK_SALES, UploadedFile.FileType.LEGACY], status=UploadedFile.Status.COMPLETED).order_by('-reference_date', '-created_at')[:20],
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
    latest_file = latest_stock_file(request.GET.get('upload_id'))
    upload_id = latest_file.id if latest_file else None
    favorites = request.session.get('favorite_products', [])
    if request.GET.get('toggle_favorite') == '1':
        if product_name in favorites:
            favorites = [item for item in favorites if item != product_name]
            messages.success(request, '즐겨찾기에서 제거했습니다.')
        else:
            favorites.insert(0, product_name)
            messages.success(request, '즐겨찾기에 추가했습니다.')
        request.session['favorite_products'] = favorites[:20]
        request.session.modified = True
        return redirect(f"{reverse('product_detail', kwargs={'product_name': product_name})}?upload_id={upload_id or ''}")

    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file, product_name=product_name).order_by('option_name') if latest_file else ProductOptionMetric.objects.none()
    option_rows = live_option_rows(metrics, latest_file)
    product_names = list(ProductOptionMetric.objects.filter(uploaded_file=latest_file).values_list('product_name', flat=True).distinct().order_by('product_name')) if latest_file else []
    previous_product, next_product = product_navigation(product_names, product_name)
    remember_product(request, product_name, upload_id)
    return render(request, 'inventory/product_detail.html', {
        'product_name': product_name,
        'metrics': option_rows,
        'latest_file': latest_file,
        'previous_product': previous_product,
        'next_product': next_product,
        'recent_products': request.session.get('recent_products', []),
        'favorite_products': request.session.get('favorite_products', []),
        'is_favorite': product_name in request.session.get('favorite_products', []),
    })


def inbound_schedule(request):
    today = timezone.localdate()
    if request.method == 'POST':
        action = request.POST.get('action')
        inbound_id = request.POST.get('inbound_id')
        order_number = request.POST.get('order_number', '').strip()
        if action == 'bulk_delete' and order_number:
            deleted, _ = InboundSchedule.objects.filter(order_number=order_number).delete()
            messages.success(request, f'발주번호 {order_number} 입고예정 {deleted}건을 일괄 삭제했습니다.')
            return redirect('inbound_schedule')
        if action == 'bulk_update' and order_number:
            update_fields = {}
            inbound_date = parse_date(request.POST.get('bulk_inbound_date'), today)
            memo = request.POST.get('bulk_memo', '').strip()
            if request.POST.get('bulk_inbound_date', '').strip():
                update_fields['inbound_date'] = inbound_date
            if memo:
                update_fields['memo'] = memo
            if update_fields:
                updated = InboundSchedule.objects.filter(order_number=order_number).update(**update_fields)
                messages.success(request, f'발주번호 {order_number} 입고예정 {updated}건을 일괄 수정했습니다.')
            else:
                messages.error(request, '일괄 수정할 입고예정일 또는 비고를 입력해주세요.')
            return redirect('inbound_schedule')
        if action == 'delete' and inbound_id:
            InboundSchedule.objects.filter(pk=inbound_id).delete()
            messages.success(request, '입고예정 건을 삭제했습니다.')
            return redirect('inbound_schedule')

        form = InboundScheduleForm(request.POST)
        if form.is_valid():
            inbound_date = parse_date(form.cleaned_data['inbound_date'], today)
            target = InboundSchedule.objects.filter(pk=inbound_id).first() if inbound_id else None
            if not target:
                latest_inbound_upload = UploadedFile.objects.filter(file_type=UploadedFile.FileType.INBOUND_SCHEDULE).order_by('-created_at').first()
                target = InboundSchedule(uploaded_file=latest_inbound_upload or UploadedFile.objects.create(
                    original_name='manual-inbound',
                    file='manual/inbound.txt',
                    file_type=UploadedFile.FileType.INBOUND_SCHEDULE,
                    status=UploadedFile.Status.COMPLETED,
                    message='화면에서 직접 등록한 입고예정입니다.',
                ))
            target.order_number = form.cleaned_data['order_number']
            target.supplier_option_name = form.cleaned_data['supplier_option_name']
            target.product_name = form.cleaned_data['product_name']
            target.option_name = form.cleaned_data['option_name']
            target.inbound_date = inbound_date
            target.quantity = form.cleaned_data['quantity']
            target.memo = form.cleaned_data['memo']
            target.status = InboundSchedule.Status.PLANNED
            target.is_completed = False
            target.save()
            messages.success(request, '입고예정 건을 저장했습니다.')
        else:
            messages.error(request, '입고예정 입력값을 확인해주세요.')
        return redirect('inbound_schedule')

    inbound_schedules = InboundSchedule.objects.order_by('order_number', 'inbound_date', 'product_name', 'option_name')
    groups = []
    grouped = defaultdict(lambda: {'option_count': 0, 'quantity': 0, 'inbound_dates': set(), 'memo': ''})
    for item in inbound_schedules:
        if not item.order_number:
            continue
        group = grouped[item.order_number]
        group['order_number'] = item.order_number
        group['option_count'] += 1
        group['quantity'] += item.quantity or 0
        if item.inbound_date:
            group['inbound_dates'].add(item.inbound_date)
        if item.memo and not group['memo']:
            group['memo'] = item.memo
    for group in grouped.values():
        group['inbound_dates'] = ', '.join(sorted(date.strftime('%Y-%m-%d') for date in group['inbound_dates'])) or '날짜 미정'
        groups.append(group)
    groups.sort(key=lambda row: row['order_number'])
    return render(request, 'inventory/inbound_schedule.html', {
        'inbound_schedules': inbound_schedules,
        'inbound_groups': groups,
        'today': today,
        'inbound_form': InboundScheduleForm(),
        'recent_products': request.session.get('recent_products', []),
        'favorite_products': request.session.get('favorite_products', []),
        'last_product_name': request.session.get('last_product_name', ''),
        'last_upload_id': request.session.get('last_upload_id', ''),
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
    columns = ['발주번호', '공급처옵션명', '상품명', '옵션', '수량', '일정', '상태', '비고']
    sample = pd.DataFrame([
        ['2026/05/28-1', 'SUP-001', '촤르르반팔', '블랙/M', 40, '2026-06-19', '예정', '1차 입고'],
        ['2026/06/10-2', 'SUP-003', '모자', '베이지/F', 100, '', '예정', '발주완료, 일정 미정'],
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
