# chat.py
import streamlit as st

st.header('AI Chatbot')

# st.session_state를 활용한 대화 기록 유지 과정
# 1) 세션 상태 초기화
if 'messages' not in st.session_state:  # messages : messages 컬럼 항목을 추가 하면서 사용자의 질문과 응답을 관리, 업데이트 되어지면서
    st.session_state.messages = [] # messages 변수가 st.session_state에 아직 없을 때만 빈 리스트(st.session_state.messages = [])로 초기화

# 2) 사용자 입력 받기
prompt = st.chat_input('무엇을 도와드릴까요?')

# 3) 데이터 저장
if prompt: # 사용자가 입력한 메시지와 AI의 다변을 딕셔너리 형태로 구성하고, append 메서드를 사용하여 추가
    st.session_state.messages.append({'role': 'user', 'content': prompt})  # user 또는 human을 첫 번째 인자로 넘겨주면 사용자의 메시지를 가지고 있는 컨테이너를 반환
    st.session_state.messages.append({'role': 'assistant', 'content': '저는 AI입니다.'})  # ai 또는 assistant를 인자로 넘겨줄 경우, 모델의 답변을 모은 컨테이너가 반환됨

# 4) 대화 내용 표시
# for 반복문을 사용하여 st.session.messages 리스트에 저장된 모든 메시지를 순회하면서, chat_messages 메서드로 role을 구분하고, markdown 메서드로 content를 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message['role']):     
        st.markdown(message['content'])




