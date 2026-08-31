from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# GPT와 멀티턴 대화하기
def get_ai_response(messages):
    response = client.chat.completions.create(
        model= 'gpt-5-nano',
        messages= messages
    )
  
    return response.choices[0].message.content    

messages = [
            {"role": "system", "content": "너는 사용자를 도와주는 상담사야."}
           ]

while True:
    user_input = input('사용자: ')

    if user_input == 'exit':
        break

    messages.append({"role": "user", "content": user_input})           
        
    ai_respose = get_ai_response(messages)  # 히스토리를 messages 안에 담아두고 대화의 맥락을 기억, http 규약 프로토콜 때문에 
    messages.append({"role": "assistant", "content": ai_respose})

    print('AI: ' + ai_respose) # AI 응답 출력

print('프로그램 종료.')    

