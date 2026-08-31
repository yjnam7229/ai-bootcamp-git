from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
from collections import defaultdict

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# 펑션 콜링
def tool_list_to_tool_obj(tools):
    # 기본 값을 가진 딕셔너리 초기화
    # lambda 전달 받는 데이터가 없는 익명 함수
    tool_calls_dict = defaultdict(
        lambda : {"id": None, 
                  "function": {"arguments": "", "name": None}, 
                  "type": None}
    )

    # 도구(함수) 호출을 반복하여 처리, chunk 단위의 갯수 만큼 수행
    for tool_call in tools:
        # id가 None이 아닌 경우 설정
        if tool_call.id is not None:
            tool_calls_dict[tool_call.index]["id"] = tool_call.id

        # 함수 이름이 None이 아닌 경우 설정
        if tool_call.function.name is not None:
            tool_calls_dict[tool_call.index]["function"]["name"] = tool_call.function.name

        # 인수 추가
        tool_calls_dict[tool_call.index]["function"]["arguments"] += tool_call.function.arguments  # arguments에 한해서 누적

        # 타입이 None이 아닌 경우 설정
        if tool_call.type is not None:
            tool_calls_dict[tool_call.index]["type"] = tool_call.type

    # 딕셔너리를 리스트로 변환
    tool_calls_list = list(tool_calls_dict.values())

    return {"tool_calls": tool_calls_list}

def get_ai_response(messages, tools=None, stream=True):
    response = client.chat.completions.create(
        model="gpt-5-nano",   # 응답 생성에 사용할 모델 지정
        stream=stream,        # 스트리밍 출력을 위해 설정
        messages=messages,    # 대화 기록을 입력으로 전달
        tools=tools,          # 사용 가능한 도구 목록 전달
    )
    
    if stream: 
        for chunk in response:
            yield chunk  # 생성된 응답의 내용을 yield로 순차적으로 반환합니다.
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
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools)

    content = ''  # chunk 단위 데이터 누적
    tool_calls = None # # tool_calls 초기화, 펑션 콜링 호출
    tool_calls_chunk = []   # tool_calls_chunk 초기화
    
    with st.chat_message("assistant").empty():              # 스트림릿 챗 메시지 초기화, 화면에 출력(UI 영역 확보)
        for chunk in ai_response:
            content_chunk = chunk.choices[0].delta.content  # 청크 속 content 추출
            if content_chunk:                               # 만약 content_chunk가 있다면, 
                print(content_chunk, end="")	            # 터미널에 줄바꿈 없이 이어서 출력
                content += content_chunk                    # content에 덧붙이기
                st.markdown(content)                        # 스트림릿 챗 메시지에 마크다운으로 출력
        
            # print(chunk) # 임시로 청크 출력
            # 펑션 콜링으로 호출이 온 경우
            if chunk.choices[0].delta.tool_calls:	                   # tool_calls가 있는 경우
                tool_calls_chunk += chunk.choices[0].delta.tool_calls  # tool_calls_chunk에 추가
    
    tool_obj = tool_list_to_tool_obj(tool_calls_chunk)
    tool_calls = tool_obj["tool_calls"]   

    # 디버깅 용 코드
    if len(tool_calls) > 0: # 만약 tool_calls가 존재하면, st.write로 tool_call 내용 출력
        print(tool_calls)
        # tool_calls에서 function 정보만 모아서 출력
        tool_call_msg = [tool_call["function"] for tool_call in tool_calls]
        st.write(tool_call_msg)
    
    print('\n===========')
    print(content)

    # 데이터가 합쳐진 상태
    if tool_calls:
        # GPT가 생성한 tool_calls를 assistant 메시지로 먼저 저장
        st.session_state.messages.append({
            "role": "assistant",
            "content": content if content else None,
            "tool_calls": tool_calls,
        })

        for tool_call in tool_calls:
            # 딕셔너리 형태에서 받기
            #tool_name = tool_call.function.name
            #tool_call_id = tool_call.id
            tool_name = tool_call["function"]["name"]   # 실행해야 한다고 판단한 함수명 받기
            tool_call_id = tool_call["id"]              # 함수 아이디 받기

            try:
                #arguments = json.loads(tool_call.function.arguments)
                arguments = json.loads(tool_call["function"]["arguments"]) # 문자열을 딕셔너리로 변환 

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
        #ai_message = ai_response.choices[0].message # 주석 처리
        
        content = ""
        with st.chat_message("assistant").empty():
            for chunk in ai_response:
                content_chunk = chunk.choices[0].delta.content
                if content_chunk:
                    print(content_chunk, end='')
                    content += content_chunk
                    st.markdown(content) # 스트림릿 챗메시지에 markdown으로 출력

        st.session_state.messages.append({
            "role": "assistant",
            "content": content   # ai_message.content
        }) # AI 응답을 대화 기록에 추가합니다.

        # st.chat_message("assistant").write(ai_message.content)

    else:
        # tool 없을 때
        st.session_state.messages.append({
            "role": "assistant",
            "content": content if content else None
        }) # AI 응답을 대화 기록에 추가합니다.

        # st.chat_message("assistant").write(content)

    # output = ai_message.content or ""
    print("AI\t:", content)