# llama_simple_chatbot.py
# 라마 기반으로 간단한 챗봇 만들기

# deepseek_simple_chatbot.py
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatOllama(model='llama3.2:3b')  

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

