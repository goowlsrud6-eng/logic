'''
엑셀 템플릿 생성 모듈
'''
import pandas as pd
import io

def create_stock_template():
    """재고 및 판매 데이터 양식 생성"""
    columns = ['이카운트코드', '상품명', '옵션', '가용재고', '최근한주판매수량', '총판매수량', '오픈일']
    df = pd.DataFrame(columns=columns)
    df.loc[0] = ['E001', '여름부들이 시즌1', '기본', 100, 10, 50, '2025-04-01']
    df.loc[1] = ['E002', '여름부들이 시즌1', '특대', 50, 5, 25, '2025-04-01']
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='재고_판매_데이터')
    return output.getvalue()

def create_yearly_sales_template():
    """연도별 판매 데이터 양식 생성"""
    months = [f"2025-{str(i).zfill(2)}" for i in range(1, 13)] + [f"2026-{str(i).zfill(2)}" for i in range(1, 13)]
    columns = ['이카운트코드', '품목명', '품목명(구매팀확인용)'] + months
    df = pd.DataFrame(columns=columns)
    sample_row = ['E001', '여름부들이 시즌1', '여름부들이'] + list(range(100, 100 + 24))
    df.loc[0] = sample_row
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='연도별_판매_데이터')
    return output.getvalue()

def create_incoming_template():
    """입고 예정 데이터 양식 생성"""
    columns = ['이카운트코드', '상품명', '옵션', '입고예정수량', '입고예정일', '비고']
    df = pd.DataFrame(columns=columns)
    df.loc[0] = ['E001', '여름부들이 시즌1', '기본', 200, '2026-03-20', '1차 입고']
    df.loc[1] = ['E001', '여름부들이 시즌1', '기본', 150, '2026-04-05', '2차 입고']
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='입고_예정_데이터')
    return output.getvalue()
