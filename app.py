import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import data_logic as dl
import template_gen as tg
import utils

# --- Page Config ---
st.set_page_config(page_title="재고·발주 관리 시스템", layout="wide")

# --- Session State ---
if 'stock_df' not in st.session_state:
    st.session_state.stock_df = pd.DataFrame()
if 'incoming_df' not in st.session_state:
    st.session_state.incoming_df = pd.DataFrame()
if 'yearly_df' not in st.session_state:
    st.session_state.yearly_df = pd.DataFrame()

# --- Sidebar: Data Upload & Templates ---
with st.sidebar:
    st.title("📦 데이터 관리")
    
    with st.expander("📄 양식 다운로드", expanded=False):
        st.download_button(
            label="1️⃣ 재고/판매 양식",
            data=tg.create_stock_template(),
            file_name="stock_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="2️⃣ 연도별 판매 양식",
            data=tg.create_yearly_sales_template(),
            file_name="yearly_sales_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="3️⃣ 입고 예정 양식",
            data=tg.create_incoming_template(),
            file_name="incoming_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.subheader("📤 데이터 업로드")
    u_stock = st.file_uploader("1️⃣ 재고 및 판매 데이터", type=['xlsx'])
    u_yearly = st.file_uploader("2️⃣ 연도별 판매 데이터", type=['xlsx'])
    u_incoming = st.file_uploader("3️⃣ 입고 예정 데이터", type=['xlsx'])

    if u_stock: st.session_state.stock_df = pd.read_excel(u_stock)
    if u_yearly: st.session_state.yearly_df = pd.read_excel(u_yearly)
    if u_incoming: st.session_state.incoming_df = pd.read_excel(u_incoming)

    if st.button("🎯 테스트용 샘플 데이터 로드"):
        st.session_state.stock_df = pd.DataFrame({
            '이카운트코드': ['E001', 'E002', 'E003', 'E004'],
            '상품명': ['여름부들이 시즌1', '여름부들이 시즌1', '여름부들이 시즌1', '린넨셔츠'],
            '옵션': ['S', 'M', 'L', 'FREE'],
            '가용재고': [10, 50, 100, 20],
            '최근한주판매수량': [30, 20, 10, 50],
            '총판매수량': [200, 150, 50, 300],
            '오픈일': ['2025-01-01', '2025-01-01', '2025-01-01', '2025-02-01'],
            '품목명(구매팀확인용)': ['여름부들이', '여름부들이', '여름부들이', '린넨셔츠']
        })
        st.session_state.yearly_df = pd.DataFrame({
            '이카운트코드': ['E001', 'E002', 'E003'],
            '품목명': ['여름부들이 시즌1', '여름부들이 시즌1', '여름부들이 시즌1'],
            '품목명(구매팀확인용)': ['여름부들이', '여름부들이', '여름부들이'],
            '2025-01': [100, 100, 100], '2025-02': [120, 120, 120], '2025-03': [110, 110, 110]
        })
        st.success("✅ 샘플 데이터가 로드되었습니다.")

# --- Main Navigation ---
menu = st.tabs(["1️⃣ 대시보드 요약", "2️⃣ 품목별 상세 데이터", "3️⃣ 연도별 판매 분석", "4️⃣ 입고 일정 관리"])

if st.session_state.stock_df.empty:
    st.info("💡 왼쪽 사이드바에서 데이터를 업로드하거나 샘플 데이터를 로드해주세요.")
    st.stop()

# Data Processing
df_processed = dl.calculate_sales_metrics(st.session_state.stock_df, st.session_state.incoming_df)
df_agg = dl.aggregate_by_product(df_processed)

# --- 1. Dashboard Summary ---
with menu[0]:
    st.header("📦 품목별 재고 현황 요약")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 품목 수", len(df_agg))
    col2.metric("🚨 긴급 발주 필요 (옵션 기준)", len(df_processed[df_processed['발주알람'] == '긴급']))
    col3.metric("🔥 판매 급상승 (옵션 기준)", len(df_processed[df_processed['판매증감여부'] == '판매급등']))

    st.subheader("품목별 요약 현황")
    summary_cols = ['상품명', '가용재고', '총입고예정수량', '입고후재고', '최근한주판매수량', '판매가능주_최근', '총판매수량', '판매가능주_총']
    
    # 데이터 표시 (컬럼 선택적 표시)
    display_df = df_agg[summary_cols].copy()
    display_df['가용재고'] = display_df['가용재고'].astype(int)
    display_df['총입고예정수량'] = display_df['총입고예정수량'].astype(int)
    display_df['입고후재고'] = display_df['입고후재고'].astype(int)
    display_df['최근한주판매수량'] = display_df['최근한주판매수량'].astype(int)
    display_df['판매가능주_최근'] = display_df['판매가능주_최근'].round(1)
    display_df['총판매수량'] = display_df['총판매수량'].astype(int)
    display_df['판매가능주_총'] = display_df['판매가능주_총'].round(1)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.download_button(
        label="📥 요약 데이터 다운로드 (Excel)",
        data=utils.to_excel(display_df),
        file_name="summary_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- 2. Product Detail Data ---
with menu[1]:
    st.header("🔍 품목별 상세 데이터 (옵션별)")
    
    search = st.text_input("상품명 또는 이카운트코드 검색")
    df_filtered = df_processed.copy()
    if search:
        df_filtered = df_filtered[
            (df_filtered['상품명'].str.contains(search, case=False, na=False)) | 
            (df_filtered['이카운트코드'].str.contains(search, case=False, na=False))
        ]
    
    detail_cols = ['이카운트코드', '상품명', '옵션', '가용재고', '총입고예정수량', '입고후재고', 
                   '최근한주판매수량', '판매가능주_최근', '총판매수량', '판매가능주_총', '판매증감여부', '발주알람']
    
    display_detail = df_filtered[detail_cols].copy()
    display_detail['가용재고'] = display_detail['가용재고'].astype(int)
    display_detail['총입고예정수량'] = display_detail['총입고예정수량'].astype(int)
    display_detail['입고후재고'] = display_detail['입고후재고'].astype(int)
    display_detail['최근한주판매수량'] = display_detail['최근한주판매수량'].astype(int)
    display_detail['판매가능주_최근'] = display_detail['판매가능주_최근'].round(1)
    display_detail['총판매수량'] = display_detail['총판매수량'].astype(int)
    display_detail['판매가능주_총'] = display_detail['판매가능주_총'].round(1)
    
    st.dataframe(display_detail, use_container_width=True, hide_index=True)
    
    st.download_button(
        label="📥 상세 데이터 다운로드 (Excel)",
        data=utils.to_excel(display_detail),
        file_name="detail_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- 3. Yearly Sales Analysis ---
with menu[2]:
    st.header("📈 연도별 판매 추이 분석")
    if st.session_state.yearly_df.empty:
        st.info("💡 연도별 판매 데이터를 업로드해주세요.")
    else:
        # 품목명(구매팀확인용) 기준 그룹화
        if '품목명(구매팀확인용)' in st.session_state.yearly_df.columns:
            purchase_groups = st.session_state.yearly_df['품목명(구매팀확인용)'].unique()
            selected_group = st.selectbox("분석할 품목 그룹 선택", purchase_groups)
            
            # 대표 품목 선정 (요구사항 12번)
            rep_product = dl.get_representative_product(st.session_state.stock_df, selected_group)
            st.subheader(f"📊 {selected_group} 판매 추이 (대표 품목: {rep_product})")
            
            # 데이터 추출
            group_data = st.session_state.yearly_df[st.session_state.yearly_df['품목명(구매팀확인용)'] == selected_group]
            month_cols = [c for c in group_data.columns if '-' in c and len(c) == 7]  # YYYY-MM 형식
            
            if month_cols:
                ts_data = group_data[month_cols].sum().reset_index()
                ts_data.columns = ['Month', 'Sales']
                ts_data['Sales'] = ts_data['Sales'].astype(int)
                
                # 최근 월 및 상승률 계산
                if len(ts_data) > 0:
                    last_month = ts_data.iloc[-1]
                    prev_month = ts_data.iloc[-2] if len(ts_data) > 1 else None
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(f"최근 월 판매 ({last_month['Month']})", f"{int(last_month['Sales']):,} 개")
                    
                    if prev_month is not None and prev_month['Sales'] > 0:
                        growth = (last_month['Sales'] - prev_month['Sales']) / prev_month['Sales'] * 100
                        m2.metric("전월 대비 상승률", f"{growth:.1f}%")
                    
                    # 전년 동월 대비 상승률 계산 (12개월 이상 데이터가 있을 경우)
                    if len(ts_data) > 12:
                        year_ago = ts_data.iloc[-13]
                        if year_ago['Sales'] > 0:
                            yoy_growth = (last_month['Sales'] - year_ago['Sales']) / year_ago['Sales'] * 100
                            m3.metric("전년 동월 대비 상승률", f"{yoy_growth:.1f}%")
                    
                    # 시계열 그래프
                    fig = px.line(ts_data, x='Month', y='Sales', title=f"{selected_group} 최근 24개월 판매 추이", markers=True)
                    fig.update_layout(hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ 날짜 형식의 컬럼(예: 2025-01)이 데이터에 없습니다.")
        else:
            st.warning("⚠️ '품목명(구매팀확인용)' 컬럼이 데이터에 없습니다.")

# --- 4. Incoming Management ---
with menu[3]:
    st.header("📅 입고 일정 관리")
    if st.session_state.incoming_df.empty:
        st.info("💡 입고 예정 데이터를 업로드해주세요.")
    else:
        st.subheader("입고 예정 리스트")
        
        # 입고 예정 데이터 표시
        incoming_display = st.session_state.incoming_df.copy()
        incoming_display['입고예정수량'] = incoming_display['입고예정수량'].astype(int)
        st.dataframe(incoming_display, use_container_width=True, hide_index=True)
        
        # 캘린더 형태의 시각화 (날짜별 입고량)
        if '입고예정일' in st.session_state.incoming_df.columns:
            inc_df = st.session_state.incoming_df.copy()
            inc_df['입고예정일'] = pd.to_datetime(inc_df['입고예정일'])
            cal_data = inc_df.groupby('입고예정일')['입고예정수량'].sum().reset_index()
            cal_data = cal_data.sort_values('입고예정일')
            
            fig_cal = px.bar(
                cal_data,
                x='입고예정일',
                y='입고예정수량',
                title="날짜별 입고 예정 수량",
                labels={'입고예정일': '입고 예정일', '입고예정수량': '수량'}
            )
            st.plotly_chart(fig_cal, use_container_width=True)
        
        st.download_button(
            label="📥 입고 일정 다운로드 (Excel)",
            data=utils.to_excel(incoming_display),
            file_name="incoming_schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Footer ---
st.divider()
st.caption("📌 재고·발주 관리 시스템 | 마지막 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
