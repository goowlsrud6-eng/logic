from django import forms


class MultiUploadInventoryForm(forms.Form):
    reference_date = forms.DateField(
        label='기준일',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='예: 2026-06-15. 입력하면 0615-0619 주차가 자동 생성됩니다.',
    )
    stock_sales_file = forms.FileField(
        label='1. 재고/판매 통합 파일',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )
    product_master_file = forms.FileField(
        label='2. 상품기본정보/오픈일 파일',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )
    inbound_schedule_file = forms.FileField(
        label='3. 입고예정 파일',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned = super().clean()
        if not any(cleaned.get(name) for name in ['stock_sales_file', 'product_master_file', 'inbound_schedule_file']):
            raise forms.ValidationError('업로드할 파일을 하나 이상 선택해주세요.')
        return cleaned


# 이전 코드/문서와의 호환을 위해 이름은 남겨둔다.
UploadInventoryFileForm = MultiUploadInventoryForm


class InboundScheduleForm(forms.Form):
    supplier_option_name = forms.CharField(label='공급처옵션명', required=False, max_length=120)
    product_name = forms.CharField(label='상품명', max_length=255)
    option_name = forms.CharField(label='옵션명', required=False, max_length=255)
    inbound_date = forms.CharField(label='입고예정일', required=False, help_text='예: 20260624, 6/24, 0624')
    quantity = forms.FloatField(label='입고예정수량', min_value=0)
    memo = forms.CharField(label='비고', required=False, max_length=255)
