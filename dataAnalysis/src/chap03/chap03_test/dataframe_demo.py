import streamlit as st
import pandas as pd

# 학생 성적 데이터 만들기
data = {
    '이름': ['김철수', '이영희', '박민수', '최지연'],
    '수학': [85, 92, 78, 96],
    '영어': [88, 85, 90, 93],
    '과학': [90, 88, 85, 89]
}

df = pd.DataFrame(data)
st.title('학생 성적 데이터 표시하기')
st.dataframe(df)

# 온라인 쇼핑몰 판매 데이터
sales_data = {
    '상품명': ['노트북', '마우스', '키보드', '모니터', '헤드셋'],
    '가격': [1200000, 25000, 80000, 350000, 150000],
    '판매량': [15, 120, 85, 30, 45],
    '평점': [4.5, 4.2, 4.7, 4.1, 4.6]
}

df = pd.DataFrame(sales_data)
# st.dataframe(df_sales)

# 평점에 따라 색깔 적용
def color_rating(val):
    if val >= 4.5:
        color = 'green'
    elif val >= 4.0:
        color = 'orange' 
    else:
        color = 'red'
    return f'color: {color}'

# 스타일 적용해서 표시
styled_df = df.style.format({
    '가격': '{:,}원',
    '판매량': '{:,}개',
    '평점': '{:.1f}점'
}).map(color_rating, subset=['평점'])

st.dataframe(styled_df)

# 날씨 정보 표시용 정적 테이블
weather_data = {
    '항목': ['최고 기온', '최저 기온', '습도', '강수 확률'],
    '값': ['28°C', '18°C', '65%', '30%']
}

weather_df = pd.DataFrame(weather_data)
st.table(weather_df)
