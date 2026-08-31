# chat.py
import streamlit as st

st.header('💬 AI Chatbot')

# st.session_state를 활용한 대화 기록 유지 과정
# 1) 세션 상태 초기화
if 'messages' not in st.session_state:   
    st.session_state.messages = []  

# 2) 사용자 입력 받기
prompt = st.chat_input('무엇을 도와드릴까요?')

# 3) 데이터 저장
if prompt:  
    st.session_state.messages.append({'role': 'user', 'content': prompt})  
    st.session_state.messages.append({'role': 'assistant', 'content': '저는 AI입니다.'})  

# 4) 대화 내용 표시
# for 반복문을 사용하여 st.session.messages 리스트에 저장된 모든 메시지를 순회하면서, chat_messages 메서드로 role을 구분하고, markdown 메서드로 content를 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message['role']):     
        st.markdown(message['content'])




