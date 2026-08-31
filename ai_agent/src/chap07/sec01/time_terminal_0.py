from gpt_functions_0 import get_current_time, tools  # gpt_functions_0 모듈안에 정의 되어 있는 함수 import
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# GPT와 멀티턴 대화하기
# 펑션 콜링 적용하기
def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model= 'gpt-5-nano',
        messages= messages,
        tools=tools  # 사용 가능한 도구 목록 전달
    )
  
    return response  # 추가적인 모든 답변을 가져옴
    # return response.choices[0].message.content    

messages = [
            {"role": "system", "content": "너는 사용자를 도와주는 상담사야."}
           ]

while True:
    user_input = input('사용자: ')

    if user_input == 'exit':
        break

    # AI 에게 질문하기    
    messages.append({"role": "user", "content": user_input})      # user_input : 질문의 내용

    # 펑션 콜링 적용하기
    # AI 응답 받기(모든 응답)
    ai_response = get_ai_response(messages, tools=tools)  # 히스토리를 messages 안에 담아두고 대화의 맥락을 기억, http 규약 프로토콜 때문에 맥락을 기억 못함
    ai_message = ai_response.choices[0].message  # message.content 대신 message 까지 꺼내옴, 펑션 콜링 함수 까지 적용(답변이 아니라 message에 담긴 객체 값을 꺼내옴)

    print(ai_message) # GPT에서 반환되는 값을 파악하기 위해 임시로 추가

    # tool_calls=에 값이 담겨져 있으므로
    messages.append({     # AI 응답을 대화 기록에 추가하기
        'role': 'assistant',
        'content': ai_message.content,
        'tool_calls': ai_message.tool_calls
    })
    # messages.append({"role": "assistant", "content": ai_response})

    tool_calls = ai_message.tool_calls      # AI 응답에 포함된 tool_calls를 가져옴

    if tool_calls:      # tool_calls가 있는 경우
        tool_name = tool_calls[0].function.name
        tool_call_id = tool_calls[0].id

        if tool_name == 'get_current_time':
            tool_result = get_current_time()

            messages.append({
                'role': 'tool',  # role을 "tool"으로 설정
                'tool_call_id': tool_call_id,
                'name': tool_name,
                'content': tool_result
            })

            ai_response = get_ai_response(messages, tools=None) # function 콜에 의한 결과를 전달, tools=None : function 콜을 호출하지 않도록 함
            ai_message = ai_response.choices[0].message

            messages.append({
                'role': 'assistant',
                'content': ai_message.content
            })

            print('AI: ' + ai_message.content) # AI 응답 출력

    else:
        print('AI: ' + ai_message.content) # AI 응답 출력

print('프로그램 종료.')    

