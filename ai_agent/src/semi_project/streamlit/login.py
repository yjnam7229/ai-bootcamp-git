# login.py
import streamlit as st

st.header('🔐 로그인')

# 입력 폼 (Id, Password, 로그인 버튼)
id = st.text_input('Id', key='id')
pwd = st.text_input('Password', key='password', type='password')

if st.button("로그인"):
    st.write(f"로그인 시도 ID: {id}")
 