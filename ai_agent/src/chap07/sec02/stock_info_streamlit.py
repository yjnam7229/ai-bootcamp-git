# 해당 모듈 import
from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# 펑션 콜링(tools)
def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model="gpt-5-nano",  # 응답 생성에 사용할 모델 지정
        messages=messages,   # 대화 기록을 입력으로 전달
        tools=tools,         # 사용 가능한 도구 목록 전달
    )
    return response  # 생성된 응답 내용 반환

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},
    ]

# UI 제목
st.title("💬 상담 챗봇")   

# 기존 대화 출력
for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user": # assistant 혹은 user 메시지인 경우만(질문과 응답 메시지만 화면상에 출력)
        st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 받기
if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})  # 사용자 메시지를 대화 기록에 추가
    st.chat_message("user").write(user_input)  # 사용자 메시지를 브라우저에서도 출력
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools) # GTP에게 메시지 내역과 함께 tools의 정보를 전달(펑션 콜링 프로세스가 실행되도록)
    ai_message = ai_response.choices[0].message
    print(ai_message)  # gpt에서 반환되는 값을 파악하기 위해 임시로 추가

    # tool call 포함해서 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_message.content,
        "tool_calls": ai_message.tool_calls # 호출할 함수에 대한 정보를 담고 있음
    })


    tool_calls = ai_message.tool_calls  # AI 응답에 포함된 tool_calls를 가져옵니다.
    
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            try:
                arguments = json.loads(tool_call.function.arguments)  # (1) 문자열을 딕셔너리로 변환    

                if tool_name == "get_current_time":
                    timezone = arguments.get("timezone", "Asia/Seoul").strip()
                    func_result = get_current_time(timezone=timezone)

                elif tool_name == "get_yf_stock_info":
                    ticker = arguments.get("ticker", "").upper()
                    func_result = get_yf_stock_info(ticker=ticker)

                elif tool_name == "get_yf_stock_history":
                    ticker = arguments.get("ticker", "").upper()
                    period = arguments.get("period", "5d")
                    func_result = get_yf_stock_history(ticker=ticker, period=period)

                elif tool_name == "get_yf_stock_recommendations":
                    ticker = arguments.get("ticker", "").upper()
                    func_result = get_yf_stock_recommendations(ticker=ticker)

                else:
                    func_result = f"지원하지 않는 함수: {tool_name}"

            except Exception as e:
                func_result = f"에러 발생: {str(e)}"

            st.session_state.messages.append({
                "role": "tool",  # 펑션 콜링 방식인 경우(tool, tool_로 정의)
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": func_result,
            })

        # system 메시지 추가
        # st.session_state.messages.append({
        #     "role": "system",
        #     "content": "이제 주어진 결과를 바탕으로 답변할 차례다."
        # })

        # 다시 GPT 호출, 두번째 요청은 fuction call을 요청하지 못하도록 셋팅 tools=None
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

    output = ai_message.content or ""
    print("AI\t:", output)