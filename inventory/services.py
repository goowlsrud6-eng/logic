import hashlib
import re
from pathlib import Path

import pandas as pd
from django.utils import timezone

from .models import ProductOptionMetric, UploadedFile

WEEK_RE = re.compile(r'(\d{4}-\d{4})')

COLUMN_ALIASES = {
    'product_code': ['상품코드', '공급처옵션', '이카운트코드'],
    'product_name': ['상품명', '품목명'],
    'option_name': ['옵션명', '옵션'],
    'available_stock': ['가용재고', '현재고'],
    'inbound_qty': ['총입고예정', '입고예정수량', '입고예정'],
    'delivery_qty': ['배송'],
    'pending_qty': ['미출고', '접수'],
    'recent_week_sales': ['판매수량최근한주', '최근한주판매수량', '최근한주수량'],
    'total_sales': ['판매수량총판매', '총판매수량'],
    'sales_days': ['판매일수', '일수'],
    'open_date': ['오픈일', '판매시작일'],
}


def normalize_header(value):
    return str(value or '').replace('\n', '').replace('\r', '').replace(' ', '').strip()


def clean_option_name(value):
    text = str(value or '')
    text = re.sub(r'★\s*\d+차\s*', '', text)
    return text.strip()


def sha256_file(file_obj):
    digest = hashlib.sha256()
    for chunk in file_obj.chunks():
        digest.update(chunk)
    file_obj.seek(0)
    return digest.hexdigest()


def infer_week_label(explicit_label, workbook_path):
    if explicit_label:
        return explicit_label
    match = WEEK_RE.search(Path(workbook_path).name)
    return match.group(1) if match else ''


def find_header_row(raw_df):
    for idx in range(min(5, len(raw_df))):
        headers = [normalize_header(v) for v in raw_df.iloc[idx].tolist()]
        if any('상품명' in h or '품목명' in h for h in headers) and any('가용재고' in h or '현재고' in h for h in headers):
            return idx
    return 1 if len(raw_df) > 1 else 0


def build_column_map(columns):
    normalized = {col: normalize_header(col) for col in columns}
    mapped = {}
    for target, aliases in COLUMN_ALIASES.items():
        for col, header in normalized.items():
            if any(alias in header for alias in aliases):
                mapped[target] = col
                break
    return mapped


def as_number(value):
    if pd.isna(value):
        return 0.0
    
    numeric = pd.to_numeric(value, errors='coerce')
    return 0.0 if pd.isna(numeric) else float(numeric)


def safe_weeks(stock, weekly_sales):
    if weekly_sales <= 0:
        return 0.0
    return round(stock / weekly_sales, 1)


def judge_stock_status(weeks):
    if weeks <= 0:
        return '판매없음'
    if weeks <= 1:
        return '긴급'
    if weeks <= 2:
        return '주의'
    if weeks <= 4:
        return '관찰'
    return '정상'



def metrics_from_dataframe(uploaded_file, df, week_label, source_sheet='기초파일'):
    colmap = build_column_map(df.columns)
    required = ['product_name', 'available_stock', 'recent_week_sales', 'total_sales']
    missing = [name for name in required if name not in colmap]
    if missing:
        raise ValueError('필수 컬럼이 없습니다: ' + ', '.join(missing))

    rows = []
    for _, row in df.dropna(how='all').iterrows():
        product_name = str(row.get(colmap['product_name'], '') or '').strip()
        if not product_name or '합계' in product_name:
            continue
        option_name = clean_option_name(row.get(colmap.get('option_name'), '')) if 'option_name' in colmap else ''
        code = str(row.get(colmap.get('product_code'), '') or '').strip() if 'product_code' in colmap else ''
        stock = as_number(row.get(colmap['available_stock']))
        inbound = as_number(row.get(colmap.get('inbound_qty'))) if 'inbound_qty' in colmap else 0
        recent_sales = as_number(row.get(colmap['recent_week_sales']))
        total_sales = as_number(row.get(colmap['total_sales']))
        days = as_number(row.get(colmap.get('sales_days'))) if 'sales_days' in colmap else 0
        if days <= 0 and 'open_date' in colmap:
            open_date = pd.to_datetime(row.get(colmap['open_date']), errors='coerce')
            if pd.notna(open_date):
                days = max((timezone.localdate() - open_date.date()).days + 1, 1)
        stock_after = stock + inbound
        weekly_total_rate = (total_sales / days * 7) if total_sales > 0 and days > 0 else 0
        current_recent = safe_weeks(stock, recent_sales)
        inbound_recent = safe_weeks(stock_after, recent_sales)
        current_total = safe_weeks(stock, weekly_total_rate)
        inbound_total = safe_weeks(stock_after, weekly_total_rate)

        rows.append(ProductOptionMetric(
            uploaded_file=uploaded_file,
            source_sheet=source_sheet,
            week_label=week_label,
            product_code=code,
            product_name=product_name,
            option_name=option_name,
            available_stock=stock,
            inbound_qty=inbound,
            stock_after_inbound=stock_after,
            delivery_qty=as_number(row.get(colmap.get('delivery_qty'))) if 'delivery_qty' in colmap else 0,
            pending_qty=as_number(row.get(colmap.get('pending_qty'))) if 'pending_qty' in colmap else 0,
            recent_week_sales=recent_sales,
            total_sales=total_sales,
            sales_days=days,
            current_recent_weeks=current_recent,
            inbound_recent_weeks=inbound_recent,
            current_total_weeks=current_total,
            inbound_total_weeks=inbound_total,
            status=judge_stock_status(inbound_recent or current_recent),
        ))
    return rows


def finish_upload(uploaded_file, rows):
    ProductOptionMetric.objects.filter(uploaded_file=uploaded_file).delete()
    ProductOptionMetric.objects.bulk_create(rows)
    uploaded_file.status = UploadedFile.Status.COMPLETED
    uploaded_file.message = f'{len(rows)}개 옵션 데이터를 처리했습니다.'
    uploaded_file.save(update_fields=['status', 'message'])
    return len(rows)


def parse_basic_inventory_workbook(uploaded_file):
    path = uploaded_file.file.path
    excel = pd.ExcelFile(path)
    sheet_name = excel.sheet_names[0]
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    header_row = find_header_row(raw)
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    week_label = infer_week_label(uploaded_file.week_label, path)
    rows = metrics_from_dataframe(uploaded_file, df, week_label, source_sheet=sheet_name)
    return finish_upload(uploaded_file, rows)


def parse_special_stock_workbook(uploaded_file):
    path = uploaded_file.file.path
    excel = pd.ExcelFile(path)
    week_label = infer_week_label(uploaded_file.week_label, path)
    rows = []

    for sheet_name in excel.sheet_names:
        if sheet_name == '옵션채우기' or '요약' in sheet_name:
            continue
        if '(' not in sheet_name and ')' not in sheet_name:
            continue

        raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
        if raw.empty:
            continue
        header_row = find_header_row(raw)
        df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
        df = df.dropna(how='all')
        colmap = build_column_map(df.columns)
        if 'product_name' not in colmap or 'available_stock' not in colmap:
            continue

        sheet_week = WEEK_RE.search(sheet_name)
        row_week_label = week_label or (sheet_week.group(1) if sheet_week else '')

        for _, row in df.iterrows():
            product_name = str(row.get(colmap['product_name'], '') or '').strip()
            if not product_name or '합계' in product_name:
                continue
            option_name = clean_option_name(row.get(colmap.get('option_name'), '')) if 'option_name' in colmap else ''
            code = str(row.get(colmap.get('product_code'), '') or '').strip() if 'product_code' in colmap else ''
            stock = as_number(row.get(colmap['available_stock']))
            inbound = as_number(row.get(colmap.get('inbound_qty'))) if 'inbound_qty' in colmap else 0
            recent_sales = as_number(row.get(colmap.get('recent_week_sales'))) if 'recent_week_sales' in colmap else 0
            total_sales = as_number(row.get(colmap.get('total_sales'))) if 'total_sales' in colmap else 0
            days = as_number(row.get(colmap.get('sales_days'))) if 'sales_days' in colmap else 0
        if days <= 0 and 'open_date' in colmap:
            open_date = pd.to_datetime(row.get(colmap['open_date']), errors='coerce')
            if pd.notna(open_date):
                days = max((timezone.localdate() - open_date.date()).days + 1, 1)
            stock_after = stock + inbound
            weekly_total_rate = (total_sales / days * 7) if total_sales > 0 and days > 0 else 0
            current_recent = safe_weeks(stock, recent_sales)
            inbound_recent = safe_weeks(stock_after, recent_sales)
            current_total = safe_weeks(stock, weekly_total_rate)
            inbound_total = safe_weeks(stock_after, weekly_total_rate)

            rows.append(ProductOptionMetric(
                uploaded_file=uploaded_file,
                source_sheet=sheet_name,
                week_label=row_week_label,
                product_code=code,
                product_name=product_name,
                option_name=option_name,
                available_stock=stock,
                inbound_qty=inbound,
                stock_after_inbound=stock_after,
                delivery_qty=as_number(row.get(colmap.get('delivery_qty'))) if 'delivery_qty' in colmap else 0,
                pending_qty=as_number(row.get(colmap.get('pending_qty'))) if 'pending_qty' in colmap else 0,
                recent_week_sales=recent_sales,
                total_sales=total_sales,
                sales_days=days,
                current_recent_weeks=current_recent,
                inbound_recent_weeks=inbound_recent,
                current_total_weeks=current_total,
                inbound_total_weeks=inbound_total,
                status=judge_stock_status(inbound_recent or current_recent),
            ))

    ProductOptionMetric.objects.filter(uploaded_file=uploaded_file).delete()
    ProductOptionMetric.objects.bulk_create(rows)
    uploaded_file.status = UploadedFile.Status.COMPLETED
    uploaded_file.message = f'{len(rows)}개 옵션 데이터를 처리했습니다.'
    uploaded_file.save(update_fields=['status', 'message'])
    return len(rows)
