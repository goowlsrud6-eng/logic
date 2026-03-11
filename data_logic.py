import pandas as pd
import numpy as np
from datetime import datetime

def calculate_sales_metrics(df_stock, df_incoming, today_date=None):
    if today_date is None:
        today_date = pd.to_datetime(datetime.now().date())
    else:
        today_date = pd.to_datetime(today_date)

    df = df_stock.copy()
    
    # 1. 입고 예정 데이터 집계 (이카운트코드 기준)
    if df_incoming is not None and not df_incoming.empty:
        if '이카운트코드' in df_incoming.columns and '입고예정수량' in df_incoming.columns:
            incoming_sum = df_incoming.groupby('이카운트코드')['입고예정수량'].sum().reset_index()
            incoming_sum.columns = ['이카운트코드', '총입고예정수량']
            df = pd.merge(df, incoming_sum, on='이카운트코드', how='left')
        else:
            df['총입고예정수량'] = 0
    else:
        df['총입고예정수량'] = 0

    df['총입고예정수량'] = df['총입고예정수량'].fillna(0)
    df['입고후재고'] = df['가용재고'] + df['총입고예정수량']
    
    # 오픈일 데이터 타입 변환
    df['오픈일'] = pd.to_datetime(df['오픈일'])

    # 2. 판매일수 계산 (최근 한주 기준)
    # 판매일수 = min(7, 오늘날짜 - 오픈일 + 1)
    df['판매일수_최근'] = df['오픈일'].apply(lambda x: min(7, (today_date - x).days + 1))
    df.loc[df['판매일수_최근'] < 1, '판매일수_최근'] = 1

    # 3. 최근한주 기준 판매가능주 계산
    # 일평균 판매수량 = 최근한주판매수량 / 판매일수
    df['일평균판매수량_최근'] = df['최근한주판매수량'] / df['판매일수_최근']
    # 최근한주 판매가능주 = 입고후재고 / (일평균 판매수량 * 7)
    df['판매가능주_최근'] = df.apply(lambda x: x['입고후재고'] / (x['일평균판매수량_최근'] * 7) if x['일평균판매수량_최근'] > 0 else 999, axis=1)

    # 4. 총판매 기준 판매가능주 계산
    # 총 판매일수 = max(7, 오늘 - 오픈일 + 1)
    df['총판매일수'] = df['오픈일'].apply(lambda x: max(7, (today_date - x).days + 1))
    # 일평균 판매량 = 총판매수량 / 총 판매일수
    df['일평균판매수량_총'] = df['총판매수량'] / df['총판매일수']
    # 총판매 기준 판매가능주 = 입고후재고 / (일평균 판매량 * 7)
    df['판매가능주_총'] = df.apply(lambda x: x['입고후재고'] / (x['일평균판매수량_총'] * 7) if x['일평균판매수량_총'] > 0 else 999, axis=1)

    # 5. 판매 증감 판단 로직
    diff = df['판매가능주_총'] - df['판매가능주_최근']
    
    def judge_trend(d):
        if d >= 10: return "판매급등"
        elif d >= 3: return "판매상승"
        elif d <= -10: return "판매급감"
        elif d <= -3: return "판매하락"
        else: return "변화 없음"
    
    df['판매증감여부'] = diff.apply(judge_trend)

    # 6. 발주 알람 로직
    df['판단판매가능주'] = df[['판매가능주_최근', '판매가능주_총']].min(axis=1)
    
    def judge_alarm(w):
        if w <= 4: return "긴급"
        elif w <= 8: return "관심 필요"
        else: return "정상"
        
    df['발주알람'] = df['판단판매가능주'].apply(judge_alarm)
    
    return df

def aggregate_by_product(df, today_date=None):
    if today_date is None:
        today_date = pd.to_datetime(datetime.now().date())
    else:
        today_date = pd.to_datetime(today_date)
        
    agg_dict = {
        '오픈일': 'min',
        '가용재고': 'sum',
        '총입고예정수량': 'sum',
        '입고후재고': 'sum',
        '최근한주판매수량': 'sum',
        '총판매수량': 'sum'
    }
    df_agg = df.groupby('상품명').agg(agg_dict).reset_index()
    
    df_agg['판매일수_최근'] = df_agg['오픈일'].apply(lambda x: min(7, (today_date - x).days + 1))
    df_agg.loc[df_agg['판매일수_최근'] < 1, '판매일수_최근'] = 1
    df_agg['일평균판매수량_최근'] = df_agg['최근한주판매수량'] / df_agg['판매일수_최근']
    df_agg['판매가능주_최근'] = df_agg.apply(lambda x: x['입고후재고'] / (x['일평균판매수량_최근'] * 7) if x['일평균판매수량_최근'] > 0 else 999, axis=1)
    
    df_agg['총판매일수'] = df_agg['오픈일'].apply(lambda x: max(7, (today_date - x).days + 1))
    df_agg['일평균판매수량_총'] = df_agg['총판매수량'] / df_agg['총판매일수']
    df_agg['판매가능주_총'] = df_agg.apply(lambda x: x['입고후재고'] / (x['일평균판매수량_총'] * 7) if x['일평균판매수량_총'] > 0 else 999, axis=1)
    
    return df_agg

def get_representative_product(df_stock, purchase_name, today_date=None):
    if today_date is None:
        today_date = pd.to_datetime(datetime.now().date())
    else:
        today_date = pd.to_datetime(today_date)
        
    if '품목명(구매팀확인용)' not in df_stock.columns:
        return "N/A"
        
    group_df = df_stock[df_stock['품목명(구매팀확인용)'] == purchase_name].copy()
    if group_df.empty:
        return "N/A"
        
    group_df['오픈일'] = pd.to_datetime(group_df['오픈일'])
    valid_df = group_df[group_df['오픈일'] <= today_date]
    
    if valid_df.empty:
        return group_df.sort_values('오픈일').iloc[0]['상품명']
        
    return valid_df.sort_values('오픈일', ascending=False).iloc[0]['상품명']
