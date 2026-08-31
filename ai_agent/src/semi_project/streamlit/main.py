# main.py
import streamlit as st

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    st.image('../static/logo.svg')

# 문구 가운데 정렬 
st.markdown("<h3 style='text-align: center;'>당신의 특별한 순간을 위한 와인을 찾아드립니다.</h3>", unsafe_allow_html=True)
st.markdown("""
    <div style='display: flex; justify-content: center;'>
        <ul><li>와인을 처음 만나는 설렘도, 깊이 있는 여운도 여기에서 시작됩니다.</li></ul>
    </div>
""", unsafe_allow_html=True)