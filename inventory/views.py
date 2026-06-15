from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from .forms import UploadInventoryFileForm
from .models import ProductOptionMetric, UploadedFile
from .services import parse_special_stock_workbook, sha256_file


def dashboard(request):
    latest_file = UploadedFile.objects.filter(status=UploadedFile.Status.COMPLETED).order_by('-created_at').first()
    metrics = ProductOptionMetric.objects.filter(uploaded_file=latest_file) if latest_file else ProductOptionMetric.objects.none()
    summary = metrics.values('product_name').annotate(
        option_count=Count('id'),
        available_stock=Sum('available_stock'),
        inbound_qty=Sum('inbound_qty'),
        stock_after_inbound=Sum('stock_after_inbound'),
        recent_week_sales=Sum('recent_week_sales'),
        total_sales=Sum('total_sales'),
    ).order_by('product_name')
    context = {
        'latest_file': latest_file,
        'summary': summary,
        'total_products': summary.count(),
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
        count = parse_special_stock_workbook(record)
        messages.success(request, f'업로드 완료: {count}개 옵션 데이터를 처리했습니다.')
    except Exception as exc:
        record.status = UploadedFile.Status.FAILED
        record.message = str(exc)
        record.save(update_fields=['status', 'message'])
        messages.error(request, f'처리 실패: {exc}')
    return redirect('dashboard')
