# app.py
import streamlit as st

st.title('와인 추천 서비스')

# 페이지 생성
main_page = st.Page('main.py', title='홈 페이지', icon='🏠')
login_page = st.Page('login.py', title='로그인', icon='🔐')   
chat = st.Page('chat.py', title='AI 챗봇', icon='💬')

# 네비게이션 생성
pages = st.navigation([main_page, login_page, chat])

# 네비게이션 실행
pages.run()