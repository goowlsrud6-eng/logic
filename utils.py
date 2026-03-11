import pandas as pd
import io

def to_excel(df):
    """
    DataFrame을 Excel 바이트 형식으로 변환
    Streamlit의 download_button에서 사용
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
