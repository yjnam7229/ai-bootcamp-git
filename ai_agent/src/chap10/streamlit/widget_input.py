# widget_input.py
import streamlit as st

st.title('위젯 입력창 연습')

name = st.text_input('이름', key='name')
st.time_input(name)
# st.write(name)