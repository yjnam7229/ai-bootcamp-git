# deepseek_simple_chatbot.py
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatOllama(model='deepseek-r1:14b')  # 만약 컴퓨터 성능이 부족하다면 7b, 8b 모델 선택

messages = [
    SystemMessage('너는 사용자를 도와주는 상담사야')
]

while True:
    user_input = input('사용자: ')

    if user_input == 'exit':
        break

    messages.append(
        HumanMessage(user_input)
        )

    response = llm.stream(messages)

    ai_message = None

    for chunk in response:
        print(chunk.content, end='')

        if ai_message is None:
            ai_message = chunk
        else:
            ai_message += chunk

    print('')                

    messages.append(AIMessage(ai_message.content))

