
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.title('Plotly 차트 통합')

# 제품 판매량 데이터 생성
dates = [datetime.now() - timedelta(days=x) for x in range(100, 0, -1)]
np.random.seed(42)
sales = np.random.randint(50, 200, 100)

# Plotly 선 그래프
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=sales,
    mode='lines',
    name='일일 판매량',
    line=dict(color='blue', width=2)
))

fig.update_layout(
    title='인터랙티브 판매량 차트',
    xaxis_title='날짜',
    yaxis_title='판매량 (개)',
    height=400
)

st.plotly_chart(fig, use_container_width=True)


# 광고비와 매출의 관계
np.random.seed(42)
ad_spend = np.random.randint(10, 100, 50)
revenue = ad_spend * 2.5 + np.random.normal(0, 20, 50)

scatter_fig = go.Figure()
scatter_fig.add_trace(go.Scatter(
    x=ad_spend,
    y=revenue,
    mode='markers',
    name='데이터 포인트',
    marker=dict(
        size=8,
        color='lightblue',
        line=dict(width=1, color='navy')
    )
))

scatter_fig.update_layout(
    title='광고비 vs 매출 관계',
    xaxis_title='광고비 (만원)',
    yaxis_title='매출 (만원)',
    height=400
)

st.subheader('산점도 차트')
st.plotly_chart(scatter_fig, use_container_width=True)


# 설문조사 결과
survey_data = {
    '매우 만족': 25,
    '만족': 40, 
    '보통': 20,
    '불만족': 10,
    '매우 불만족': 5
}

pie_fig = go.Figure(data=go.Pie(
    labels=list(survey_data.keys()),
    values=list(survey_data.values()),
    hole=0.3
))

pie_fig.update_layout(
    title='고객 만족도 설문 결과',
    height=400
)

st.subheader('만족도 분포')
st.plotly_chart(pie_fig, use_container_width=True)


# 학생들의 키 분포
np.random.seed(42)
heights = np.random.normal(170, 10, 200)

hist_fig = go.Figure()
hist_fig.add_trace(go.Histogram(
    x=heights,
    nbinsx=20,
    name='키 분포',
    marker_color='lightgreen'
))

hist_fig.update_layout(
    title='학생 키 분포',
    xaxis_title='키 (cm)',
    yaxis_title='학생 수',
    height=400
)

st.subheader('키 분포 히스토그램')
st.plotly_chart(hist_fig, use_container_width=True)
