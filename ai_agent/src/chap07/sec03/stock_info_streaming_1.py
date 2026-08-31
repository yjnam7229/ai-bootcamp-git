from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

def get_ai_response(messages, tools=None, stream=True):
    response = client.chat.completions.create(
        model="gpt-5-nano",   # 응답 생성에 사용할 모델 지정
        stream=stream,        # 스트리밍 출력을 위해 설정
        messages=messages,    # 대화 기록을 입력으로 전달
        tools=tools,          # 사용 가능한 도구 목록 전달
    )

    # yield : 다음 데이터가 존재하지 않을 때까지 대기하고 있음 -> 다음 chunk 데이터가 올 때까지 대기 -> 최종 응답 대기 -> 리턴
    if stream: 
        for chunk in response:
            yield chunk  # 생성된 응답의 내용을 yield 키워드로 순차적으로 반환합니다(제너레이터 함수화 되어짐), chunk 단위의 쪼개긴 데이터가 전송되어 옴
    else:
        return response  # 생성된 응답의 내용을 반환합니다.

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},
    ]

# UI 제목
st.title("💬 상담 챗봇")   

# 기존 대화 출력
for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user": # assistant 혹은 user 메시지인 경우만
        st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 받기
if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})  # 사용자 메시지를 대화 기록에 추가
    st.chat_message("user").write(user_input)  # 사용자 메시지를 브라우저에서도 출력
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools) # GPT에게 질문을 전달, chunk 단위의 데이터가 전송되어 옴
    
    content = ''
    tool_calls = None

    # chunk 단위의 데이터가 화면상에 타이핑 하듯이 출력(실시간 업데이트)
    with st.chat_message("assistant").empty():              # 스트림릿 챗 메시지 초기화, 화면에 출력할 영역 확보
        for chunk in ai_response:
            content_chunk = chunk.choices[0].delta.content  # 청크 속 content 추출
            if content_chunk:                               # 만약 content_chunk가 있다면, 
                print(content_chunk, end="")	            # 쪼개진 chunk단위 데이터를 터미널에 줄바꿈 없이 이어서 출력
                content += content_chunk                    # content에 덧붙이기
                st.markdown(content)                        # 스트림릿 챗 메시지에 마크다운으로 출력
    
    print('\n============================')
    print(content)
    
    #ai_message = ai_response.choices[0].message
    #print(ai_message)  # gpt에서 반환되는 값을 파악하기 위해 임시로 추가

    # tool call 포함해서 저장
    # st.session_state.messages.append({
    #     "role": "assistant",
    #     "content": ai_message.content,
    #     "tool_calls": ai_message.tool_calls  # ai_response가 한꺼번에 오는 경우, chunk단위로 전송에는 에러 발생  
    # })

    # tool_calls = ai_message.tool_calls  # AI 응답에 포함된 tool_calls를 가져옵니다.
    
    # 쪼개진 chunk 단위의 데이터를 합침
    # tool_calls : None -> 
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            try:
                arguments = json.loads(tool_call.function.arguments)

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
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": func_result,
            })

        # 다시 GPT 호출
        ai_response = get_ai_response(st.session_state.messages, tools=None)
        ai_message = ai_response.choices[0].message

        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_message.content
        })

        st.chat_message("assistant").write(ai_message.content)

    #else:
        # tool 없을 때
        # st.chat_message("assistant").write(ai_message.content)

    # output = ai_message.content or ""
    # print("AI\t:", output)
    # print("AI\t:", content)
