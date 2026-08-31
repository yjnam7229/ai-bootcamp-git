# app.py
import streamlit as st

st.title('Streamlit x LangChain')

# 페이지 생성
main_page = st.Page('main.py', title='메인 페이지', icon='😂')  # icon='0' 이모지 키(Win키 + .)
chat = st.Page('chat.py', title='챗 요소', icon='❤️')
widget_button = st.Page('widget_button.py', title='위젯 - 버튼', icon='😘')
widget_input = st.Page('widget_input.py', title='위젯 - 입력', icon='🙌')  # 사용자로 부터 데이터를 직접 전달 받음

# 네비게이션 생성
pages = st.navigation([main_page, chat, widget_button, widget_input])

# 네비게이션 실행
pages.run()