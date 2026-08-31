import streamlit as st
import random
import time

st.write("Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat.")

st.caption("Note that this demo app isn't actually connected to any LLMs. Those are expensive ;)")

# Initialize chat history
# messages 안에 대화의 히스토리 기억
# 사용자가 엔터를 입력하는 순간 화면 전체를 업데이트 하는 구조
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # with 의 구문으로 영역 확보, assistant, user role을 꺼내옴
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt}) # input 영역에 질문이 담겨 있으면
    # Display user message in chat message container
    with st.chat_message("user"):  # 사용자 아이콘
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"): # assistant 아이콘
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        # Simulate stream of response with milliseconds delay
        # 답변을 타이핑 하듯이 결과를 출력하는 효과
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    # 응답으로 온 메시지를 추가하면 streamlit은 종료 -> 엔터를 입력하면 다시 소스 코드의 처음으로 이동하면서 실행되면서 화면이 업데이트 됨
    st.session_state.messages.append({"role": "assistant", "content": full_response}) 
