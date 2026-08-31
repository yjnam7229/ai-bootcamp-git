# agent_with_mcp.py
# MCP 서버의 도구를 에이전트에 불러오기
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.server.fastmcp import FastMCP
from dotenv  import load_dotenv
import asyncio

# .env 파일 호출
load_dotenv()

model = ChatOpenAI(model='gpt-5-nano')

# MCP 통신은 기본적으로 비동기(asynchronous) 방식으로 작동함
# MCP 클라이언트 생성 및 서버 연결
# async/await : 모든 동작 처리는 비동기로 호출, 대기하고 있는 상황에서 이벤트가 발생할 때마다 실행
async def main():
    """스트리밍 모드로 MCP 에이전트 실행 """

    # 1. MCP 클라이언트 생성: 서버 정보 등록
    client = MultiServerMCPClient({
        'file_manager': {
            'transport': 'stdio',
            'command': 'python',
            'args': ['file_server.py']  # python file_server.py 명령어
        },
        'time_server': {    # 도구 추가 
            'transport': 'stdio',
            'command': 'python',
            "args": ["-m", "mcp_server_time", "--local-timezone=Asia/Seoul"]  # python -m mcp_server_time 명령어가 실행됨(-m : module)
        }
    })

    # 2. 서버와 연결하고 도구 가져오기
    # 비동기적으로 구동 : 서버에게 요청 -> 대기(await) -> MCP 서버 응답 -> MCP 클라이언트는 전달 되어온 데이터 반환 받음 -> LLM 에게 전달
    tools = await client.get_tools()  # file_manager 키 값으로 모듈이 활성화

    # file_server.py 안에 정의되어 있는 도구들을 사용가능한 agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
        당신은 유능한 파일 관리자입니다.
        사용자가 파일 생성에 대해 요청하면, 파일을 생성하고,
        파일 요약을 요청하면, 파일을 읽고 요약을 작성합니다.
        그리고 반드시 파일 생성시에는 작성 일자를 포함해야 합니다.
         """
    )

    query = 'sample.txt 파일을 읽고, 내용을 요약해서 summary.md 저장해줘'
    print(f'사용자: {query}\n')

    # ReAct(추론) -> Observation(관찰)
    # 에이전트 실행, 수행하고 일정 시간이 지나면 다른 thread에게 넘겼다가 다시 제어권을 가져오는 방식(async 비동기)
    async for chunk in agent.astream(  # stream 출력도 비동기적으로 astream()
        {'messages': [{'role': 'user', 'content': query}]},
        stream_mode='values'  # 변화가 없는 응답이라도 모두 보내줘~
    ):
        if 'messages' not in chunk:
             continue
        
        latest_msg = chunk["messages"][-1]
            
        if latest_msg.__class__.__name__ == "AIMessage":
                if latest_msg.content:
                    print(f"Agent 생각:\n{latest_msg.content[:150]}...\n")
                
                if latest_msg.tool_calls:
                    for tc in latest_msg.tool_calls:
                        print(f"도구 호출: {tc['name']}")
                        print(f"   입력: {tc['args']}\n")
            
        elif latest_msg.__class__.__name__ == "ToolMessage":
                print(f"도구 결과:") # 관찰(Observation)한 다음 멈출 것인지 다시 도구를 호출할것인지 판단
                print(f"   {latest_msg.content[:200]}...\n")


# 파이썬 프로그램의 시작점임을 간접적으로 알려주는 방법
# asyncio 라이브러리를 사용
# asyncio는 async/await 구문을 사용하여 동시성 코드를 작성하는 라이브러리
if __name__ == '__main__':
    asyncio.run(main())
    




