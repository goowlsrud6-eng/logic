from django import forms


class UploadInventoryFileForm(forms.Form):
    week_label = forms.CharField(
        label='기준 주차',
        required=False,
        max_length=20,
        help_text='예: 0615-0619. 비워두면 파일/시트명에서 추정합니다.',
    )
    file = forms.FileField(label='특별재고 엑셀 파일')
