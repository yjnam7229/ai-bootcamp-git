# 스트림릿에서 펑션 콜링 사용하기

from gpt_functions import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model="gpt-5-nano",  # 응답 생성에 사용할 모델 지정
        messages=messages,  # 대화 기록을 입력으로 전달
        tools=tools,  # 사용 가능한 도구 목록 전달
    )
    return response  # 생성된 응답 내용 반환


# 세션 상태 초기화, 스트림릿이 대화의 히스토리 관리(전체 화면을 업데이트)
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {'role': 'system', 'content': '너는 사용자를 도와주는 상담사야.'}    # 대화 내용 누적하고 보관
    ]

# UI 제목
st.title("💬 상담 챗봇")

# 기존 대화 출력
for msg in st.session_state.messages:   # 모든 대화의 내용을 화면상에 업데이트
    if msg['role'] == 'assistant' or msg['role'] == 'user':
        st.chat_message(msg['role']).write(msg['content'])      # role에 따라 아이콘 구별해서 출력


# 사용자 입력 받기
if user_input := st.chat_input("메시지를 입력하세요"):
    # 1. 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    st.chat_message("user").write(user_input)  # 화면상에 업데이트

    # 2. 1차 응답
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    ai_message = ai_response.choices[0].message

    # tool call 포함해서 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_message.content,
        "tool_calls": ai_message.tool_calls
    })

    tool_calls = ai_message.tool_calls

    # 3. tool 호출 처리
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)

            if tool_name == "get_current_time":
                tool_result = get_current_time(timezone=arguments['timezone'])

                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": tool_result,
                })

        # system 메시지 추가
        # st.session_state.messages.append({
        #     "role": "system",
        #     "content": "이제 주어진 결과를 바탕으로 답변할 차례다."
        # })

        # 다시 GPT 호출, tools=None : function 콜 수행 하지 못하게 
        ai_response = get_ai_response(st.session_state.messages, tools=None)
        ai_message = ai_response.choices[0].message

        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_message.content
        })

        st.chat_message("assistant").write(ai_message.content)

    else:
        # tool 없을 때
        st.chat_message("assistant").write(ai_message.content)