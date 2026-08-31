import streamlit as st
from openai import OpenAI

st.title("Context-aware Chatbot Demo")

# 1. API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. 세션 상태에 메시지 히스토리 관리
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇이든 물어보세요. 대화 맥락을 기억합니다."}
    ]

# 3. 화면에 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Assistant 응답 생성 (이전 대화 전체를 모델에 전달)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-5-nano",
            # 전체 히스토리(st.session_state.messages)를 전달하여 맥락 유지
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)

    # Assistant 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": response})