
import streamlit as st


# 선택 상자 만들기 - 좋아하는 과일 선택
fruit = st.selectbox(
    '좋아하는 과일을 선택하세요',
    ['사과', '바나나', '오렌지', '포도']
)

st.write(f'당신이 선택한 과일은 {fruit}입니다')

# 텍스트 입력받기
name = st.text_input('이름을 입력하세요')
age = st.number_input('나이를 입력하세요', min_value=0, max_value=120)

if name and age:
    st.write(f'{name}님은 {age}살입니다')


# 슬라이더로 값 조정하기
temperature = st.slider('온도를 선택하세요', 0, 40, 25)
st.write(f'선택한 온도는 {temperature}도입니다')


# 라디오 버튼
color = st.radio(
    '좋아하는 색깔을 선택하세요',
    ['빨강', '파랑', '초록']
)

# 체크박스
agree = st.checkbox('이용약관에 동의합니다')

if agree:
    st.write('동의해주셔서 감사합니다!')

# 여러 개 선택하기
hobbies = st.multiselect(
    '취미를 선택하세요 (여러 개 선택 가능)',
    ['독서', '영화감상', '운동', '여행', '음악감상']
)

if hobbies:
    st.write('선택한 취미:', hobbies)


# 날짜와 시간 입력
from datetime import datetime

today = st.date_input('날짜를 선택하세요')
current_time = st.time_input('시간을 선택하세요')

st.write(f'선택한 날짜: {today}')
st.write(f'선택한 시간: {current_time}')
