from django import forms


class UploadInventoryFileForm(forms.Form):
    UPLOAD_MODE_CHOICES = [
        ('basic', '간단 기초파일: 현재고/최근한주수량/총판매수량만 업로드'),
        ('legacy', '기존 특별재고 파일: 여러 품목 시트가 있는 파일 업로드'),
    ]

    upload_mode = forms.ChoiceField(
        label='업로드 방식',
        choices=UPLOAD_MODE_CHOICES,
        initial='basic',
        help_text='앞으로는 간단 기초파일 방식을 기본으로 사용합니다.',
    )
    week_label = forms.CharField(
        label='기준 주차',
        required=False,
        max_length=20,
        help_text='예: 0615-0619. 비워도 됩니다.',
    )
    file = forms.FileField(label='엑셀 파일')
