
import streamlit as st

# 제목과 헤더 만들기
st.title('이것은 가장 큰 제목입니다')
st.header('이것은 큰 헤더입니다')
st.subheader('이것은 작은 헤더입니다')


# 일반 텍스트 표시하기
st.text('이것은 일반적인 텍스트입니다')
st.text('여러 줄로 텍스트를 작성할 수도 있습니다')

# 마크다운으로 꾸미기
st.markdown('**이것은 굵은 글씨입니다**')
st.markdown('*이것은 기울어진 글씨입니다*')
st.markdown('이것은 `코드`처럼 보이는 글씨입니다')


# 만능 출력 함수
st.write('안녕하세요!')
st.write(123)
st.write([1, 2, 3, 4, 5])
